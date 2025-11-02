/**
 * Optimization settings page component.
 * Allows users to configure optimization preferences and defaults.
 */

import { useState } from "react";
import {
  H1,
  H3,
  Card,
  Divider,
  FormGroup,
  NumericInput,
  Switch,
  Button,
  Callout,
  Intent,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { pageHeader } from "../styles/common";
import { spacing, colors } from "../styles/theme";

interface OptimizationSettings {
  // Source finding defaults
  defaultMaxSources: number;
  defaultIncludePlayerStocks: boolean;
  defaultMinReliability: number;

  // Craft suggestions defaults
  defaultMaxSuggestions: number;

  // Display preferences
  autoRefreshGaps: boolean;
  gapRefreshInterval: number; // seconds

  // Cost preferences
  preferOwnStock: boolean;
  preferLowerCost: boolean;
  preferHigherReliability: boolean;
}

const DEFAULT_SETTINGS: OptimizationSettings = {
  defaultMaxSources: 10,
  defaultIncludePlayerStocks: true,
  defaultMinReliability: 0.5,
  defaultMaxSuggestions: 10,
  autoRefreshGaps: true,
  gapRefreshInterval: 10,
  preferOwnStock: true,
  preferLowerCost: true,
  preferHigherReliability: false,
};

export default function OptimizationSettingsPage() {
  const [settings, setSettings] = useState<OptimizationSettings>(() => {
    // Load from localStorage or use defaults
    const saved = localStorage.getItem("optimizationSettings");
    return saved
      ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) }
      : DEFAULT_SETTINGS;
  });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem("optimizationSettings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    localStorage.removeItem("optimizationSettings");
  };

  const updateSetting = <K extends keyof OptimizationSettings>(
    key: K,
    value: OptimizationSettings[K]
  ) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <DashboardLayout>
      <div style={pageHeader}>
        <H1>Optimization Settings</H1>
        <p style={{ color: colors.text.secondary, marginTop: spacing.sm }}>
          Configure default preferences for source finding, craft suggestions,
          and resource gap analysis.
        </p>
      </div>

      {saved && (
        <Callout
          intent={Intent.SUCCESS}
          icon="tick-circle"
          style={{ marginBottom: spacing.lg }}
        >
          Settings saved successfully!
        </Callout>
      )}

      <div
        style={{
          display: "flex",
          gap: spacing.lg,
          justifyContent: "flex-end",
          marginBottom: spacing.lg,
        }}
      >
        <Button text="Reset to Defaults" onClick={handleReset} />
        <Button
          intent={Intent.PRIMARY}
          text="Save Settings"
          icon="floppy-disk"
          onClick={handleSave}
        />
      </div>

      {/* Source Finding Settings */}
      <Card style={{ marginBottom: spacing.lg }}>
        <H3>Source Finding Defaults</H3>
        <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
        <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
          Default settings when finding sources for items.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: spacing.lg,
          }}
        >
          <FormGroup
            label="Maximum Sources to Return"
            labelInfo="(1-50)"
            helperText="Maximum number of source options to display"
          >
            <NumericInput
              value={settings.defaultMaxSources}
              onValueChange={(value) =>
                updateSetting(
                  "defaultMaxSources",
                  Math.max(1, Math.min(50, value || 10))
                )
              }
              min={1}
              max={50}
              majorStepSize={5}
              minorStepSize={1}
            />
          </FormGroup>

          <FormGroup
            label="Minimum Reliability Score"
            labelInfo="(0.0-1.0)"
            helperText="Filter out sources below this reliability threshold"
          >
            <NumericInput
              value={settings.defaultMinReliability}
              onValueChange={(value) =>
                updateSetting(
                  "defaultMinReliability",
                  Math.max(0, Math.min(1, value || 0.5))
                )
              }
              min={0}
              max={1}
              stepSize={0.1}
              majorStepSize={0.1}
              minorStepSize={0.05}
            />
          </FormGroup>
        </div>

        <FormGroup
          label="Include Player Stocks by Default"
          helperText="When enabled, player stock sources will be included in source searches"
        >
          <Switch
            checked={settings.defaultIncludePlayerStocks}
            onChange={(e) =>
              updateSetting(
                "defaultIncludePlayerStocks",
                e.currentTarget.checked
              )
            }
            label="Include player stocks in source searches"
          />
        </FormGroup>
      </Card>

      {/* Craft Suggestions Settings */}
      <Card style={{ marginBottom: spacing.lg }}>
        <H3>Craft Suggestions Defaults</H3>
        <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
        <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
          Default settings when getting craft suggestions for target items.
        </p>

        <FormGroup
          label="Maximum Suggestions to Return"
          labelInfo="(1-20)"
          helperText="Maximum number of blueprint suggestions to display"
        >
          <NumericInput
            value={settings.defaultMaxSuggestions}
            onValueChange={(value) =>
              updateSetting(
                "defaultMaxSuggestions",
                Math.max(1, Math.min(20, value || 10))
              )
            }
            min={1}
            max={20}
            majorStepSize={5}
            minorStepSize={1}
          />
        </FormGroup>
      </Card>

      {/* Display Preferences */}
      <Card style={{ marginBottom: spacing.lg }}>
        <H3>Display Preferences</H3>
        <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
        <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
          Configure how optimization data is displayed and refreshed.
        </p>

        <FormGroup
          label="Auto-refresh Resource Gaps"
          helperText="Automatically refresh resource gap analysis for planned crafts"
        >
          <Switch
            checked={settings.autoRefreshGaps}
            onChange={(e) =>
              updateSetting("autoRefreshGaps", e.currentTarget.checked)
            }
            label="Enable automatic gap refresh"
          />
        </FormGroup>

        {settings.autoRefreshGaps && (
          <FormGroup
            label="Refresh Interval"
            labelInfo="(seconds)"
            helperText="How often to refresh resource gap data (5-60 seconds)"
          >
            <NumericInput
              value={settings.gapRefreshInterval}
              onValueChange={(value) =>
                updateSetting(
                  "gapRefreshInterval",
                  Math.max(5, Math.min(60, value || 10))
                )
              }
              min={5}
              max={60}
              majorStepSize={10}
              minorStepSize={5}
            />
          </FormGroup>
        )}
      </Card>

      {/* Prioritization Preferences */}
      <Card style={{ marginBottom: spacing.lg }}>
        <H3>Source Prioritization</H3>
        <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
        <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
          Choose how sources should be prioritized when multiple options are
          available. These preferences influence the sorting order of source
          results.
        </p>

        <div
          style={{ display: "flex", flexDirection: "column", gap: spacing.md }}
        >
          <FormGroup helperText="Always prioritize your own stock over external sources">
            <Switch
              checked={settings.preferOwnStock}
              onChange={(e) =>
                updateSetting("preferOwnStock", e.currentTarget.checked)
              }
              label="Prefer Own Stock"
              disabled
            />
            <div
              style={{
                fontSize: "0.85em",
                color: colors.text.secondary,
                marginTop: spacing.xs,
              }}
            >
              Note: Own stock is always shown first regardless of this setting
            </div>
          </FormGroup>

          <FormGroup helperText="Prioritize sources with lower cost per unit">
            <Switch
              checked={settings.preferLowerCost}
              onChange={(e) =>
                updateSetting("preferLowerCost", e.currentTarget.checked)
              }
              label="Prioritize Lower Cost"
            />
          </FormGroup>

          <FormGroup helperText="Prioritize sources with higher reliability scores">
            <Switch
              checked={settings.preferHigherReliability}
              onChange={(e) =>
                updateSetting(
                  "preferHigherReliability",
                  e.currentTarget.checked
                )
              }
              label="Prioritize Higher Reliability"
            />
          </FormGroup>

          <Callout
            intent={Intent.NONE}
            icon="info-sign"
            style={{ marginTop: spacing.sm }}
          >
            <strong>Prioritization Order:</strong> Sources are sorted by: Own
            stock (always first) → Cost
            {settings.preferLowerCost ? " (ascending)" : ""} → Reliability{" "}
            {settings.preferHigherReliability ? " (descending)" : ""}. These
            settings help determine the order when costs are equal.
          </Callout>
        </div>
      </Card>

      {/* Information Section */}
      <Card>
        <H3>About Optimization Settings</H3>
        <Divider style={{ margin: `${spacing.sm} 0 ${spacing.md} 0` }} />
        <div style={{ color: colors.text.secondary }}>
          <p>
            These settings are stored locally in your browser and apply as
            defaults when using optimization features. You can override these
            settings on a per-request basis when finding sources or getting
            craft suggestions.
          </p>
          <p style={{ marginTop: spacing.sm }}>Settings affect:</p>
          <ul style={{ marginTop: spacing.xs, paddingLeft: spacing.lg }}>
            <li>Default parameters for source finding queries</li>
            <li>Default parameters for craft suggestion queries</li>
            <li>Resource gap analysis refresh behavior</li>
            <li>Source prioritization and sorting preferences</li>
          </ul>
        </div>
      </Card>
    </DashboardLayout>
  );
}
