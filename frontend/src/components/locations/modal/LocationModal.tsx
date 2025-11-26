/**
 * Location Creation/Edit Modal Component
 *
 * A self-contained modal for creating and editing locations.
 * Uses Zustand store for state management and handles all submission logic internally.
 */

import React, { useMemo } from "react";
import {
  FormGroup,
  InputGroup,
  Intent,
  Callout,
  Checkbox,
} from "@blueprintjs/core";
import { EntityModal } from "../../common/EntityModal";
import { EasySelect, type EasySelectOption } from "../../common/EasySelect";
import { usePublicLocations } from "../../../hooks/queries/commons";
import { useLocations } from "../../../hooks/queries/locations";
import {
  useCreateLocation,
  useUpdateLocation,
} from "../../../hooks/mutations/locations";
import {
  useCreateCanonicalLocation,
  useUpdateCanonicalLocation,
} from "../../../hooks/mutations/canonical_locations";
import { useAuth } from "../../../contexts/AuthContext";
import { useAdmin } from "../../../hooks/useAdmin";
import { spacing } from "../../../styles/theme";
import { LocationType } from "../../../types/enums";
import { useLocationModalStore } from "../../../stores/locationModalStore";
import { LOCATION_TYPES } from "./constants";
import { ParentLocationSelector } from "./ParentLocationSelector";
import { CanonicalLocationSelector } from "./CanonicalLocationSelector";
import { OwnerTypeSelector } from "./OwnerTypeSelector";
import { ViewEditField } from "../../common/ViewEditField";
import { MetadataField } from "../../common/MetadataField";

/**
 * Self-contained LocationModal component.
 * Gets all state from Zustand store and handles submission internally.
 */
