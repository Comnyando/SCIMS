/**
 * Utility functions for handling API errors.
 * FastAPI returns validation errors as arrays of error objects.
 */

interface FastAPIValidationError {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}

interface FastAPIErrorResponse {
  detail: string | FastAPIValidationError[];
}

/**
 * Extract a user-friendly error message from an API error response.
 */
export function extractErrorMessage(error: unknown): string | null {
  if (!error || typeof error !== "object") {
    return "An unexpected error occurred. Please try again.";
  }

  // Check if it's an Axios error with a response
  if ("response" in error) {
    const axiosError = error as {
      response?: {
        data?: FastAPIErrorResponse;
        status?: number;
      };
    };
    const response = axiosError.response;

    if (!response) {
      return "Network error. Please check your connection and try again.";
    }

    const data = response.data;

    // Handle case where data might not exist
    if (!data) {
      if (response.status === 401) {
        return "Authentication failed. Please check your credentials.";
      }
      if (response.status === 422) {
        return "Invalid request. Please check your input and try again.";
      }
      return "Request failed. Please try again.";
    }

    // Handle FastAPI error format
    if (data.detail) {
      // If detail is a string, use it directly
      if (typeof data.detail === "string") {
        return data.detail;
      }

      // If detail is an array (validation errors), format them
      if (Array.isArray(data.detail)) {
        if (data.detail.length === 0) {
          return "Validation failed. Please check your input.";
        }
        const messages = data.detail.map((err: FastAPIValidationError) => {
          const field = err.loc[err.loc.length - 1];
          // Make field names more user-friendly
          const fieldName = String(field).replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
          return `${fieldName}: ${err.msg}`;
        });
        return messages.join(". ");
      }
    }
  }

  // Fallback for other error types
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred. Please try again.";
}

