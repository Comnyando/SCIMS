/**
 * Craft Creation/Edit/View Modal Component
 *
 * A self-contained modal for creating, editing, and viewing crafts.
 * Uses Zustand store for state management and handles all submission logic internally.
 */

import { useMemo } from "react";
import { FormGroup, NumericInput, InputGroup } from "@blueprintjs/core";
import { EntityModal } from "../../common/EntityModal";
import { ViewEditField } from "../../common/ViewEditField";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";
import {
  useCreateCraft,
  useUpdateCraft,
} from "../../../hooks/mutations/crafts";
import { useCraftModalStore } from "../../../stores/craftModalStore";
import { useBlueprints } from "../../../hooks/queries/blueprints";
import { useLocations } from "../../../hooks/queries/locations";
import { colors } from "../../../styles/theme";
import type { Blueprint } from "../../../types/blueprint";
import type { Location } from "../../../types/location";

/**
 * Self-contained CraftModal component.
 * Gets all state from Zustand store and handles submission internally.
 */
export function CraftModal() {
  // Get all state and actions from store
  const {
    isOpen,
    mode,
    craft,
    isSubmitting,
    error,
    blueprintId,
    outputLocationId,
    priority,
    scheduledStart,
    closeModal,
    switchToEditMode,
    setBlueprintId,
    setOutputLocationId,
    setPriority,
    setScheduledStart,
    handleSubmit: storeHandleSubmit,
  } = useCraftModalStore();

  const isViewMode = mode === "view";
  const isEditMode = mode === "edit";

  // Fetch blueprints and locations for dropdowns
  const { data: blueprintsData } = useBlueprints({
    skip: 0,
    limit: 1000,
    is_public: undefined,
  });
  const { data: locationsData } = useLocations({ skip: 0, limit: 1000 });
  const blueprints = useMemo(
    () => blueprintsData?.items || [],
    [blueprintsData?.items]
  );
  const locations = useMemo(
    () => locationsData?.locations || [],
    [locationsData?.locations]
  );

  // Convert to EasySelect options
  const blueprintOptions: EasySelectOption<Blueprint>[] = useMemo(
    () =>
      blueprints.map((bp) => ({
        value: bp.id,
        label: bp.name,
        secondaryText: bp.category || undefined,
        data: bp,
      })),
    [blueprints]
  );

  const locationOptions: EasySelectOption<Location>[] = useMemo(
    () =>
      locations.map((loc) => ({
        value: loc.id,
        label: loc.name,
        secondaryText: loc.type,
        data: loc,
      })),
    [locations]
  );

  // Mutations for submission
  const createMutation = useCreateCraft();
  const updateMutation = useUpdateCraft();

  // Handle form submission
  const handleSubmit = async () => {
    await storeHandleSubmit(createMutation, updateMutation);
  };

  const validateForm = (): boolean => {
    if (!blueprintId) return false;
    if (!outputLocationId) return false;
    if (priority < 1 || priority > 10) return false;
    return true;
  };

  const modalTitle = isViewMode
    ? `View Craft: ${craft?.blueprint?.name || "Unknown Blueprint"}`
    : isEditMode
    ? "Edit Craft"
    : "Create New Craft";

  // For crafts, all authenticated users can edit their own
  const canEdit = true; // TODO: Check ownership/permissions

  const getBlueprintName = (bpId: string): string => {
    const bp = blueprints.find((b) => b.id === bpId);
    return bp?.name || bpId || "—";
  };

  const getLocationName = (locId: string): string => {
    const loc = locations.find((l) => l.id === locId);
    return loc?.name || locId || "—";
  };

  return (
    <EntityModal
      isOpen={isOpen}
      onClose={closeModal}
      title={modalTitle}
      mode={mode}
      onSwitchToEdit={switchToEditMode}
      canEdit={canEdit}
      submitText={isEditMode ? "Update" : "Create"}
      onSubmit={isViewMode ? undefined : handleSubmit}
      isSubmitting={isSubmitting}
      error={error}
      isSubmitDisabled={!validateForm()}
    >
      <div>
        {isViewMode ? (
          <FormGroup label="Blueprint" labelInfo="(required)">
            <ViewEditField
              isViewMode={true}
              viewContent={getBlueprintName(blueprintId)}
              editContent={null}
            />
          </FormGroup>
        ) : (
          <EasySelect
            label="Blueprint"
            labelInfo="(required)"
            value={blueprintId}
            options={blueprintOptions}
            onValueChange={(newValue) => setBlueprintId(newValue as string)}
            disabled={isSubmitting || isEditMode} // Can't change blueprint after creation
            placeholder="Search and select blueprint..."
            fill
          />
        )}

        {isViewMode ? (
          <FormGroup label="Output Location" labelInfo="(required)">
            <ViewEditField
              isViewMode={true}
              viewContent={getLocationName(outputLocationId)}
              editContent={null}
            />
          </FormGroup>
        ) : (
          <EasySelect
            label="Output Location"
            labelInfo="(required)"
            value={outputLocationId}
            options={locationOptions}
            onValueChange={(newValue) =>
              setOutputLocationId(newValue as string)
            }
            disabled={isSubmitting}
            placeholder="Search and select output location..."
            fill
          />
        )}

        <FormGroup
          label="Priority"
          labelInfo="(1-10)"
          helperText="Higher priority crafts are processed first"
        >
          <ViewEditField
            isViewMode={isViewMode}
            viewContent={priority.toString()}
            editContent={
              <NumericInput
                value={priority}
                onValueChange={(value) => setPriority(value || 5)}
                min={1}
                max={10}
                disabled={isSubmitting}
                fill
              />
            }
          />
        </FormGroup>

        <FormGroup
          label="Scheduled Start"
          labelInfo="(optional)"
          helperText="When to start this craft (leave empty for immediate start)"
        >
          <ViewEditField
            isViewMode={isViewMode}
            viewContent={
              scheduledStart ? (
                new Date(scheduledStart).toLocaleString()
              ) : (
                <span style={{ color: colors.text.muted }}>Immediate</span>
              )
            }
            editContent={
              <InputGroup
                type="datetime-local"
                value={scheduledStart}
                onChange={(e) => setScheduledStart(e.target.value)}
                disabled={isSubmitting}
                fill
              />
            }
          />
        </FormGroup>

        {isViewMode && craft && (
          <>
            <FormGroup label="Status">
              <ViewEditField
                isViewMode={true}
                viewContent={craft.status}
                editContent={null}
              />
            </FormGroup>
            {craft.started_at && (
              <FormGroup label="Started At">
                <ViewEditField
                  isViewMode={true}
                  viewContent={new Date(craft.started_at).toLocaleString()}
                  editContent={null}
                />
              </FormGroup>
            )}
            {craft.completed_at && (
              <FormGroup label="Completed At">
                <ViewEditField
                  isViewMode={true}
                  viewContent={new Date(craft.completed_at).toLocaleString()}
                  editContent={null}
                />
              </FormGroup>
            )}
          </>
        )}
      </div>
    </EntityModal>
  );
}