export function LocationModal() {
  const { user } = useAuth();
  const { isAdmin } = useAdmin();
  const organizationId = undefined; // TODO: Get organization ID from user's organizations

  // Get all state and actions from store
  const {
    isOpen,
    mode,
    location,
    isSubmitting,
    error,
    name,
    type,
    ownerType,
    parentLocationId,
    parentSearch,
    canonicalLocationId,
    canonicalSearch,
    isCanonical,
    metadataJson,
    closeModal,
    switchToEditMode,
    setName,
    setType,
    setOwnerType,
    setParentLocationId,
    setParentSearch,
    setCanonicalLocationId,
    setCanonicalSearch,
    setIsCanonical,
    setMetadataJson,
    handleSubmit: storeHandleSubmit,
  } = useLocationModalStore();

  const isViewMode = mode === "view";
  const isEditMode = mode === "edit";

  // Mutations for submission
  const createMutation = useCreateLocation();
  const updateMutation = useUpdateLocation();
  const updateCanonicalMutation = useUpdateCanonicalLocation();
  const createCanonicalMutation = useCreateCanonicalLocation();

  // Determine if we're editing a canonical location
  const isEditingCanonical = Boolean(isEditMode && location?.is_canonical);

  // If editing and we have a parent/canonical location ID but no search value,
  // we need to fetch the location name to display it
  const needsParentName =
    isEditMode &&
    location?.parent_location_id &&
    !parentSearch &&
    !location?.parent_location_name;
  const needsCanonicalName =
    isEditMode &&
    location?.canonical_location_id &&
    !canonicalSearch &&
    !isEditingCanonical;

  // Search for canonical locations (for linking regular locations to canonical)
  // Only fetch if not editing canonical (canonical locations can't link to other canonical)
  // Also fetch if we need the canonical location name
  const shouldFetchCanonical =
    (!isEditingCanonical && !!canonicalSearch) || needsCanonicalName;
  const { data: canonicalLocationsData } = usePublicLocations({
    skip: 0,
    limit: 50,
    search:
      shouldFetchCanonical && canonicalSearch ? canonicalSearch : undefined,
  });

  // Search for parent locations
  // If editing canonical, we'll use canonical locations; otherwise use user's accessible locations
  // Also fetch if we need the parent location name
  const shouldFetchParent = !!parentSearch || needsParentName;
  const { data: parentLocationsData } = useLocations({
    skip: 0,
    limit: 50,
    search:
      shouldFetchParent && !isEditingCanonical && parentSearch
        ? parentSearch
        : undefined,
    enabled: Boolean(shouldFetchParent && !isEditingCanonical),
  });

  // For canonical locations, fetch canonical locations for parent selection
  const shouldFetchCanonicalParent =
    isEditingCanonical && (!!parentSearch || needsParentName);
  const { data: canonicalParentLocationsData } = usePublicLocations({
    skip: 0,
    limit: 50,
    search:
      shouldFetchCanonicalParent && parentSearch ? parentSearch : undefined,
  });

  // Update search values when we have location data but no search value
  React.useEffect(() => {
    if (isEditMode && location) {
      // Set parent search from parent_location_name if available
      if (location.parent_location_name && !parentSearch) {
        setParentSearch(location.parent_location_name);
      }
      // For canonical location, we need to find it in the fetched data
      if (
        location.canonical_location_id &&
        !canonicalSearch &&
        canonicalLocationsData?.entities
      ) {
        const canonical = canonicalLocationsData.entities.find(
          (e) => (e.canonical_id || e.id) === location.canonical_location_id
        );
        if (canonical) {
          const locName =
            (canonical.data as { name?: string })?.name || canonical.id;
          setCanonicalSearch(locName);
        }
      }
    }
  }, [
    isEditMode,
    location,
    parentSearch,
    canonicalSearch,
    canonicalLocationsData,
    setParentSearch,
    setCanonicalSearch,
  ]);

  // Handle form submission
  const handleSubmit = async () => {
    await storeHandleSubmit(
      createMutation,
      updateMutation,
      updateCanonicalMutation,
      createCanonicalMutation,
      isAdmin,
      user?.id || "",
      organizationId
    );
  };

  const validateForm = (): boolean => {
    if (!name.trim()) return false;
    if (metadataJson.trim()) {
      try {
        JSON.parse(metadataJson);
      } catch {
        return false;
      }
    }
    return true;
  };

  const canonicalLocations = canonicalLocationsData?.entities || [];
  // For canonical locations, use canonical locations as parent options; otherwise use regular locations
  let parentLocations = isEditingCanonical
    ? (canonicalParentLocationsData?.entities || []).map((entity) => ({
        id: entity.canonical_id || entity.id,
        name: (entity.data as { name?: string })?.name || entity.id,
        type: (entity.data as { type?: string })?.type || "unknown",
      }))
    : parentLocationsData?.locations || [];

  // If editing and we have a parent location ID, ensure it's in the list
  // This handles the case where the parent location isn't in the search results
  if (
    isEditMode &&
    location?.parent_location_id &&
    location?.parent_location_name
  ) {
    const parentExists = parentLocations.some(
      (loc) => loc.id === location.parent_location_id
    );
    if (!parentExists) {
      // Add the parent location to the list so it appears in the dropdown
      parentLocations = [
        {
          id: location.parent_location_id,
          name: location.parent_location_name,
          type: "unknown", // We don't have the type, but it's better than nothing
        },
        ...parentLocations,
      ];
    }
  }

  // Convert location types to EasySelect format
  const locationTypeOptions: EasySelectOption[] = useMemo(
    () =>
      LOCATION_TYPES.map((opt) => ({
        value: opt.value,
        label: opt.label,
      })),
    []
  );

  const modalTitle = isViewMode
    ? `View Location: ${location?.name || ""}`
    : isEditMode
    ? "Edit Location"
    : "Create New Location";

  // Determine if user can edit (for view mode)
  const canEdit = isAdmin || !location?.is_canonical;

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
        <FormGroup label="Name" labelInfo="(required)">
          <ViewEditField
            isViewMode={isViewMode}
            viewContent={name}
            editContent={
              <InputGroup
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter location name"
                disabled={isSubmitting}
                fill
              />
            }
          />
        </FormGroup>

        {isViewMode ? (
          <FormGroup label="Type">
            <ViewEditField
              isViewMode={true}
              viewContent={
                LOCATION_TYPES.find((opt) => opt.value === type)?.label || type
              }
              editContent={null}
            />
          </FormGroup>
        ) : (
          <EasySelect
            label="Type"
            value={type}
            options={locationTypeOptions}
            onValueChange={(newValue) => setType(newValue as LocationType)}
            disabled={isSubmitting}
            placeholder="Select location type..."
            fill
          />
        )}

        {!isEditMode && !isViewMode && (
          <OwnerTypeSelector
            value={ownerType}
            onChange={setOwnerType}
            disabled={isSubmitting || isEditMode}
            organizationId={organizationId}
          />
        )}

        {!isViewMode && (
          <ParentLocationSelector
            value={parentLocationId || ""}
            searchValue={parentSearch}
            locations={parentLocations}
            isSubmitting={isSubmitting}
            isCanonical={isEditingCanonical}
            onValueChange={setParentLocationId}
            onSearchChange={setParentSearch}
          />
        )}
        {isViewMode && location?.parent_location_name && (
          <FormGroup label="Parent Location">
            <ViewEditField
              isViewMode={true}
              viewContent={location.parent_location_name}
              editContent={null}
            />
          </FormGroup>
        )}

        {isAdmin && !isEditMode && !isViewMode && (
          <FormGroup
            label="Canonical Location"
            helperText="Mark this location as canonical to add it to public commons (admin only)"
          >
            <Checkbox
              checked={isCanonical}
              onChange={(e) => setIsCanonical(e.currentTarget.checked)}
              disabled={isSubmitting}
              label="Create as canonical location (public commons)"
            />
            {isCanonical && (
              <Callout
                intent={Intent.WARNING}
                style={{ marginTop: spacing.xs }}
              >
                This location will be added to public commons and be visible to
                all users.
              </Callout>
            )}
          </FormGroup>
        )}

        {!isEditingCanonical && !isViewMode && (
          <CanonicalLocationSelector
            value={canonicalLocationId || ""}
            searchValue={canonicalSearch}
            locations={canonicalLocations}
            isSubmitting={isSubmitting}
            onValueChange={setCanonicalLocationId}
            onSearchChange={setCanonicalSearch}
          />
        )}
        {isViewMode && location?.is_canonical && (
          <FormGroup label="Canonical">
            <ViewEditField
              isViewMode={true}
              viewContent="Yes (Public Commons)"
              editContent={null}
            />
          </FormGroup>
        )}

        <MetadataField
          isViewMode={isViewMode}
          value={metadataJson}
          onChange={setMetadataJson}
          disabled={isSubmitting}
        />
      </div>
    </EntityModal>
  );
}
