/**
 * Zustand store for managing alerts and confirmations.
 * Provides a centralized way to show alerts and confirmation dialogs.
 */

import { create } from "zustand";
import { Intent } from "@blueprintjs/core";

export interface AlertState {
  isOpen: boolean;
  title: string;
  message: string;
  intent: Intent;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

interface AlertStore {
  // Alert state
  alert: AlertState;

  // Actions
  showAlert: (config: {
    title: string;
    message: string;
    intent?: Intent;
    confirmText?: string;
  }) => Promise<void>;

  showConfirm: (config: {
    title: string;
    message: string;
    intent?: Intent;
    confirmText?: string;
    cancelText?: string;
  }) => Promise<boolean>;

  closeAlert: () => void;
  handleConfirm: () => void;
  handleCancel: () => void;
}

const initialAlertState: AlertState = {
  isOpen: false,
  title: "",
  message: "",
  intent: Intent.PRIMARY,
  confirmText: "OK",
  cancelText: "Cancel",
};

export const useAlertStore = create<AlertStore>((set, get) => ({
  alert: initialAlertState,

  showAlert: async (config) => {
    return new Promise<void>((resolve) => {
      set({
        alert: {
          isOpen: true,
          title: config.title,
          message: config.message,
          intent: config.intent || Intent.PRIMARY,
          confirmText: config.confirmText || "OK",
          onConfirm: () => {
            get().closeAlert();
            resolve();
          },
        },
      });
    });
  },

  showConfirm: async (config) => {
    return new Promise<boolean>((resolve) => {
      set({
        alert: {
          isOpen: true,
          title: config.title,
          message: config.message,
          intent: config.intent || Intent.WARNING,
          confirmText: config.confirmText || "Confirm",
          cancelText: config.cancelText || "Cancel",
          onConfirm: () => {
            get().closeAlert();
            resolve(true);
          },
          onCancel: () => {
            get().closeAlert();
            resolve(false);
          },
        },
      });
    });
  },

  closeAlert: () => {
    set({
      alert: {
        ...initialAlertState,
        isOpen: false,
      },
    });
  },

  handleConfirm: () => {
    const { onConfirm } = get().alert;
    if (onConfirm) {
      onConfirm();
    } else {
      get().closeAlert();
    }
  },

  handleCancel: () => {
    const { onCancel } = get().alert;
    if (onCancel) {
      onCancel();
    } else {
      get().closeAlert();
    }
  },
}));
