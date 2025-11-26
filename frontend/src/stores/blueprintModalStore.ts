/**
 * Zustand store for managing BlueprintModal state.
 * Handles both modal visibility and form data.
 */

import { create } from "zustand";
import type { UseMutationResult } from "@tanstack/react-query";
import type {
  Blueprint,
  BlueprintCreate,
  BlueprintUpdate,
  BlueprintIngredient,
} from "../types/blueprint";

export interface BlueprintModalFormState {
  // Form fields
  name: string;
  description: string;
  category: string;
  craftingTimeMinutes: number; // Total minutes (for API)
  craftingTimeHours: number; // For UI input
  craftingTimeMinutesInput: number; // For UI input (0-59)
  craftingTimeSeconds: number; // For UI input (0-59)
  outputItemId: string;
  outputItemSearch: string; // Search value for output item
  outputQuantity: number;
  ingredients: BlueprintIngredient[];
  isPublic: boolean;
}

interface BlueprintModalStore extends BlueprintModalFormState {
  // Modal state
  isOpen: boolean;
  mode: "view" | "edit" | "create";
  blueprint: Blueprint | null;
  isSubmitting: boolean;
  error: string | null;

  // Actions
  openCreateModal: () => void;
  openViewModal: (blueprint: Blueprint) => void;
  openEditModal: (blueprint: Blueprint) => void;
  switchToEditMode: () => void;
  closeModal: () => void;
  resetForm: () => void;
  initializeFromBlueprint: (blueprint: Blueprint) => void;
  initializeForNew: () => void;

  // Form field setters
  setName: (name: string) => void;
  setDescription: (description: string) => void;
  setCategory: (category: string) => void;
  setCraftingTimeMinutes: (minutes: number) => void;
  setCraftingTimeHours: (hours: number) => void;
  setCraftingTimeMinutesInput: (minutes: number) => void;
  setCraftingTimeSeconds: (seconds: number) => void;
  setOutputItemId: (itemId: string) => void;
  setOutputItemSearch: (search: string) => void;
  setOutputQuantity: (quantity: number) => void;
  setIsPublic: (isPublic: boolean) => void;

  // Ingredient management
  addIngredient: () => void;
  removeIngredient: (index: number) => void;
  updateIngredient: (
    index: number,
    field: keyof BlueprintIngredient,
    value: string | number | boolean
  ) => void;

  // Submission
  setSubmitting: (isSubmitting: boolean) => void;
  setError: (error: string | null) => void;
  handleSubmit: (
    createMutation: UseMutationResult<
      Blueprint,
      Error,
      BlueprintCreate,
      unknown
    >,
    updateMutation: UseMutationResult<
      Blueprint,
      Error,
      { id: string; data: BlueprintUpdate },
      unknown
    >
  ) => Promise<void>;
}

const initialFormState: BlueprintModalFormState = {
  name: "",
  description: "",
  category: "",
  craftingTimeMinutes: 0,
  craftingTimeHours: 0,
  craftingTimeMinutesInput: 0,
  craftingTimeSeconds: 0,
  outputItemId: "",
  outputItemSearch: "",
  outputQuantity: 1,
  ingredients: [],
  isPublic: false,
};

// Helper function to convert hours/minutes/seconds to total minutes
const convertToTotalMinutes = (
  hours: number,
  minutes: number,
  seconds: number
): number => {
  return hours * 60 + minutes + seconds / 60;
};

// Helper function to convert total minutes to hours/minutes/seconds
const convertFromTotalMinutes = (
  totalMinutes: number
): {
  hours: number;
  minutes: number;
  seconds: number;
} => {
  const totalSeconds = Math.floor(totalMinutes * 60);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return { hours, minutes, seconds };
};

