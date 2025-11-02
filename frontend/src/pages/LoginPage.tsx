/**
 * Login page component using Blueprint.js.
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { Button, Card, InputGroup, Intent, Callout, H1, H2 } from "@blueprintjs/core";
import { useLogin } from "../hooks/mutations/auth";
import { extractErrorMessage } from "../utils/errorHandler";
import { authPageContainer, authCard, inputGroupSpacing } from "../styles/common";
import { spacing, colors, typography } from "../styles/theme";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const loginMutation = useLogin();

  const handleLogin = () => {
    if (!email || !password) {
      return;
    }
    loginMutation.mutate({ email, password });
  };

  const errorMessage = loginMutation.error ? extractErrorMessage(loginMutation.error) : null;

  return (
    <div style={authPageContainer}>
      <Card style={authCard}>
        <H1 style={{ marginBottom: spacing.lg, textAlign: "center" }}>SCIMS</H1>
        <H2 style={{ marginBottom: spacing.lg, textAlign: "center" }}>Login</H2>

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
            disabled={loginMutation.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleLogin();
              }
            }}
          />
        </div>

        <div style={{ marginBottom: spacing.lg }}>
          <InputGroup
            large
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loginMutation.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleLogin();
              }
            }}
          />
        </div>

        <Button
          large
          intent={Intent.PRIMARY}
          text={loginMutation.isPending ? "Logging in..." : "Login"}
          onClick={handleLogin}
          disabled={loginMutation.isPending || !email || !password}
          fill
          loading={loginMutation.isPending}
        />

        <p
          style={{
            marginTop: spacing.lg,
            textAlign: "center",
            color: colors.text.secondary,
            fontSize: typography.fontSize.base,
          }}
        >
          Don't have an account? <Link to="/register">Register here</Link>
        </p>
      </Card>
    </div>
  );
}
