/**
 * Zustand store for managing ItemModal state.
 * Handles both modal visibility and form data.
 */

import { create } from "zustand";
import type { UseMutationResult } from "@tanstack/react-query";
import type { Item, ItemCreate, ItemUpdate } from "../types/item";

export interface ItemModalFormState {
  // Form fields
  name: string;
  description: string;
  category: string;
  subcategory: string;
  rarity: string;
  metadataJson: string;
}

interface ItemModalStore extends ItemModalFormState {
  // Modal state
  isOpen: boolean;
  mode: "view" | "edit" | "create";
  item: Item | null;
  isSubmitting: boolean;
  error: string | null;

  // Actions
  openCreateModal: () => void;
  openViewModal: (item: Item) => void;
  openEditModal: (item: Item) => void;
  switchToEditMode: () => void;
  closeModal: () => void;
  resetForm: () => void;
  initializeFromItem: (item: Item) => void;
  initializeForNew: () => void;

  // Form field setters
  setName: (name: string) => void;
  setDescription: (description: string) => void;
  setCategory: (category: string) => void;
  setSubcategory: (subcategory: string) => void;
  setRarity: (rarity: string) => void;
  setMetadataJson: (json: string) => void;

  // Submission
  setSubmitting: (isSubmitting: boolean) => void;
  setError: (error: string | null) => void;
  handleSubmit: (
    createMutation: UseMutationResult<Item, Error, ItemCreate, unknown>,
    updateMutation: UseMutationResult<
      Item,
      Error,
      { id: string; data: ItemUpdate },
      unknown
    >
  ) => Promise<void>;
}

const initialFormState: ItemModalFormState = {
  name: "",
  description: "",
  category: "",
  subcategory: "",
  rarity: "",
  metadataJson: "",
};

export const useItemModalStore = create<ItemModalStore>((set, get) => ({
  ...initialFormState,

  // Modal state
  isOpen: false,
  mode: "create",
  item: null,
  isSubmitting: false,
  error: null,

  // Modal actions
  openCreateModal: () => {
    get().initializeForNew();
    set({ isOpen: true, mode: "create" });
  },

  openViewModal: (item: Item) => {
    get().initializeFromItem(item);
    set({ isOpen: true, mode: "view", item });
  },

  openEditModal: (item: Item) => {
    get().initializeFromItem(item);
    set({ isOpen: true, mode: "edit", item });
  },

  switchToEditMode: () => {
    set({ mode: "edit" });
  },

  closeModal: () => {
    set({
      isOpen: false,
      mode: "create",
      item: null,
      isSubmitting: false,
      error: null,
    });
    get().resetForm();
  },

  resetForm: () => {
    set(initialFormState);
  },

  initializeFromItem: (item: Item) => {
    set({
      name: item.name,
      description: item.description || "",
      category: item.category || "",
      subcategory: item.subcategory || "",
      rarity: item.rarity || "",
      metadataJson: item.metadata ? JSON.stringify(item.metadata, null, 2) : "",
    });
  },

  initializeForNew: () => {
    set({
      ...initialFormState,
      item: null,
    });
  },

  // Form field setters
  setName: (name) => set({ name }),
  setDescription: (description) => set({ description }),
  setCategory: (category) => set({ category }),
  setSubcategory: (subcategory) => set({ subcategory }),
  setRarity: (rarity) => set({ rarity }),
  setMetadataJson: (json) => set({ metadataJson: json }),

  // Submission helpers
  setSubmitting: (isSubmitting) => set({ isSubmitting }),
  setError: (error) => set({ error }),

  handleSubmit: async (createMutation, updateMutation) => {
    const state = get();
    set({ isSubmitting: true, error: null });

    try {
      // Parse metadata JSON if provided
      let metadata: Record<string, unknown> | undefined = undefined;
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

      if (state.item) {
        // Update existing item
        const updateData: ItemUpdate = {
          name: state.name,
          ...(state.description && { description: state.description }),
          ...(state.category && { category: state.category }),
          ...(state.subcategory && { subcategory: state.subcategory }),
          ...(state.rarity && { rarity: state.rarity }),
          ...(metadata && Object.keys(metadata).length > 0 && { metadata }),
        };
        await updateMutation.mutateAsync({
          id: state.item.id,
          data: updateData,
        });
      } else {
        // Create new item
        const createData: ItemCreate = {
          name: state.name,
          ...(state.description && { description: state.description }),
          ...(state.category && { category: state.category }),
          ...(state.subcategory && { subcategory: state.subcategory }),
          ...(state.rarity && { rarity: state.rarity }),
          ...(metadata && Object.keys(metadata).length > 0 && { metadata }),
        };
        await createMutation.mutateAsync(createData);
      }

      // Success - close modal and reset
      set({ isSubmitting: false });
      get().closeModal();
    } catch (err: unknown) {
      console.error("Failed to save item:", err);
      set({
        error: "Failed to save item. Please try again.",
        isSubmitting: false,
      });
    }
  },
}));
