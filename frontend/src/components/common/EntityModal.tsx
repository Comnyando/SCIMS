/**
 * Reusable Entity Modal Component Framework
 *
 * This provides a base modal structure that can be extended for different entity types.
 * It handles common patterns like loading states, error handling, and form submission.
 */

import React, { ReactNode } from "react";
import {
  Dialog,
  DialogBody,
  DialogFooter,
  Button,
  Intent,
  Spinner,
  Callout,
} from "@blueprintjs/core";
import { spacing } from "../../styles/theme";

export interface EntityModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Title of the modal */
  title: string;
  /** Form content to render inside the modal */
  children: ReactNode;
  /** Whether the form is currently submitting */
  isSubmitting?: boolean;
  /** Error message to display */
  error?: string | null;
  /** Callback when form is submitted */
  onSubmit: () => void;
  /** Text for the submit button */
  submitText?: string;
  /** Intent for the submit button */
  submitIntent?: Intent;
  /** Whether the submit button should be disabled */
  isSubmitDisabled?: boolean;
  /** Optional footer actions */
  footerActions?: ReactNode;
}

/**
 * Base Entity Modal Component
 *
 * Provides a consistent structure for entity creation/editing modals.
 * Extend this for specific entity types by providing custom form content.
 */
export function EntityModal({
  isOpen,
  onClose,
  title,
  children,
  isSubmitting = false,
  error,
  onSubmit,
  submitText = "Save",
  submitIntent = Intent.PRIMARY,
  isSubmitDisabled = false,
  footerActions,
}: EntityModalProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isSubmitting && !isSubmitDisabled) {
      onSubmit();
    }
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      style={{ width: "90%", maxWidth: "600px" }}
      canOutsideClickClose={!isSubmitting}
      canEscapeKeyClose={!isSubmitting}
    >
      <form onSubmit={handleSubmit}>
        <DialogBody>
          {error && (
            <Callout
              intent={Intent.DANGER}
              style={{ marginBottom: spacing.md }}
            >
              {error}
            </Callout>
          )}
          {children}
        </DialogBody>
        <DialogFooter
          actions={
            <>
              {footerActions}
              <Button text="Cancel" onClick={onClose} disabled={isSubmitting} />
              <Button
                text={submitText}
                intent={submitIntent}
                onClick={onSubmit}
                disabled={isSubmitting || isSubmitDisabled}
                type="submit"
                icon={isSubmitting ? <Spinner size={16} /> : undefined}
              />
            </>
          }
        />
      </form>
    </Dialog>
  );
}
