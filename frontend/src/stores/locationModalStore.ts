/**
 * Zustand store for managing LocationModal state.
 * Handles both modal visibility and form data.
 */

import { create } from "zustand";
import type { UseMutationResult } from "@tanstack/react-query";
import { LocationType, OwnerType } from "../types/enums";
import type {
  Location,
  LocationCreate,
  LocationUpdate,
} from "../types/location";
import type {
  CanonicalLocation,
  CanonicalLocationCreate,
  CanonicalLocationUpdate,
} from "../types/canonical_location";
import { WORLD_OWNER_UUID } from "../constants/location";

export interface LocationModalFormState {
  // Form fields
  name: string;
  type: LocationType;
  ownerType: OwnerType;
  parentLocationId: string;
  parentSearch: string;
  canonicalLocationId: string;
  canonicalSearch: string;
  isCanonical: boolean;
  metadataJson: string;
}

interface LocationModalStore extends LocationModalFormState {
  // Modal state
  isOpen: boolean;
  location: Location | null;
  isSubmitting: boolean;
  error: string | null;

  // Actions
  openCreateModal: (organizationId?: string | null) => void;
  openEditModal: (location: Location) => void;
  closeModal: () => void;
  resetForm: () => void;
  initializeFromLocation: (location: Location) => void;
  initializeForNew: (organizationId?: string | null) => void;

  // Form field setters
  setName: (name: string) => void;
  setType: (type: LocationType) => void;
  setOwnerType: (ownerType: OwnerType) => void;
  setParentLocationId: (id: string) => void;
  setParentSearch: (search: string) => void;
  setCanonicalLocationId: (id: string) => void;
  setCanonicalSearch: (search: string) => void;
  setIsCanonical: (isCanonical: boolean) => void;
  setMetadataJson: (json: string) => void;

  // Submission
  setSubmitting: (isSubmitting: boolean) => void;
  setError: (error: string | null) => void;
  handleSubmit: (
    createMutation: UseMutationResult<Location, Error, LocationCreate, unknown>,
    updateMutation: UseMutationResult<
      Location,
      Error,
      { id: string; data: LocationUpdate },
      unknown
    >,
    updateCanonicalMutation: UseMutationResult<
      CanonicalLocation,
      Error,
      { id: string; data: CanonicalLocationUpdate },
      unknown
    >,
    createCanonicalMutation: UseMutationResult<
      CanonicalLocation,
      Error,
      CanonicalLocationCreate,
      unknown
    >,
    isAdmin: boolean,
    userId: string,
    organizationId?: string | null
  ) => Promise<void>;
}

const initialFormState: LocationModalFormState = {
  name: "",
  type: LocationType.WAREHOUSE,
  ownerType: OwnerType.USER,
  parentLocationId: "",
  parentSearch: "",
  canonicalLocationId: "",
  canonicalSearch: "",
  isCanonical: false,
  metadataJson: "",
};

