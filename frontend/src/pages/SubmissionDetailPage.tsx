/**
 * Submission Detail page component using Blueprint.js.
 */

import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  H1,
  Callout,
  Intent,
  Spinner,
  Button,
  Card,
  Tag,
  TextArea,
  Dialog,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useSubmission,
  useApproveSubmission,
  useRejectSubmission,
  useRequestChangesSubmission,
  useMergeSubmission,
} from "../hooks/queries/commons";
import { pageHeader, sectionSpacing } from "../styles/common";
import { spacing } from "../styles/theme";
import type { CommonsModerationActionCreate } from "../types/commons";

const STATUS_COLORS: Record<string, Intent> = {
  pending: Intent.WARNING,
  approved: Intent.SUCCESS,
  rejected: Intent.DANGER,
  needs_changes: Intent.PRIMARY,
  merged: Intent.NONE,
};

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function SubmissionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [actionDialog, setActionDialog] = useState<{
    type: "approve" | "reject" | "request_changes" | "merge";
    open: boolean;
  }>({ type: "approve", open: false });
  const [notes, setNotes] = useState("");
  const [mergeTargetId, setMergeTargetId] = useState("");

  const { data: submission, isLoading, error } = useSubmission(id);
  const approveSubmission = useApproveSubmission();
  const rejectSubmission = useRejectSubmission();
  const requestChangesSubmission = useRequestChangesSubmission();
  const mergeSubmission = useMergeSubmission();

  const handleAction = async () => {
    if (!submission) return;

    const actionData: CommonsModerationActionCreate = {
      action: actionDialog.type,
      notes: notes || undefined,
    };

    if (actionDialog.type === "merge") {
      if (!mergeTargetId) {
        alert("Please enter a target entity ID for merge");
        return;
      }
      actionData.action_payload = { target_entity_id: mergeTargetId };
    }

    try {
      if (actionDialog.type === "approve") {
        await approveSubmission.mutateAsync({
          submissionId: submission.id,
          data: actionData,
        });
      } else if (actionDialog.type === "reject") {
        await rejectSubmission.mutateAsync({
          submissionId: submission.id,
          data: actionData,
        });
      } else if (actionDialog.type === "request_changes") {
        await requestChangesSubmission.mutateAsync({
          submissionId: submission.id,
          data: actionData,
        });
      } else if (actionDialog.type === "merge") {
        await mergeSubmission.mutateAsync({
          submissionId: submission.id,
          data: actionData,
        });
      }
      setActionDialog({ type: "approve", open: false });
      setNotes("");
      setMergeTargetId("");
      navigate("/admin/commons/submissions");
    } catch (error) {
      console.error("Action failed:", error);
    }
  };

  const openActionDialog = (
    type: "approve" | "reject" | "request_changes" | "merge"
  ) => {
    setActionDialog({ type, open: true });
  };

  const isActionPending =
    approveSubmission.isPending ||
    rejectSubmission.isPending ||
    requestChangesSubmission.isPending ||
    mergeSubmission.isPending;

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !submission) {
    return (
      <DashboardLayout>
        <Callout intent={Intent.DANGER}>
          {error instanceof Error
            ? `Error loading submission: ${error.message}`
            : "Submission not found"}
        </Callout>
      </DashboardLayout>
    );
  }

  const canModerate =
    submission.status === "pending" || submission.status === "needs_changes";

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Submission Details</H1>

      <div
        style={{ display: "flex", gap: spacing.md, marginBottom: spacing.lg }}
      >
        <Button
          icon="arrow-left"
          text="Back to Queue"
          onClick={() => navigate("/admin/commons/submissions")}
        />
      </div>

      <Card style={sectionSpacing}>
        <div style={{ marginBottom: spacing.md }}>
          <strong>Status: </strong>
          <Tag intent={STATUS_COLORS[submission.status]}>
            {submission.status.replace("_", " ").toUpperCase()}
          </Tag>
        </div>

        <div style={{ marginBottom: spacing.md }}>
          <strong>Entity Type: </strong>
          <Tag>{submission.entity_type}</Tag>
        </div>

        <div style={{ marginBottom: spacing.md }}>
          <strong>Submitted: </strong>
          {formatDate(submission.created_at)}
        </div>

        <div style={{ marginBottom: spacing.md }}>
          <strong>Last Updated: </strong>
          {formatDate(submission.updated_at)}
        </div>

        {submission.review_notes && (
          <div style={{ marginBottom: spacing.md }}>
            <strong>Review Notes: </strong>
            <Callout intent={Intent.NONE} style={{ marginTop: spacing.sm }}>
              {submission.review_notes}
            </Callout>
          </div>
        )}

        {submission.source_reference && (
          <div style={{ marginBottom: spacing.md }}>
            <strong>Source Reference: </strong>
            <a
              href={submission.source_reference}
              target="_blank"
              rel="noopener noreferrer"
            >
              {submission.source_reference}
            </a>
          </div>
        )}

        <div style={{ marginTop: spacing.lg }}>
          <strong>Entity Payload:</strong>
          <pre
            style={{
              marginTop: spacing.sm,
              padding: spacing.md,
              backgroundColor: "var(--scims-code-background)",
              color: "var(--scims-text-primary)",
              borderRadius: "4px",
              overflow: "auto",
              maxHeight: "400px",
            }}
          >
            {JSON.stringify(submission.entity_payload, null, 2)}
          </pre>
        </div>
      </Card>

      {canModerate && (
        <Card style={sectionSpacing}>
          <h3>Moderation Actions</h3>
          <div
            style={{
              display: "flex",
              gap: spacing.md,
              flexWrap: "wrap",
              marginTop: spacing.md,
            }}
          >
            <Button
              intent={Intent.SUCCESS}
              text="Approve"
              icon="tick"
              onClick={() => openActionDialog("approve")}
              disabled={isActionPending}
            />
            <Button
              intent={Intent.DANGER}
              text="Reject"
              icon="cross"
              onClick={() => openActionDialog("reject")}
              disabled={isActionPending}
            />
            <Button
              intent={Intent.PRIMARY}
              text="Request Changes"
              icon="edit"
              onClick={() => openActionDialog("request_changes")}
              disabled={isActionPending}
            />
            <Button
              intent={Intent.WARNING}
              text="Merge"
              icon="git-merge"
              onClick={() => openActionDialog("merge")}
              disabled={isActionPending}
            />
          </div>
        </Card>
      )}

      <Dialog
        isOpen={actionDialog.open}
        onClose={() => setActionDialog({ type: "approve", open: false })}
        title={`${actionDialog.type
          .replace("_", " ")
          .toUpperCase()} Submission`}
        style={{ width: "500px" }}
      >
        <div style={{ padding: spacing.md }}>
          <div style={{ marginBottom: spacing.md }}>
            <label>
              <strong>Notes (optional):</strong>
            </label>
            <TextArea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              fill
              style={{ marginTop: spacing.sm }}
            />
          </div>

          {actionDialog.type === "merge" && (
            <div style={{ marginBottom: spacing.md }}>
              <label>
                <strong>Target Entity ID:</strong>
              </label>
              <input
                type="text"
                value={mergeTargetId}
                onChange={(e) => setMergeTargetId(e.target.value)}
                style={{
                  width: "100%",
                  padding: spacing.sm,
                  marginTop: spacing.sm,
                  borderRadius: "4px",
                  border: "1px solid var(--scims-border-light)",
                }}
                placeholder="Enter UUID of entity to merge into"
              />
            </div>
          )}

          <div
            style={{
              display: "flex",
              gap: spacing.md,
              justifyContent: "flex-end",
              marginTop: spacing.lg,
            }}
          >
            <Button
              text="Cancel"
              onClick={() => setActionDialog({ type: "approve", open: false })}
              disabled={isActionPending}
            />
            <Button
              intent={
                actionDialog.type === "approve"
                  ? Intent.SUCCESS
                  : actionDialog.type === "reject"
                  ? Intent.DANGER
                  : Intent.PRIMARY
              }
              text="Confirm"
              onClick={handleAction}
              loading={isActionPending}
            />
          </div>
        </div>
      </Dialog>
    </DashboardLayout>
  );
}
