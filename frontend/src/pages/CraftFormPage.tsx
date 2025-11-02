/**
 * Craft creation wizard page component using Blueprint.js.
 */

import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  H1,
  H3,
  Callout,
  Intent,
  Spinner,
  Button,
  FormGroup,
  HTMLSelect,
  NumericInput,
  Switch,
  Card,
  Divider,
  Tag,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useBlueprints } from "../hooks/queries/blueprints";
import { useLocations } from "../hooks/queries/locations";
import { useItems } from "../hooks/queries/items";
import { useCreateCraft } from "../hooks/queries/crafts";
import { pageHeader } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type { CraftCreate, Blueprint } from "../types";

function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

export default function CraftFormPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const blueprintIdFromUrl = searchParams.get("blueprint_id");

  const { data: blueprintsData, isLoading: isLoadingBlueprints } =
    useBlueprints({
      skip: 0,
      limit: 1000,
      is_public: undefined, // Get both public and private
    });
  const { data: locationsData, isLoading: isLoadingLocations } = useLocations({
    skip: 0,
    limit: 1000,
  });
  const { data: itemsData } = useItems({ skip: 0, limit: 1000 });
  const createCraft = useCreateCraft();

  const [blueprintId, setBlueprintId] = useState(blueprintIdFromUrl || "");
  const [outputLocationId, setOutputLocationId] = useState("");
  const [priority, setPriority] = useState(5);
  const [scheduledStart, setScheduledStart] = useState("");
  const [reserveIngredients, setReserveIngredients] = useState(false);
  const [selectedBlueprint, setSelectedBlueprint] = useState<Blueprint | null>(
    null
  );

  // Update selected blueprint when blueprintId changes
  useEffect(() => {
    if (blueprintId && blueprintsData?.items) {
      const bp = blueprintsData.items.find((b) => b.id === blueprintId);
      setSelectedBlueprint(bp || null);
    } else {
      setSelectedBlueprint(null);
    }
  }, [blueprintId, blueprintsData]);

  // Set blueprint from URL param
  useEffect(() => {
    if (blueprintIdFromUrl) {
      setBlueprintId(blueprintIdFromUrl);
    }
  }, [blueprintIdFromUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!blueprintId || !outputLocationId) {
      return;
    }

    const craftData: CraftCreate = {
      blueprint_id: blueprintId,
      output_location_id: outputLocationId,
      priority,
      scheduled_start: scheduledStart || null,
      metadata: null,
    };

    try {
      const result = await createCraft.mutateAsync({
        data: craftData,
        reserve_ingredients: reserveIngredients,
      });
      navigate(`/crafts/${result.id}`);
    } catch (error) {
      console.error("Failed to create craft:", error);
    }
  };

  const isLoading = isLoadingBlueprints || isLoadingLocations;
  const isSaving = createCraft.isPending;

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
      <H1 style={pageHeader}>Create Craft</H1>

      <form onSubmit={handleSubmit}>
        <Card style={{ marginBottom: spacing.lg }}>
          <H3>Select Blueprint</H3>
          <FormGroup
            label="Blueprint"
            labelFor="blueprint"
            helperText="Select the blueprint to craft"
          >
            <HTMLSelect
              id="blueprint"
              value={blueprintId}
              onChange={(e) => setBlueprintId(e.target.value)}
              fill
              required
              data-tour="blueprint-select"
            >
              <option value="">Select a blueprint...</option>
              {blueprintsData?.items.map((bp) => (
                <option key={bp.id} value={bp.id}>
                  {bp.name} {bp.is_public ? "(Public)" : "(Private)"}
                  {bp.category ? ` - ${bp.category}` : ""}
                </option>
              ))}
            </HTMLSelect>
          </FormGroup>

          {selectedBlueprint && (
            <Card
              style={{
                marginTop: spacing.md,
                backgroundColor: colors.background.secondary,
              }}
              data-tour="blueprint-preview"
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: spacing.sm,
                }}
              >
                <strong>{selectedBlueprint.name}</strong>
                {selectedBlueprint.category && (
                  <Tag>{selectedBlueprint.category}</Tag>
                )}
              </div>
              {selectedBlueprint.description && (
                <p
                  style={{
                    color: colors.text.secondary,
                    marginBottom: spacing.sm,
                  }}
                >
                  {selectedBlueprint.description}
                </p>
              )}
              <Divider />
              <div style={{ marginTop: spacing.sm, fontSize: "0.9em" }}>
                <div style={{ marginBottom: spacing.xs }}>
                  <strong>Crafting Time:</strong>{" "}
                  {formatTime(selectedBlueprint.crafting_time_minutes)}
                </div>
                <div style={{ marginBottom: spacing.xs }}>
                  <strong>Output:</strong> {selectedBlueprint.output_quantity}x{" "}
                  {selectedBlueprint.output_item?.name || "Unknown Item"}
                </div>
                <div style={{ marginBottom: spacing.xs }}>
                  <strong>Ingredients:</strong>{" "}
                  {selectedBlueprint.blueprint_data.ingredients.length} required
                </div>
                {selectedBlueprint.blueprint_data.ingredients.length > 0 && (
                  <div style={{ marginTop: spacing.sm }}>
                    <strong>Required Items:</strong>
                    <ul
                      style={{ marginTop: spacing.xs, paddingLeft: spacing.lg }}
                    >
                      {selectedBlueprint.blueprint_data.ingredients.map(
                        (ing, idx) => {
                          const item = itemsData?.items.find(
                            (i) => i.id === ing.item_id
                          );
                          return (
                            <li key={idx}>
                              {ing.quantity}x {item?.name || ing.item_id}{" "}
                              {ing.optional && (
                                <Tag minimal intent="warning">
                                  optional
                                </Tag>
                              )}
                            </li>
                          );
                        }
                      )}
                    </ul>
                  </div>
                )}
              </div>
            </Card>
          )}
        </Card>

        <Card style={{ marginBottom: spacing.lg }}>
          <H3>Craft Configuration</H3>
          <FormGroup
            label="Output Location"
            labelFor="output_location"
            helperText="Where the crafted items will be placed"
          >
            <HTMLSelect
              id="output_location"
              value={outputLocationId}
              onChange={(e) => setOutputLocationId(e.target.value)}
              fill
              required
              data-tour="output-location"
            >
              <option value="">Select output location...</option>
              {locationsData?.locations?.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.name} ({loc.type})
                </option>
              ))}
            </HTMLSelect>
          </FormGroup>

          <FormGroup
            label="Priority"
            labelFor="priority"
            helperText="Craft priority (0-100, higher is more important)"
          >
            <NumericInput
              id="priority"
              value={priority}
              onValueChange={(value) =>
                setPriority(Math.max(0, Math.min(100, value || 0)))
              }
              min={0}
              max={100}
              fill
              data-tour="priority-input"
            />
          </FormGroup>

          <FormGroup
            label="Scheduled Start (Optional)"
            labelFor="scheduled_start"
            helperText="Schedule this craft to start at a specific time"
          >
            <input
              id="scheduled_start"
              type="datetime-local"
              value={scheduledStart}
              onChange={(e) => setScheduledStart(e.target.value)}
              style={{
                width: "100%",
                padding: spacing.sm,
                fontSize: "14px",
                border: `1px solid ${colors.border.medium}`,
                borderRadius: "3px",
              }}
            />
          </FormGroup>

          <FormGroup helperText="Automatically reserve ingredients when creating this craft">
            <div data-tour="reserve-ingredients">
              <Switch
                checked={reserveIngredients}
                onChange={(e) => setReserveIngredients(e.currentTarget.checked)}
                label="Reserve Ingredients on Creation"
              />
            </div>
          </FormGroup>
        </Card>

        {createCraft.error && (
          <Callout intent={Intent.DANGER} style={{ marginBottom: spacing.lg }}>
            Error creating craft:{" "}
            {createCraft.error instanceof Error
              ? createCraft.error.message
              : "Unknown error"}
          </Callout>
        )}

        <div style={{ display: "flex", gap: spacing.md }}>
          <Button
            type="submit"
            intent="primary"
            text="Create Craft"
            icon="add"
            loading={isSaving}
            disabled={!blueprintId || !outputLocationId}
            data-tour="create-button"
          />
          <Button
            text="Cancel"
            onClick={() => navigate("/crafts")}
            disabled={isSaving}
          />
        </div>
      </form>
    </DashboardLayout>
  );
}
