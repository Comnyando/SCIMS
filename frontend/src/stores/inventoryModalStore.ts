/**
 * Zustand store for managing InventoryModal state.
 * Handles inventory adjustments and transfers.
 */

import { create } from "zustand";
import type {
  InventoryStock,
  InventoryAdjust,
  InventoryTransfer,
} from "../types/inventory";

export type InventoryModalAction = "adjust" | "transfer" | "view";

export interface InventoryModalFormState {
  // For adjust action
  itemId: string;
  locationId: string;
  quantityChange: string; // Decimal as string
  notes: string;

  // For transfer action
  fromLocationId: string;
  toLocationId: string;
  transferQuantity: string; // Decimal as string
  transferNotes: string;
}

interface InventoryModalStore extends InventoryModalFormState {
  // Modal state
  isOpen: boolean;
  action: InventoryModalAction;
  stock: InventoryStock | null;
  isSubmitting: boolean;
  error: string | null;

  // Actions
  openAdjustModal: (stock: InventoryStock) => void;
  openTransferModal: (stock: InventoryStock) => void;
  openViewModal: (stock: InventoryStock) => void;
  closeModal: () => void;
  resetForm: () => void;
  initializeFromStock: (
    stock: InventoryStock,
    action: InventoryModalAction
  ) => void;

  // Form field setters
  setItemId: (itemId: string) => void;
  setLocationId: (locationId: string) => void;
  setQuantityChange: (change: string) => void;
  setNotes: (notes: string) => void;
  setFromLocationId: (locationId: string) => void;
  setToLocationId: (locationId: string) => void;
  setTransferQuantity: (quantity: string) => void;
  setTransferNotes: (notes: string) => void;

  // Submission
  setSubmitting: (isSubmitting: boolean) => void;
  setError: (error: string | null) => void;
  handleAdjust: (
    adjustFn: (data: InventoryAdjust) => Promise<InventoryStock>
  ) => Promise<void>;
  handleTransfer: (
    transferFn: (data: InventoryTransfer) => Promise<{ message: string }>
  ) => Promise<void>;
}

const initialFormState: InventoryModalFormState = {
  itemId: "",
  locationId: "",
  quantityChange: "",
  notes: "",
  fromLocationId: "",
  toLocationId: "",
  transferQuantity: "",
  transferNotes: "",
};

export const useInventoryModalStore = create<InventoryModalStore>(
  (set, get) => ({
    ...initialFormState,

    // Modal state
    isOpen: false,
    action: "view",
    stock: null,
    isSubmitting: false,
    error: null,

    // Modal actions
    openAdjustModal: (stock: InventoryStock) => {
      get().initializeFromStock(stock, "adjust");
      set({ isOpen: true, action: "adjust" });
    },

    openTransferModal: (stock: InventoryStock) => {
      get().initializeFromStock(stock, "transfer");
      set({ isOpen: true, action: "transfer" });
    },

    openViewModal: (stock: InventoryStock) => {
      get().initializeFromStock(stock, "view");
      set({ isOpen: true, action: "view" });
    },

    closeModal: () => {
      set({
        isOpen: false,
        action: "view",
        stock: null,
        isSubmitting: false,
        error: null,
      });
      get().resetForm();
    },

    resetForm: () => {
      set(initialFormState);
    },

    initializeFromStock: (
      stock: InventoryStock,
      action: InventoryModalAction
    ) => {
      if (action === "adjust") {
        set({
          itemId: stock.item_id,
          locationId: stock.location_id,
          quantityChange: "",
          notes: "",
          stock,
        });
      } else if (action === "transfer") {
        set({
          itemId: stock.item_id,
          fromLocationId: stock.location_id,
          toLocationId: "",
          transferQuantity: "",
          transferNotes: "",
          stock,
        });
      } else {
        // view
        set({ stock });
      }
    },

    // Form field setters
    setItemId: (itemId) => set({ itemId }),
    setLocationId: (locationId) => set({ locationId }),
    setQuantityChange: (change) => set({ quantityChange: change }),
    setNotes: (notes) => set({ notes }),
    setFromLocationId: (locationId) => set({ fromLocationId: locationId }),
    setToLocationId: (locationId) => set({ toLocationId: locationId }),
    setTransferQuantity: (quantity) => set({ transferQuantity: quantity }),
    setTransferNotes: (notes) => set({ transferNotes: notes }),

    // Submission helpers
    setSubmitting: (isSubmitting) => set({ isSubmitting }),
    setError: (error) => set({ error }),

    handleAdjust: async (adjustFn) => {
      const state = get();
      set({ isSubmitting: true, error: null });

      try {
        const adjustData: InventoryAdjust = {
          item_id: state.itemId,
          location_id: state.locationId,
          quantity_change: state.quantityChange,
          ...(state.notes && { notes: state.notes }),
        };
        await adjustFn(adjustData);

        // Success - close modal and reset
        set({ isSubmitting: false });
        get().closeModal();
      } catch (err: unknown) {
        console.error("Failed to adjust inventory:", err);
        set({
          error: "Failed to adjust inventory. Please try again.",
          isSubmitting: false,
        });
      }
    },

    handleTransfer: async (transferFn) => {
      const state = get();
      set({ isSubmitting: true, error: null });

      try {
        const transferData: InventoryTransfer = {
          item_id: state.itemId,
          from_location_id: state.fromLocationId,
          to_location_id: state.toLocationId,
          quantity: state.transferQuantity,
          ...(state.transferNotes && { notes: state.transferNotes }),
        };
        await transferFn(transferData);

        // Success - close modal and reset
        set({ isSubmitting: false });
        get().closeModal();
      } catch (err: unknown) {
        console.error("Failed to transfer inventory:", err);
        set({
          error: "Failed to transfer inventory. Please try again.",
          isSubmitting: false,
        });
      }
    },
  })
);
