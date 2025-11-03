/**
 * Tag Manager page component using Blueprint.js.
 */

import { useState } from "react";
import {
  H1,
  Callout,
  Intent,
  Spinner,
  Button,
  FormGroup,
  InputGroup,
  TextArea,
  Dialog,
  Tag as BlueprintTag,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useTagsAdmin,
  useCreateTag,
  useUpdateTag,
  useDeleteTag,
} from "../hooks/queries/admin_tags";
import DataTable from "../components/common/DataTable";
import { pageHeader } from "../styles/common";
import { spacing } from "../styles/theme";
import type { TagResponse } from "../types/commons";

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

export default function TagManagerPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<TagResponse | null>(null);
  const [tagName, setTagName] = useState("");
  const [tagDescription, setTagDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: tagsData, isLoading } = useTagsAdmin();
  const createTag = useCreateTag();
  const updateTag = useUpdateTag();
  const deleteTag = useDeleteTag();

  const handleCreateTag = async () => {
    if (!tagName.trim()) {
      setError("Tag name is required");
      return;
    }

    setError(null);

    try {
      await createTag.mutateAsync({
        name: tagName.trim(),
        description: tagDescription.trim() || null,
      });
      setIsCreateDialogOpen(false);
      setTagName("");
      setTagDescription("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create tag");
    }
  };

  const handleEditTag = (tag: TagResponse) => {
    setEditingTag(tag);
    setTagName(tag.name);
    setTagDescription(tag.description || "");
    setIsEditDialogOpen(true);
  };

  const handleUpdateTag = async () => {
    if (!editingTag || !tagName.trim()) {
      setError("Tag name is required");
      return;
    }

    setError(null);

    try {
      await updateTag.mutateAsync({
        tagId: editingTag.id,
        data: {
          name: tagName.trim(),
          description: tagDescription.trim() || null,
        },
      });
      setIsEditDialogOpen(false);
      setEditingTag(null);
      setTagName("");
      setTagDescription("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update tag");
    }
  };

  const handleDeleteTag = async (tag: TagResponse) => {
    if (
      !window.confirm(`Delete tag "${tag.name}"? This action cannot be undone.`)
    ) {
      return;
    }

    try {
      await deleteTag.mutateAsync(tag.id);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete tag");
    }
  };

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (tag: TagResponse) => <BlueprintTag>{tag.name}</BlueprintTag>,
    },
    {
      key: "description",
      label: "Description",
      render: (tag: TagResponse) => tag.description || "-",
    },
    {
      key: "created_at",
      label: "Created",
      render: (tag: TagResponse) => formatDate(tag.created_at),
    },
    {
      key: "actions",
      label: "Actions",
      render: (tag: TagResponse) => (
        <div style={{ display: "flex", gap: spacing.xs }}>
          <Button
            small
            text="Edit"
            icon="edit"
            onClick={() => handleEditTag(tag)}
            intent={Intent.PRIMARY}
          />
          <Button
            small
            text="Delete"
            icon="trash"
            onClick={() => handleDeleteTag(tag)}
            intent={Intent.DANGER}
          />
        </div>
      ),
    },
  ];

  if (isLoading) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: spacing.lg,
        }}
      >
        <H1 style={{ ...pageHeader, marginBottom: 0 }}>Tag Manager</H1>
        <Button
          intent={Intent.PRIMARY}
          icon="plus"
          text="Create Tag"
          onClick={() => setIsCreateDialogOpen(true)}
        />
      </div>

      {tagsData && tagsData.tags.length > 0 ? (
        <>
          <DataTable
            data={tagsData.tags}
            columns={columns}
            keyExtractor={(tag) => tag.id}
          />
        </>
      ) : (
        <Callout intent={Intent.NONE} style={{ marginTop: spacing.lg }}>
          No tags found.
        </Callout>
      )}

      {/* Create Tag Dialog */}
      <Dialog
        isOpen={isCreateDialogOpen}
        onClose={() => {
          setIsCreateDialogOpen(false);
          setTagName("");
          setTagDescription("");
          setError(null);
        }}
        title="Create Tag"
        style={{ width: "500px" }}
      >
        <div style={{ padding: spacing.md }}>
          <FormGroup label="Tag Name" labelInfo="(required)">
            <InputGroup
              value={tagName}
              onChange={(e) => setTagName(e.target.value)}
              placeholder="e.g., weapons, components"
              required
            />
          </FormGroup>
          <FormGroup label="Description">
            <TextArea
              value={tagDescription}
              onChange={(e) => setTagDescription(e.target.value)}
              rows={3}
              placeholder="Optional description"
            />
          </FormGroup>
          {error && (
            <Callout
              intent={Intent.DANGER}
              style={{ marginBottom: spacing.md }}
            >
              {error}
            </Callout>
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
              onClick={() => {
                setIsCreateDialogOpen(false);
                setTagName("");
                setTagDescription("");
                setError(null);
              }}
              disabled={createTag.isPending}
            />
            <Button
              intent={Intent.PRIMARY}
              text="Create"
              onClick={handleCreateTag}
              loading={createTag.isPending}
            />
          </div>
        </div>
      </Dialog>

      {/* Edit Tag Dialog */}
      <Dialog
        isOpen={isEditDialogOpen}
        onClose={() => {
          setIsEditDialogOpen(false);
          setEditingTag(null);
          setTagName("");
          setTagDescription("");
          setError(null);
        }}
        title="Edit Tag"
        style={{ width: "500px" }}
      >
        <div style={{ padding: spacing.md }}>
          <FormGroup label="Tag Name" labelInfo="(required)">
            <InputGroup
              value={tagName}
              onChange={(e) => setTagName(e.target.value)}
              placeholder="e.g., weapons, components"
              required
            />
          </FormGroup>
          <FormGroup label="Description">
            <TextArea
              value={tagDescription}
              onChange={(e) => setTagDescription(e.target.value)}
              rows={3}
              placeholder="Optional description"
            />
          </FormGroup>
          {error && (
            <Callout
              intent={Intent.DANGER}
              style={{ marginBottom: spacing.md }}
            >
              {error}
            </Callout>
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
              onClick={() => {
                setIsEditDialogOpen(false);
                setEditingTag(null);
                setTagName("");
                setTagDescription("");
                setError(null);
              }}
              disabled={createTag.isPending}
            />
            <Button
              intent={Intent.PRIMARY}
              text="Update"
              onClick={handleUpdateTag}
              loading={createTag.isPending}
            />
          </div>
        </div>
      </Dialog>
    </DashboardLayout>
  );
}
