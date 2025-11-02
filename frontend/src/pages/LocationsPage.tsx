/**
 * Locations management page component using Blueprint.js.
 */

import { useState } from "react";
import { InputGroup, H1, Callout, Intent, Spinner, HTMLSelect } from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useLocations } from "../hooks/queries/locations";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type { Location } from "../types";

export default function LocationsPage() {
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

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setSkip(0);
  };

  const handleTypeChange = (value: string) => {
    setTypeFilter(value);
    setSkip(0);
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
      key: "owner_type",
      label: "Owner Type",
      render: (location: Location) => location.owner_type,
    },
    {
      key: "is_canonical",
      label: "Canonical",
      render: (location: Location) => (location.is_canonical ? "Yes" : "No"),
    },
  ];

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.total / limit) : 1;

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Locations</H1>

      <div style={filterRow}>
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
          <option value="station">Station</option>
          <option value="ship">Ship</option>
          <option value="player_inventory">Player Inventory</option>
          <option value="warehouse">Warehouse</option>
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

