/**
 * Register page component using Blueprint.js.
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { Button, Card, InputGroup, Intent, Callout, H1, H2 } from "@blueprintjs/core";
import { useRegister } from "../hooks/mutations/auth";
import { extractErrorMessage } from "../utils/errorHandler";
import { authPageContainer, authCard, inputGroupSpacing } from "../styles/common";
import { spacing, colors, typography } from "../styles/theme";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const registerMutation = useRegister();

  const handleRegister = () => {
    setValidationError(null);

    if (!email || !password || !confirmPassword) {
      setValidationError("Please fill in all required fields");
      return;
    }

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setValidationError("Password must be at least 8 characters long");
      return;
    }

    registerMutation.mutate({
      email,
      username: username || undefined,
      password,
    });
  };

  const errorMessage =
    validationError || (registerMutation.error ? extractErrorMessage(registerMutation.error) : null);

  const isFormValid = email && password && confirmPassword && password.length >= 8;

  return (
    <div style={authPageContainer}>
      <Card style={authCard}>
        <H1 style={{ marginBottom: spacing.lg, textAlign: "center" }}>SCIMS</H1>
        <H2 style={{ marginBottom: spacing.lg, textAlign: "center" }}>Register</H2>

        {errorMessage && (
          <Callout intent={Intent.DANGER} style={{ marginBottom: spacing.md }}>
            {errorMessage}
          </Callout>
        )}

        <div style={inputGroupSpacing}>
          <InputGroup
            large
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={registerMutation.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleRegister();
              }
            }}
          />
        </div>

        <div style={inputGroupSpacing}>
          <InputGroup
            large
            placeholder="Username (optional)"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={registerMutation.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleRegister();
              }
            }}
          />
        </div>

        <div style={inputGroupSpacing}>
          <InputGroup
            large
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={registerMutation.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleRegister();
              }
            }}
          />
        </div>

        <div style={{ marginBottom: spacing.lg }}>
          <InputGroup
            large
            placeholder="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={registerMutation.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleRegister();
              }
            }}
          />
        </div>

        <Button
          large
          intent={Intent.PRIMARY}
          text={registerMutation.isPending ? "Registering..." : "Register"}
          onClick={handleRegister}
          disabled={registerMutation.isPending || !isFormValid}
          fill
          loading={registerMutation.isPending}
        />

        <p
          style={{
            marginTop: spacing.lg,
            textAlign: "center",
            color: colors.text.secondary,
            fontSize: typography.fontSize.base,
          }}
        >
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </Card>
    </div>
  );
}
