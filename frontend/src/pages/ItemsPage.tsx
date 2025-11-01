/**
 * Items list page component using Blueprint.js.
 */

import { useState } from "react";
import { InputGroup, H1, Callout, Intent, Spinner } from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useItems } from "../hooks/queries/items";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type { Item } from "../types";

export default function ItemsPage() {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const { data, isLoading, error } = useItems({
    skip,
    limit,
    search: search || undefined,
    category: category || undefined,
  });

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setSkip(0);
  };

  const handleCategoryChange = (value: string) => {
    setCategory(value);
    setSkip(0);
  };

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (item: Item) => <strong>{item.name}</strong>,
    },
    {
      key: "category",
      label: "Category",
      render: (item: Item) => item.category || "-",
    },
    {
      key: "rarity",
      label: "Rarity",
      render: (item: Item) => item.rarity || "-",
    },
    {
      key: "description",
      label: "Description",
      render: (item: Item) => (
        <span style={{ color: colors.text.secondary }}>{item.description || "-"}</span>
      ),
    },
  ];

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.total / limit) : 1;

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Items</H1>

      <div style={filterRow}>
        <InputGroup
          leftIcon="search"
          placeholder="Search items..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          style={{ flex: 1 }}
        />
        <InputGroup
          leftIcon="filter"
          placeholder="Filter by category..."
          value={category}
          onChange={(e) => handleCategoryChange(e.target.value)}
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
          Error loading items. Please try again.
        </Callout>
      )}

      {data && !isLoading && (
        <>
          <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
            Showing {data.items.length} of {data.total} items
          </p>

          <DataTable
            columns={columns}
            data={data.items}
            emptyMessage="No items found"
            keyExtractor={(item) => item.id}
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

