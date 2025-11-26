/**
 * Account Management page for user settings.
 * Allows users to change their password and delete their account.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  FormGroup,
  InputGroup,
  Button,
  Intent,
  Callout,
  H5,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../services";
import { useAlert } from "../hooks/useAlert";
import { spacing } from "../styles/theme";
import { themeStyles } from "../utils/theme";

export default function AccountManagementPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { showError, showSuccess, showConfirm } = useAlert();

  // Password change state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Account deletion state
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      showError("Error", "Please fill in all password fields.");
      return;
    }

    if (newPassword.length < 8) {
      showError("Error", "New password must be at least 8 characters long.");
      return;
    }

    if (newPassword !== confirmPassword) {
      showError("Error", "New password and confirmation do not match.");
      return;
    }

    if (currentPassword === newPassword) {
      showError(
        "Error",
        "New password must be different from current password."
      );
      return;
    }

    setIsChangingPassword(true);
    try {
      await apiClient.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      showSuccess("Success", "Password changed successfully.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      console.error("Failed to change password:", err);
      const errorMessage =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || "Failed to change password"
          : "Failed to change password. Please try again.";
      showError("Error", errorMessage);
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      showError(
        "Error",
        "Please enter your password to confirm account deletion."
      );
      return;
    }

    if (!deleteConfirm) {
      showError("Error", "Please check the confirmation box to proceed.");
      return;
    }

    const confirmed = await showConfirm({
      title: "Delete Account",
      message:
        "Are you absolutely sure you want to delete your account? This action cannot be undone and all your data will be permanently lost.",
      intent: Intent.DANGER,
      confirmText: "Delete Account",
      cancelText: "Cancel",
    });

    if (!confirmed) {
      return;
    }

    setIsDeletingAccount(true);
    try {
      await apiClient.deleteAccount({
        password: deletePassword,
        confirm: true,
      });
      showSuccess("Success", "Account deleted successfully.");
      logout();
      navigate("/login");
    } catch (err: unknown) {
      console.error("Failed to delete account:", err);
      const errorMessage =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || "Failed to delete account"
          : "Failed to delete account. Please try again.";
      showError("Error", errorMessage);
    } finally {
      setIsDeletingAccount(false);
    }
  };

  return (
    <DashboardLayout>
      <div>
        <H5 style={themeStyles.text.primary}>Account Management</H5>
        <p
          style={{
            ...themeStyles.text.secondary,
            marginBottom: spacing.lg,
          }}
        >
          Manage your account settings and preferences.
        </p>

        <Card
          style={{
            marginBottom: spacing.lg,
            ...themeStyles.background.primary,
          }}
        >
          <H5 style={themeStyles.text.primary}>Change Password</H5>
          <p
            style={{
              ...themeStyles.text.secondary,
              marginBottom: spacing.md,
            }}
          >
            Update your account password. Make sure to use a strong, unique
            password.
          </p>

          <FormGroup label="Current Password" labelInfo="(required)">
            <InputGroup
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="Enter current password"
              disabled={isChangingPassword}
              fill
            />
          </FormGroup>

          <FormGroup label="New Password" labelInfo="(required)">
            <InputGroup
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new password (min 8 characters)"
              disabled={isChangingPassword}
              fill
            />
          </FormGroup>

          <FormGroup label="Confirm New Password" labelInfo="(required)">
            <InputGroup
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
              disabled={isChangingPassword}
              fill
            />
          </FormGroup>

          <Button
            intent={Intent.PRIMARY}
            text="Change Password"
            onClick={handleChangePassword}
            disabled={isChangingPassword}
            loading={isChangingPassword}
          />
        </Card>

        <Card style={themeStyles.background.primary}>
          <H5 style={themeStyles.text.primary}>Delete Account</H5>
          <Callout intent={Intent.DANGER} style={{ marginBottom: spacing.md }}>
            <strong>Warning:</strong> Deleting your account is permanent and
            cannot be undone. All your data, including items, locations,
            blueprints, crafts, and goals will be permanently deleted.
          </Callout>

          <FormGroup label="Password" labelInfo="(required)">
            <InputGroup
              type="password"
              value={deletePassword}
              onChange={(e) => setDeletePassword(e.target.value)}
              placeholder="Enter your password to confirm"
              disabled={isDeletingAccount}
              fill
            />
          </FormGroup>

          <FormGroup>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: spacing.xs,
                ...themeStyles.text.primary,
              }}
            >
              <input
                type="checkbox"
                checked={deleteConfirm}
                onChange={(e) => setDeleteConfirm(e.target.checked)}
                disabled={isDeletingAccount}
              />
              <span>I understand that this action cannot be undone</span>
            </label>
          </FormGroup>

          <Button
            intent={Intent.DANGER}
            text="Delete Account"
            onClick={handleDeleteAccount}
            disabled={isDeletingAccount || !deletePassword || !deleteConfirm}
            loading={isDeletingAccount}
          />
        </Card>
      </div>
    </DashboardLayout>
  );
}
