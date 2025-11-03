/**
 * Import/Export page component using Blueprint.js.
 */

import { useState } from "react";
import {
  H1,
  H3,
  Callout,
  Intent,
  Card,
  Button,
  HTMLSelect,
  FileInput,
  Divider,
  Pre,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { apiClient } from "../services";
import { pageHeader } from "../styles/common";
import { spacing } from "../styles/theme";
import type {
  ExportType,
  ExportFormat,
  ImportResponse,
} from "../types/import_export";

export default function ImportExportPage() {
  const [exportType, setExportType] = useState<ExportType>("items");
  const [exportFormat, setExportFormat] = useState<ExportFormat>("csv");
  const [exportCategory, setExportCategory] = useState("");
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const [importType, setImportType] = useState<ExportType>("items");
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState<ImportResponse | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  const handleExport = async () => {
    setExportLoading(true);
    setExportError(null);

    try {
      const filters: {
        category?: string;
      } = {};
      if (exportCategory) {
        filters.category = exportCategory;
      }

      const blob = await apiClient.importExport.exportData(
        exportType,
        exportFormat,
        filters
      );

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${exportType}_export.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setExportError(error instanceof Error ? error.message : "Export failed");
    } finally {
      setExportLoading(false);
    }
  };

  const handleImport = async () => {
    if (!importFile) {
      setImportError("Please select a file to import");
      return;
    }

    setImportLoading(true);
    setImportError(null);
    setImportResult(null);

    try {
      const result = await apiClient.importExport.importData(
        importType,
        importFile
      );
      setImportResult(result);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : "Import failed");
    } finally {
      setImportLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImportFile(file);
      setImportError(null);
    }
  };

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Import & Export</H1>

      {/* Export Section */}
      <Card style={{ marginBottom: spacing.lg }}>
        <H3 style={{ marginTop: 0 }}>Export Data</H3>
        <p style={{ marginBottom: spacing.md }}>
          Export your data to CSV or JSON format for backup or use in other
          tools.
        </p>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: spacing.md,
            maxWidth: "600px",
          }}
        >
          <div
            style={{ display: "flex", gap: spacing.sm, alignItems: "center" }}
          >
            <label style={{ minWidth: "100px" }}>Data Type:</label>
            <HTMLSelect
              value={exportType}
              onChange={(e) => setExportType(e.target.value as ExportType)}
            >
              <option value="items">Items</option>
              <option value="inventory">Inventory</option>
              <option value="blueprints">Blueprints</option>
            </HTMLSelect>
          </div>

          <div
            style={{ display: "flex", gap: spacing.sm, alignItems: "center" }}
          >
            <label style={{ minWidth: "100px" }}>Format:</label>
            <HTMLSelect
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as ExportFormat)}
            >
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </HTMLSelect>
          </div>

          {exportType === "items" && (
            <div
              style={{ display: "flex", gap: spacing.sm, alignItems: "center" }}
            >
              <label style={{ minWidth: "100px" }}>Category (optional):</label>
              <input
                type="text"
                value={exportCategory}
                onChange={(e) => setExportCategory(e.target.value)}
                placeholder="Filter by category"
                style={{ padding: "5px", flex: 1 }}
              />
            </div>
          )}

          <Button
            icon="download"
            text="Export"
            intent={Intent.PRIMARY}
            onClick={handleExport}
            loading={exportLoading}
          />

          {exportError && (
            <Callout intent={Intent.DANGER}>{exportError}</Callout>
          )}
        </div>
      </Card>

      <Divider />

      {/* Import Section */}
      <Card style={{ marginTop: spacing.lg }}>
        <H3 style={{ marginTop: 0 }}>Import Data</H3>
        <p style={{ marginBottom: spacing.md }}>
          Import data from CSV or JSON files. Files must match the export
          format.
        </p>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: spacing.md,
            maxWidth: "600px",
          }}
        >
          <div
            style={{ display: "flex", gap: spacing.sm, alignItems: "center" }}
          >
            <label style={{ minWidth: "100px" }}>Data Type:</label>
            <HTMLSelect
              value={importType}
              onChange={(e) => setImportType(e.target.value as ExportType)}
            >
              <option value="items">Items</option>
              <option value="inventory">Inventory</option>
              <option value="blueprints">Blueprints</option>
            </HTMLSelect>
          </div>

          <div
            style={{ display: "flex", gap: spacing.sm, alignItems: "center" }}
          >
            <label style={{ minWidth: "100px" }}>File:</label>
            <FileInput
              text={importFile?.name || "Choose file..."}
              onInputChange={handleFileChange}
              inputProps={{ accept: ".csv,.json" }}
              style={{ flex: 1 }}
            />
          </div>

          <Button
            icon="upload"
            text="Import"
            intent={Intent.PRIMARY}
            onClick={handleImport}
            loading={importLoading}
            disabled={!importFile}
          />

          {importError && (
            <Callout intent={Intent.DANGER}>{importError}</Callout>
          )}

          {importResult && (
            <div>
              <Callout
                intent={importResult.success ? Intent.SUCCESS : Intent.WARNING}
              >
                <div>
                  <p>
                    <strong>Result:</strong>{" "}
                    {importResult.success ? "Success" : "Completed with errors"}
                  </p>
                  <p>
                    <strong>Imported:</strong> {importResult.imported_count}{" "}
                    items
                  </p>
                  <p>
                    <strong>Failed:</strong> {importResult.failed_count} items
                  </p>
                  {importResult.errors.length > 0 && (
                    <div style={{ marginTop: spacing.md }}>
                      <strong>Errors:</strong>
                      <Pre
                        style={{
                          marginTop: spacing.sm,
                          fontSize: "0.9em",
                          maxHeight: "300px",
                          overflow: "auto",
                        }}
                      >
                        {JSON.stringify(importResult.errors, null, 2)}
                      </Pre>
                    </div>
                  )}
                </div>
              </Callout>
            </div>
          )}
        </div>
      </Card>
    </DashboardLayout>
  );
}