export const useLocationModalStore = create<LocationModalStore>((set, get) => ({
  // Initial state
  ...initialFormState,
  isOpen: false,
  location: null,
  isSubmitting: false,
  error: null,

  // Modal actions
  openCreateModal: (organizationId) => {
    get().initializeForNew(organizationId);
    set({ isOpen: true, error: null });
  },

  openEditModal: (location) => {
    get().initializeFromLocation(location);
    set({ isOpen: true, error: null });
  },

  closeModal: () => {
    set({ isOpen: false, location: null, error: null, isSubmitting: false });
    get().resetForm();
  },

  resetForm: () => {
    set(initialFormState);
  },

  initializeFromLocation: (location) => {
    set({
      name: location.name,
      type: location.type,
      ownerType: location.owner_type,
      parentLocationId: location.parent_location_id || "",
      // Set parent search to the parent location name if it exists
      parentSearch: location.parent_location_name || "",
      canonicalLocationId: location.canonical_location_id || "",
      // Set canonical search - we'll need to fetch the canonical location name
      // For now, set to empty and let the selector handle it
      canonicalSearch: "",
      isCanonical: Boolean(location.is_canonical),
      metadataJson: location.metadata
        ? JSON.stringify(location.metadata, null, 2)
        : "",
      location,
    });
  },

  initializeForNew: (organizationId) => {
    set({
      ...initialFormState,
      ownerType: organizationId ? OwnerType.ORGANIZATION : OwnerType.USER,
      location: null,
    });
  },

  // Form field setters
  setName: (name) => set({ name }),
  setType: (type) => set({ type }),
  setOwnerType: (ownerType) => set({ ownerType }),
  setParentLocationId: (id) => set({ parentLocationId: id }),
  setParentSearch: (search) => set({ parentSearch: search }),
  setCanonicalLocationId: (id) => set({ canonicalLocationId: id }),
  setCanonicalSearch: (search) => set({ canonicalSearch: search }),
  setIsCanonical: (isCanonical) => set({ isCanonical }),
  setMetadataJson: (json) => set({ metadataJson: json }),

  // Submission helpers
  setSubmitting: (isSubmitting) => set({ isSubmitting }),
  setError: (error) => set({ error }),

  handleSubmit: async (
    createMutation,
    updateMutation,
    updateCanonicalMutation,
    createCanonicalMutation,
    isAdmin,
    userId: string,
    organizationId?: string | null
  ) => {
    const state = get();
    set({ isSubmitting: true, error: null });

    try {
      // Parse metadata JSON
      let metadata: Record<string, unknown> | undefined;
      if (state.metadataJson.trim()) {
        try {
          metadata = JSON.parse(state.metadataJson);
        } catch (e) {
          set({
            error: "Invalid JSON in metadata field",
            isSubmitting: false,
          });
          return;
        }
      }

      // Determine owner_id based on owner_type
      let ownerId: string | undefined = userId;
      if (state.ownerType === OwnerType.ORGANIZATION && organizationId) {
        ownerId = organizationId;
      } else if (state.ownerType === OwnerType.SHIP) {
        // TODO: Allow user to select from available ships
        // For now, we'll use the user ID as a placeholder
        ownerId = userId;
      } else if (state.ownerType === OwnerType.WORLD) {
        // World-owned locations use a placeholder UUID (universe-owned)
        ownerId = WORLD_OWNER_UUID;
      }

      if (state.location) {
        // Update existing location
        if (state.location.is_canonical) {
          // Update canonical location using canonical endpoint
          const canonicalUpdateData: {
            name: string;
            type: LocationType;
            parent_location_id?: string;
            metadata?: Record<string, unknown>;
          } = {
            name: state.name,
            type: state.type,
          };
          if (state.parentLocationId) {
            canonicalUpdateData.parent_location_id = state.parentLocationId;
          }
          if (metadata && Object.keys(metadata).length > 0) {
            canonicalUpdateData.metadata = metadata;
          }
          await updateCanonicalMutation.mutateAsync({
            id: state.location.id,
            data: canonicalUpdateData,
          });
        } else {
          // Update regular location - only include fields allowed in LocationUpdate
          const updateData: LocationUpdate = {
            name: state.name,
            type: state.type,
            ...(state.parentLocationId && {
              parent_location_id: state.parentLocationId,
            }),
            ...(state.canonicalLocationId && {
              canonical_location_id: state.canonicalLocationId,
            }),
            ...(metadata && Object.keys(metadata).length > 0 && { metadata }),
          };
          await updateMutation.mutateAsync({
            id: state.location.id,
            data: updateData,
          });
        }
      } else {
        // Create new location
        // Build the create data object with all required fields
        const createData: LocationCreate = {
          name: state.name,
          type: state.type,
          owner_type: state.ownerType,
          owner_id: ownerId,
          ...(state.parentLocationId && {
            parent_location_id: state.parentLocationId,
          }),
          ...(state.canonicalLocationId && {
            canonical_location_id: state.canonicalLocationId,
          }),
          ...(metadata && Object.keys(metadata).length > 0 && { metadata }),
        };

        // Check if this should be created as a canonical location
        if (state.isCanonical && isAdmin) {
          // Create as canonical location
          const canonicalData: {
            name: string;
            type: LocationType;
            parent_location_id?: string;
            metadata?: Record<string, unknown>;
          } = {
            name: state.name,
            type: state.type,
          };
          if (state.parentLocationId) {
            canonicalData.parent_location_id = state.parentLocationId;
          }
          if (metadata && Object.keys(metadata).length > 0) {
            canonicalData.metadata = metadata;
          }
          await createCanonicalMutation.mutateAsync(canonicalData);
        } else {
          // Create as regular location
          await createMutation.mutateAsync(createData);
        }
      }

      // Success - reset submitting state and close modal
      set({ isSubmitting: false });
      get().closeModal();
    } catch (err: unknown) {
      console.error("Failed to save location:", err);
      set({
        error: "Failed to save location. Please try again.",
        isSubmitting: false,
      });
    }
  },
}));
