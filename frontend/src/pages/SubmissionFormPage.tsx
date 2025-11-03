/**
 * Submission Form page component using Blueprint.js.
 */

import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  H1,
  Callout,
  Intent,
  Button,
  FormGroup,
  InputGroup,
  HTMLSelect,
  Card,
  TextArea,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useCreateSubmission,
  useUpdateSubmission,
  useSubmission,
} from "../hooks/queries/commons";
import { pageHeader } from "../styles/common";
import { spacing } from "../styles/theme";
import type {
  CommonsSubmissionCreate,
  CommonsSubmissionUpdate,
  EntityType,
} from "../types/commons";

const ENTITY_TYPE_OPTIONS = [
  { value: "item", label: "Item" },
  { value: "blueprint", label: "Blueprint (Recipe)" },
  { value: "location", label: "Location" },
  { value: "ingredient", label: "Ingredient" },
  { value: "taxonomy", label: "Taxonomy" },
];

export default function SubmissionFormPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;

  const [entityType, setEntityType] = useState<EntityType>("item");
  const [entityPayload, setEntityPayload] = useState("");
  const [sourceReference, setSourceReference] = useState("");
  const [payloadError, setPayloadError] = useState<string | null>(null);

  const { data: submissionData } = useSubmission(id);
  const createSubmission = useCreateSubmission();
  const updateSubmission = useUpdateSubmission();

  // Load existing submission data when editing
  useEffect(() => {
    if (isEdit && submissionData) {
      setEntityType(submissionData.entity_type);
      setEntityPayload(JSON.stringify(submissionData.entity_payload, null, 2));
      setSourceReference(submissionData.source_reference || "");
    }
  }, [isEdit, submissionData]);

  const handlePayloadChange = (value: string) => {
    setEntityPayload(value);
    setPayloadError(null);
    if (value.trim()) {
      try {
        JSON.parse(value);
      } catch (e) {
        setPayloadError("Invalid JSON format");
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!entityType || !entityPayload) {
      return;
    }

    let parsedPayload: Record<string, unknown>;
    try {
      parsedPayload = JSON.parse(entityPayload);
    } catch (e) {
      setPayloadError("Invalid JSON format");
      return;
    }

    try {
      if (isEdit && id) {
        const updateData: CommonsSubmissionUpdate = {
          entity_payload: parsedPayload,
          source_reference: sourceReference || null,
        };
        await updateSubmission.mutateAsync({
          submissionId: id,
          data: updateData,
        });
      } else {
        const createData: CommonsSubmissionCreate = {
          entity_type: entityType,
          entity_payload: parsedPayload,
          source_reference: sourceReference || null,
        };
        await createSubmission.mutateAsync(createData);
      }
      navigate("/commons/my-submissions");
    } catch (error) {
      console.error("Failed to save submission:", error);
    }
  };

  const isSubmitting = createSubmission.isPending || updateSubmission.isPending;

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>
        {isEdit ? "Update Submission" : "Submit to Commons"}
      </H1>

      <Card style={{ maxWidth: "900px", marginTop: spacing.lg }}>
        <Callout intent={Intent.PRIMARY} style={{ marginBottom: spacing.lg }}>
          <h4>Submission Guidelines</h4>
          <ul style={{ marginTop: spacing.sm, paddingLeft: spacing.lg }}>
            <li>Ensure all data is accurate and verified</li>
            <li>Include all relevant fields in the entity payload</li>
            <li>Provide source references when available</li>
            <li>Check existing commons to avoid duplicates</li>
            <li>Follow the standard JSON format for entity payload</li>
          </ul>
        </Callout>

        <form onSubmit={handleSubmit}>
          <FormGroup
            label="Entity Type"
            labelInfo="(required)"
            disabled={isEdit}
          >
            <HTMLSelect
              value={entityType}
              onChange={(e) => setEntityType(e.target.value as EntityType)}
              disabled={isEdit}
              options={ENTITY_TYPE_OPTIONS}
            />
          </FormGroup>

          <FormGroup
            label="Entity Payload"
            labelInfo="(required)"
            helperText="JSON object containing the entity data"
          >
            <TextArea
              value={entityPayload}
              onChange={(e) => handlePayloadChange(e.target.value)}
              placeholder='{"name": "Item Name", "description": "...", "category": "..."}'
              rows={12}
              style={{ fontFamily: "monospace" }}
              required
            />
            {payloadError && (
              <Callout intent={Intent.DANGER} style={{ marginTop: spacing.sm }}>
                {payloadError}
              </Callout>
            )}
          </FormGroup>

          <FormGroup
            label="Source Reference"
            helperText="URL or notes about where this data came from (optional)"
          >
            <InputGroup
              value={sourceReference}
              onChange={(e) => setSourceReference(e.target.value)}
              placeholder="https://example.com/source or notes"
              type="url"
            />
          </FormGroup>

          <div
            style={{
              display: "flex",
              gap: spacing.md,
              marginTop: spacing.lg,
            }}
          >
            <Button
              type="submit"
              intent={Intent.PRIMARY}
              loading={isSubmitting}
              text={isEdit ? "Update Submission" : "Submit"}
            />
            <Button
              text="Cancel"
              onClick={() => navigate("/commons/my-submissions")}
              disabled={isSubmitting}
            />
          </div>

          {(createSubmission.isError || updateSubmission.isError) && (
            <Callout intent={Intent.DANGER} style={{ marginTop: spacing.md }}>
              Failed to save submission:{" "}
              {createSubmission.error instanceof Error
                ? createSubmission.error.message
                : updateSubmission.error instanceof Error
                ? updateSubmission.error.message
                : "Unknown error"}
            </Callout>
          )}
        </form>
      </Card>
    </DashboardLayout>
  );
}
