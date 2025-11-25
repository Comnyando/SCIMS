/**
 * Locations management page component using Blueprint.js.
 */

import { useState } from "react";
import {
  InputGroup,
  H1,
  Callout,
  Intent,
  Spinner,
  HTMLSelect,
  Button,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useLocations } from "../hooks/queries/locations";
import { useDeleteLocation } from "../hooks/mutations/locations";
import { useDeleteCanonicalLocation } from "../hooks/mutations/canonical_locations";
import { useLocationModalStore } from "../stores/locationModalStore";
import { useAlert } from "../hooks/useAlert";
import { useAdmin } from "../hooks/useAdmin";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import { LocationType } from "../types/enums";
import type { Location } from "../types";
import { apiClient } from "../services";

export default function LocationsPage() {
  const openCreateModal = useLocationModalStore(
    (state) => state.openCreateModal
  );
  const openEditModal = useLocationModalStore((state) => state.openEditModal);
  const { showConfirm, showError } = useAlert();
  const { isAdmin } = useAdmin();
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const { data, isLoading, error } = useLocations({
    skip,
    limit,
    type: typeFilter || undefined,
    search: search || undefined,
  });

  const deleteMutation = useDeleteLocation();
  const deleteCanonicalMutation = useDeleteCanonicalLocation();

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setSkip(0);
  };

  const handleTypeChange = (value: string) => {
    setTypeFilter(value);
    setSkip(0);
  };

  const handleCreateClick = () => {
    // TODO: Get organization ID from user's organizations
    openCreateModal(undefined);
  };

  const handleEditClick = (location: Location) => {
    openEditModal(location);
  };

  const handleDeleteClick = async (location: Location) => {
    const locationType = location.is_canonical
      ? "canonical location"
      : "location";
    const confirmMessage = location.is_canonical
      ? `Delete canonical location "${location.name}"? This action cannot be undone and may affect locations that reference it.`
      : `Delete location "${location.name}"? This action cannot be undone.`;

    const confirmed = await showConfirm({
      title: `Delete ${locationType}`,
      message: confirmMessage,
      intent: Intent.DANGER,
      confirmText: "Delete",
      cancelText: "Cancel",
    });

    if (!confirmed) {
      return;
    }

    try {
      if (location.is_canonical) {
        await deleteCanonicalMutation.mutateAsync(location.id);
      } else {
        await deleteMutation.mutateAsync(location.id);
      }
    } catch (err: unknown) {
      console.error(`Failed to delete ${locationType}:`, err);
      const errorMessage =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || `Failed to delete ${locationType}`
          : `Failed to delete ${locationType}. Please try again.`;
      await showError("Delete Failed", errorMessage);
    }
  };

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (location: Location) => <strong>{location.name}</strong>,
    },
    {
      key: "type",
      label: "Type",
      render: (location: Location) => location.type,
    },
    {
      key: "parent_location",
      label: "Parent Location",
      render: (location: Location) =>
        location.parent_location_name || (
          <span style={{ color: colors.text.muted }}>—</span>
        ),
    },
    {
      key: "child_locations",
      label: "Child Locations",
      render: (location: Location) => {
        if (location.child_locations.length === 0) {
          return <span style={{ color: colors.text.muted }}>—</span>;
        }
        return (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: spacing.xs,
            }}
          >
            {location.child_locations.map((child) => (
              <Button
                key={child.id}
                icon="chevron-right"
                text={child.name}
                onClick={async () => {
                  // Fetch the full location data and open edit modal
                  try {
                    const response = await apiClient.locations.getLocation(
                      child.id
                    );
                    openEditModal(response);
                  } catch (error) {
                    console.error("Failed to fetch child location:", error);
                    showError(
                      "Error",
                      `Failed to load location "${child.name}". Please try again.`
                    );
                  }
                }}
                style={{
                  textAlign: "left",
                  justifyContent: "flex-start",
                  cursor: "pointer",
                }}
                title={`Click to edit ${child.name}`}
              />
            ))}
          </div>
        );
      },
    },
    {
      key: "owner_type",
      label: "Owner Type",
      render: (location: Location) => location.owner_type,
    },
    {
      key: "is_canonical",
      label: "Canonical",
      render: (location: Location) => (location.is_canonical ? "Yes" : "No"),
    },
    {
      key: "actions",
      label: "Actions",
      render: (location: Location) => {
        // Canonical locations can only be edited/deleted by admins
        const isCanonical = location.is_canonical;

        return (
          <div style={{ display: "flex", gap: spacing.xs }}>
            <Button
              small
              icon="edit"
              text="Edit"
              onClick={() => handleEditClick(location)}
              intent={Intent.PRIMARY}
              disabled={isCanonical && !isAdmin}
              title={
                isCanonical && !isAdmin
                  ? "Canonical locations can only be edited by admins"
                  : undefined
              }
            />
            <Button
              small
              icon="trash"
              text="Delete"
              onClick={() => handleDeleteClick(location)}
              intent={Intent.DANGER}
              disabled={
                deleteMutation.isPending ||
                deleteCanonicalMutation.isPending ||
                (isCanonical && !isAdmin)
              }
              title={
                isCanonical && !isAdmin
                  ? "Canonical locations can only be deleted by admins"
                  : undefined
              }
            />
          </div>
        );
      },
    },
  ];

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.total / limit) : 1;

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Locations</H1>

      <div style={filterRow}>
        <Button
          icon="add"
          text="Create Location"
          intent={Intent.PRIMARY}
          onClick={handleCreateClick}
          large
        />
        <InputGroup
          large
          leftIcon="search"
          placeholder="Search locations..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          style={{ flex: 1 }}
        />
        <HTMLSelect
          large
          value={typeFilter}
          onChange={(e) => handleTypeChange(e.target.value)}
          style={{ flex: 1, minWidth: "200px" }}
        >
          <option value="">All Types</option>
          <option value={LocationType.STATION}>Station</option>
          <option value={LocationType.SHIP}>Ship</option>
          <option value={LocationType.PLAYER_INVENTORY}>
            Player Inventory
          </option>
          <option value={LocationType.WAREHOUSE}>Warehouse</option>
        </HTMLSelect>
      </div>

      {isLoading && (
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      )}

      {error && (
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading locations. Please try again.
        </Callout>
      )}

      {data?.locations && !isLoading && (
        <>
          <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
            Showing {data.locations.length} of {data.total} locations
          </p>

          <DataTable
            columns={columns}
            data={data.locations}
            emptyMessage="No locations found"
            keyExtractor={(location) => location.id}
          />

          {data.total > limit && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPrevious={() => setSkip(Math.max(0, skip - limit))}
              onNext={() => setSkip(skip + limit)}
              hasPrevious={skip > 0}
              hasNext={skip + limit < data.total}
            />
          )}
        </>
      )}
    </DashboardLayout>
  );
}