export const useBlueprintModalStore = create<BlueprintModalStore>(
  (set, get) => ({
    ...initialFormState,

    // Modal state
    isOpen: false,
    mode: "create",
    blueprint: null,
    isSubmitting: false,
    error: null,

    // Modal actions
    openCreateModal: () => {
      get().initializeForNew();
      set({ isOpen: true, mode: "create" });
    },

    openViewModal: (blueprint: Blueprint) => {
      get().initializeFromBlueprint(blueprint);
      set({ isOpen: true, mode: "view", blueprint });
    },

    openEditModal: (blueprint: Blueprint) => {
      get().initializeFromBlueprint(blueprint);
      set({ isOpen: true, mode: "edit", blueprint });
    },

    switchToEditMode: () => {
      set({ mode: "edit" });
    },

    closeModal: () => {
      set({
        isOpen: false,
        mode: "create",
        blueprint: null,
        isSubmitting: false,
        error: null,
      });
      get().resetForm();
    },

    resetForm: () => {
      set(initialFormState);
    },

    initializeFromBlueprint: (blueprint: Blueprint) => {
      const timeComponents = convertFromTotalMinutes(
        blueprint.crafting_time_minutes
      );
      set({
        name: blueprint.name,
        description: blueprint.description || "",
        category: blueprint.category || "",
        craftingTimeMinutes: blueprint.crafting_time_minutes,
        craftingTimeHours: timeComponents.hours,
        craftingTimeMinutesInput: timeComponents.minutes,
        craftingTimeSeconds: timeComponents.seconds,
        outputItemId: blueprint.output_item_id,
        outputItemSearch: "", // Will be populated by modal when items load
        outputQuantity: blueprint.output_quantity,
        ingredients: blueprint.blueprint_data?.ingredients || [],
        isPublic: blueprint.is_public,
      });
    },

    initializeForNew: () => {
      set({
        ...initialFormState,
        blueprint: null,
      });
    },

    // Form field setters
    setName: (name) => set({ name }),
    setDescription: (description) => set({ description }),
    setCategory: (category) => set({ category }),
    setCraftingTimeMinutes: (minutes) => set({ craftingTimeMinutes: minutes }),
    setCraftingTimeHours: (hours) => {
      const state = get();
      const totalMinutes = convertToTotalMinutes(
        hours,
        state.craftingTimeMinutesInput,
        state.craftingTimeSeconds
      );
      set({ craftingTimeHours: hours, craftingTimeMinutes: totalMinutes });
    },
    setCraftingTimeMinutesInput: (minutes) => {
      const state = get();
      const totalMinutes = convertToTotalMinutes(
        state.craftingTimeHours,
        minutes,
        state.craftingTimeSeconds
      );
      set({
        craftingTimeMinutesInput: minutes,
        craftingTimeMinutes: totalMinutes,
      });
    },
    setCraftingTimeSeconds: (seconds) => {
      const state = get();
      const totalMinutes = convertToTotalMinutes(
        state.craftingTimeHours,
        state.craftingTimeMinutesInput,
        seconds
      );
      set({ craftingTimeSeconds: seconds, craftingTimeMinutes: totalMinutes });
    },
    setOutputItemId: (itemId) => set({ outputItemId: itemId }),
    setOutputItemSearch: (search) => set({ outputItemSearch: search }),
    setOutputQuantity: (quantity) => set({ outputQuantity: quantity }),
    setIsPublic: (isPublic) => set({ isPublic }),

    // Ingredient management
    addIngredient: () => {
      const current = get().ingredients;
      set({
        ingredients: [
          ...current,
          { item_id: "", quantity: 1, optional: false },
        ],
      });
    },

    removeIngredient: (index: number) => {
      const current = get().ingredients;
      set({
        ingredients: current.filter((_, i) => i !== index),
      });
    },

    updateIngredient: (
      index: number,
      field: keyof BlueprintIngredient,
      value: string | number | boolean
    ) => {
      const current = get().ingredients;
      const updated = [...current];
      updated[index] = { ...updated[index], [field]: value };
      set({ ingredients: updated });
    },

    // Submission helpers
    setSubmitting: (isSubmitting) => set({ isSubmitting }),
    setError: (error) => set({ error }),

    handleSubmit: async (createMutation, updateMutation) => {
      const state = get();
      set({ isSubmitting: true, error: null });

      try {
        // Validate that no placeholder IDs are present
        if (state.outputItemId && state.outputItemId.startsWith("__new__")) {
          throw new Error(
            "Please wait for the item to be created before submitting."
          );
        }

        // Validate ingredients don't have placeholder IDs
        const invalidIngredients = state.ingredients.filter(
          (ing) => ing.item_id && ing.item_id.startsWith("__new__")
        );
        if (invalidIngredients.length > 0) {
          throw new Error(
            "Please wait for all items to be created before submitting."
          );
        }
        // Filter out empty ingredients
        const validIngredients = state.ingredients.filter(
          (ing) => ing.item_id !== ""
        );

        if (state.blueprint) {
          // Update existing blueprint
          const updateData: BlueprintUpdate = {
            name: state.name,
            ...(state.description && { description: state.description }),
            ...(state.category && { category: state.category }),
            crafting_time_minutes: state.craftingTimeMinutes,
            output_item_id: state.outputItemId,
            output_quantity: state.outputQuantity,
            blueprint_data: {
              ingredients: validIngredients,
            },
            is_public: state.isPublic,
          };
          await updateMutation.mutateAsync({
            id: state.blueprint.id,
            data: updateData,
          });
        } else {
          // Create new blueprint
          const createData: BlueprintCreate = {
            name: state.name,
            ...(state.description && { description: state.description }),
            ...(state.category && { category: state.category }),
            crafting_time_minutes: state.craftingTimeMinutes,
            output_item_id: state.outputItemId,
            output_quantity: state.outputQuantity,
            blueprint_data: {
              ingredients: validIngredients,
            },
            is_public: state.isPublic,
          };
          await createMutation.mutateAsync(createData);
        }

        // Success - wait a moment for query invalidation/refetch to complete
        // This ensures the new blueprint appears in the list
        await new Promise((resolve) => setTimeout(resolve, 100));

        // Close modal and reset
        set({ isSubmitting: false });
        get().closeModal();
      } catch (err: unknown) {
        console.error("Failed to save blueprint:", err);
        set({
          error: "Failed to save blueprint. Please try again.",
          isSubmitting: false,
        });
      }
    },
  })
);
