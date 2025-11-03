/**
 * Commons service methods.
 */

import { ApiClient } from "./client";
import type {
  CommonsSubmissionCreate,
  CommonsSubmissionUpdate,
  CommonsSubmissionResponse,
  CommonsSubmissionsListResponse,
  CommonsModerationActionCreate,
  CommonsEntityResponse,
  CommonsEntitiesListResponse,
  TagResponse,
  TagsListResponse,
} from "../types/commons";

export class CommonsService extends ApiClient {
  /**
   * Submit a new entity to the commons.
   */
  async submitSubmission(
    data: CommonsSubmissionCreate
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.post<CommonsSubmissionResponse>(
      "/commons/submit",
      data
    );
    return response.data;
  }

  /**
   * Get current user's submissions.
   */
  async getMySubmissions(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    entity_type?: string;
  }): Promise<CommonsSubmissionsListResponse> {
    const response = await this.client.get<CommonsSubmissionsListResponse>(
      "/commons/my-submissions",
      { params }
    );
    return response.data;
  }

  /**
   * Update a submission.
   */
  async updateSubmission(
    submissionId: string,
    data: CommonsSubmissionUpdate
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.patch<CommonsSubmissionResponse>(
      `/commons/submissions/${submissionId}`,
      data
    );
    return response.data;
  }

  /**
   * List submissions for moderation (admin only).
   */
  async listSubmissions(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    entity_type?: string;
  }): Promise<CommonsSubmissionsListResponse> {
    const response = await this.client.get<CommonsSubmissionsListResponse>(
      "/admin/commons/submissions",
      { params }
    );
    return response.data;
  }

  /**
   * Get a specific submission (admin only).
   */
  async getSubmission(
    submissionId: string
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.get<CommonsSubmissionResponse>(
      `/admin/commons/submissions/${submissionId}`
    );
    return response.data;
  }

  /**
   * Approve a submission (admin only).
   */
  async approveSubmission(
    submissionId: string,
    data: CommonsModerationActionCreate
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.post<CommonsSubmissionResponse>(
      `/admin/commons/submissions/${submissionId}/approve`,
      data
    );
    return response.data;
  }

  /**
   * Reject a submission (admin only).
   */
  async rejectSubmission(
    submissionId: string,
    data: CommonsModerationActionCreate
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.post<CommonsSubmissionResponse>(
      `/admin/commons/submissions/${submissionId}/reject`,
      data
    );
    return response.data;
  }

  /**
   * Request changes on a submission (admin only).
   */
  async requestChangesSubmission(
    submissionId: string,
    data: CommonsModerationActionCreate
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.post<CommonsSubmissionResponse>(
      `/admin/commons/submissions/${submissionId}/request-changes`,
      data
    );
    return response.data;
  }

  /**
   * Merge a submission into an existing entity (admin only).
   */
  async mergeSubmission(
    submissionId: string,
    data: CommonsModerationActionCreate
  ): Promise<CommonsSubmissionResponse> {
    const response = await this.client.post<CommonsSubmissionResponse>(
      `/admin/commons/submissions/${submissionId}/merge`,
      data
    );
    return response.data;
  }

  /**
   * List public items.
   */
  async listPublicItems(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    tag?: string;
  }): Promise<CommonsEntitiesListResponse> {
    const response = await this.client.get<CommonsEntitiesListResponse>(
      "/public/items",
      { params }
    );
    return response.data;
  }

  /**
   * List public recipes.
   */
  async listPublicRecipes(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    tag?: string;
  }): Promise<CommonsEntitiesListResponse> {
    const response = await this.client.get<CommonsEntitiesListResponse>(
      "/public/recipes",
      { params }
    );
    return response.data;
  }

  /**
   * List public locations.
   */
  async listPublicLocations(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    tag?: string;
  }): Promise<CommonsEntitiesListResponse> {
    const response = await this.client.get<CommonsEntitiesListResponse>(
      "/public/locations",
      { params }
    );
    return response.data;
  }

  /**
   * Get a specific public entity.
   */
  async getPublicEntity(
    entityType: "item" | "recipe" | "location",
    entityId: string
  ): Promise<CommonsEntityResponse> {
    const endpoint = `/public/${
      entityType === "recipe" ? "recipes" : `${entityType}s`
    }/${entityId}`;
    const response = await this.client.get<CommonsEntityResponse>(endpoint);
    return response.data;
  }

  /**
   * Search public entities.
   */
  async searchPublicEntities(params?: {
    q: string;
    entity_type?: string;
    skip?: number;
    limit?: number;
  }): Promise<CommonsEntitiesListResponse> {
    const response = await this.client.get<CommonsEntitiesListResponse>(
      "/public/search",
      { params }
    );
    return response.data;
  }

  /**
   * List all tags.
   */
  async listTags(): Promise<TagsListResponse> {
    const response = await this.client.get<TagsListResponse>("/public/tags");
    return response.data;
  }

  /**
   * List all tags (admin only).
   */
  async listTagsAdmin(params?: {
    skip?: number;
    limit?: number;
  }): Promise<TagsListResponse> {
    const response = await this.client.get<TagsListResponse>(
      "/admin/commons/tags",
      { params }
    );
    return response.data;
  }

  /**
   * Create a tag (admin only).
   */
  async createTag(data: {
    name: string;
    description?: string | null;
  }): Promise<TagResponse> {
    const response = await this.client.post<TagResponse>(
      "/admin/commons/tags",
      data
    );
    return response.data;
  }

  /**
   * Update a tag (admin only).
   */
  async updateTag(
    tagId: string,
    data: { name: string; description?: string | null }
  ): Promise<TagResponse> {
    const response = await this.client.patch<TagResponse>(
      `/admin/commons/tags/${tagId}`,
      data
    );
    return response.data;
  }

  /**
   * Delete a tag (admin only).
   */
  async deleteTag(tagId: string): Promise<void> {
    await this.client.delete(`/admin/commons/tags/${tagId}`);
  }
}
