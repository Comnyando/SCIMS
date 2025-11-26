/**
 * Zustand store for managing CraftModal state.
 * Handles both modal visibility and form data.
 */

import { create } from "zustand";
import type { UseMutationResult } from "@tanstack/react-query";
import type { Craft, CraftCreate, CraftUpdate } from "../types/craft";

export interface CraftModalFormState {
  // Form fields
  blueprintId: string;
  organizationId: string | null;
  outputLocationId: string;
  priority: number;
  scheduledStart: string; // ISO date string
}

interface CraftModalStore extends CraftModalFormState {
  // Modal state
  isOpen: boolean;
  mode: "view" | "edit" | "create";
  craft: Craft | null;
  isSubmitting: boolean;
  error: string | null;

  // Actions
  openCreateModal: (blueprintId?: string) => void;
  openViewModal: (craft: Craft) => void;
  openEditModal: (craft: Craft) => void;
  switchToEditMode: () => void;
  closeModal: () => void;
  resetForm: () => void;
  initializeFromCraft: (craft: Craft) => void;
  initializeForNew: (blueprintId?: string) => void;

  // Form field setters
  setBlueprintId: (blueprintId: string) => void;
  setOrganizationId: (organizationId: string | null) => void;
  setOutputLocationId: (locationId: string) => void;
  setPriority: (priority: number) => void;
  setScheduledStart: (date: string) => void;

  // Submission
  setSubmitting: (isSubmitting: boolean) => void;
  setError: (error: string | null) => void;
  handleSubmit: (
    createMutation: UseMutationResult<Craft, Error, CraftCreate, unknown>,
    updateMutation: UseMutationResult<
      Craft,
      Error,
      { id: string; data: CraftUpdate },
      unknown
    >
  ) => Promise<void>;
}

const initialFormState: CraftModalFormState = {
  blueprintId: "",
  organizationId: null,
  outputLocationId: "",
  priority: 5,
  scheduledStart: "",
};

export const useCraftModalStore = create<CraftModalStore>((set, get) => ({
  ...initialFormState,

  // Modal state
  isOpen: false,
  mode: "create",
  craft: null,
  isSubmitting: false,
  error: null,

  // Modal actions
  openCreateModal: (blueprintId?: string) => {
    get().initializeForNew(blueprintId);
    set({ isOpen: true, mode: "create" });
  },

  openViewModal: (craft: Craft) => {
    get().initializeFromCraft(craft);
    set({ isOpen: true, mode: "view", craft });
  },

  openEditModal: (craft: Craft) => {
    get().initializeFromCraft(craft);
    set({ isOpen: true, mode: "edit", craft });
  },

  switchToEditMode: () => {
    set({ mode: "edit" });
  },

  closeModal: () => {
    set({
      isOpen: false,
      mode: "create",
      craft: null,
      isSubmitting: false,
      error: null,
    });
    get().resetForm();
  },

  resetForm: () => {
    set(initialFormState);
  },

  initializeFromCraft: (craft: Craft) => {
    set({
      blueprintId: craft.blueprint_id,
      organizationId: craft.organization_id,
      outputLocationId: craft.output_location_id,
      priority: craft.priority,
      scheduledStart: craft.scheduled_start
        ? new Date(craft.scheduled_start).toISOString().slice(0, 16) // Format for datetime-local input
        : "",
    });
  },

  initializeForNew: (blueprintId?: string) => {
    set({
      ...initialFormState,
      blueprintId: blueprintId || "",
      craft: null,
    });
  },

  // Form field setters
  setBlueprintId: (blueprintId) => set({ blueprintId }),
  setOrganizationId: (organizationId) => set({ organizationId }),
  setOutputLocationId: (locationId) => set({ outputLocationId: locationId }),
  setPriority: (priority) => set({ priority }),
  setScheduledStart: (date) => set({ scheduledStart: date }),

  // Submission helpers
  setSubmitting: (isSubmitting) => set({ isSubmitting }),
  setError: (error) => set({ error }),

  handleSubmit: async (createMutation, updateMutation) => {
    const state = get();
    set({ isSubmitting: true, error: null });

    try {
      if (state.craft) {
        // Update existing craft
        const updateData: CraftUpdate = {
          ...(state.organizationId !== null && {
            organization_id: state.organizationId,
          }),
          output_location_id: state.outputLocationId,
          priority: state.priority,
          scheduled_start: state.scheduledStart || null,
        };
        await updateMutation.mutateAsync({
          id: state.craft.id,
          data: updateData,
        });
      } else {
        // Create new craft
        const createData: CraftCreate = {
          blueprint_id: state.blueprintId,
          ...(state.organizationId !== null && {
            organization_id: state.organizationId,
          }),
          output_location_id: state.outputLocationId,
          priority: state.priority,
          scheduled_start: state.scheduledStart || null,
        };
        await createMutation.mutateAsync(createData);
      }

      // Success - close modal and reset
      set({ isSubmitting: false });
      get().closeModal();
    } catch (err: unknown) {
      console.error("Failed to save craft:", err);
      set({
        error: "Failed to save craft. Please try again.",
        isSubmitting: false,
      });
    }
  },
}));
