/**
 * Inventory view page component using Blueprint.js.
 */

import { useState } from "react";
import { InputGroup, H1, Callout, Intent, Spinner } from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useInventory } from "../hooks/queries/inventory";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors, typography } from "../styles/theme";
import type { InventoryStock } from "../types";

export default function InventoryPage() {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [search, setSearch] = useState("");
  const [itemIdFilter, setItemIdFilter] = useState("");
  const [locationIdFilter, setLocationIdFilter] = useState("");

  const { data, isLoading, error } = useInventory({
    skip,
    limit,
    item_id: itemIdFilter || undefined,
    location_id: locationIdFilter || undefined,
    search: search || undefined,
  });

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setSkip(0);
  };

  const handleItemIdChange = (value: string) => {
    setItemIdFilter(value);
    setSkip(0);
  };

  const handleLocationIdChange = (value: string) => {
    setLocationIdFilter(value);
    setSkip(0);
  };

  const columns = [
    {
      key: "item",
      label: "Item",
      render: (stock: InventoryStock) => (
        <div>
          <strong>{stock.item_name}</strong>
          {stock.item_category && (
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {stock.item_category}
            </div>
          )}
        </div>
      ),
    },
    {
      key: "location",
      label: "Location",
      render: (stock: InventoryStock) => (
        <div>
          <strong>{stock.location_name}</strong>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            {stock.location_type}
          </div>
        </div>
      ),
    },
    {
      key: "quantity",
      label: "Quantity",
      align: "right" as const,
      render: (stock: InventoryStock) => stock.quantity,
    },
    {
      key: "reserved",
      label: "Reserved",
      align: "right" as const,
      render: (stock: InventoryStock) => (
        <span style={{ color: "#FF9800" }}>{stock.reserved_quantity}</span>
      ),
    },
    {
      key: "available",
      label: "Available",
      align: "right" as const,
      render: (stock: InventoryStock) => (
        <span style={{ color: "#4CAF50" }}>{stock.available_quantity}</span>
      ),
    },
    {
      key: "last_updated",
      label: "Last Updated",
      render: (stock: InventoryStock) => (
        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            {new Date(stock.last_updated).toLocaleString()}
          </div>
          {stock.updated_by_username && (
            <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
              by {stock.updated_by_username}
            </div>
          )}
        </div>
      ),
    },
  ];

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.total / limit) : 1;

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Inventory</H1>

      <div style={filterRow}>
        <InputGroup
          large
          leftIcon="search"
          placeholder="Search by item name..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          style={{ flex: 1 }}
        />
        <InputGroup
          large
          leftIcon="cube"
          placeholder="Filter by item ID..."
          value={itemIdFilter}
          onChange={(e) => handleItemIdChange(e.target.value)}
          style={{ flex: 1 }}
        />
        <InputGroup
          large
          leftIcon="map-marker"
          placeholder="Filter by location ID..."
          value={locationIdFilter}
          onChange={(e) => handleLocationIdChange(e.target.value)}
          style={{ flex: 1 }}
        />
      </div>

      {isLoading && (
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      )}

      {error && (
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading inventory. Please try again.
        </Callout>
      )}

      {data && !isLoading && (
        <>
          <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
            Showing {data.items.length} of {data.total} inventory records
          </p>

          <DataTable
            columns={columns}
            data={data.items}
            emptyMessage="No inventory records found"
            keyExtractor={(stock) => `${stock.item_id}-${stock.location_id}`}
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

