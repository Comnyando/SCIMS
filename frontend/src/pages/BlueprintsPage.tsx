/**
 * Blueprints list page component using Blueprint.js.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  InputGroup,
  H1,
  Callout,
  Intent,
  Spinner,
  HTMLSelect,
  Button,
  Tag,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useBlueprints } from "../hooks/queries/blueprints";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow, sectionSpacing } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type { Blueprint } from "../types";

export default function BlueprintsPage() {
  const navigate = useNavigate();
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [isPublic, setIsPublic] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const { data, isLoading, error } = useBlueprints({
    skip,
    limit,
    search: search || undefined,
    category: category || undefined,
    is_public: isPublic === "" ? undefined : isPublic === "true",
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setSkip(0);
  };

  const handleCategoryChange = (value: string) => {
    setCategory(value);
    setSkip(0);
  };

  const handlePublicChange = (value: string) => {
    setIsPublic(value);
    setSkip(0);
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
    setSkip(0);
  };

  const handleSortOrderChange = (value: string) => {
    setSortOrder(value as "asc" | "desc");
    setSkip(0);
  };

  const handleBlueprintClick = (blueprint: Blueprint) => {
    navigate(`/blueprints/${blueprint.id}`);
  };

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (blueprint: Blueprint) => (
        <strong
          style={{ cursor: "pointer" }}
          onClick={() => handleBlueprintClick(blueprint)}
        >
          {blueprint.name}
        </strong>
      ),
    },
    {
      key: "category",
      label: "Category",
      render: (blueprint: Blueprint) => blueprint.category || "-",
    },
    {
      key: "crafting_time",
      label: "Crafting Time",
      render: (blueprint: Blueprint) => {
        const hours = Math.floor(blueprint.crafting_time_minutes / 60);
        const minutes = blueprint.crafting_time_minutes % 60;
        if (hours > 0) {
          return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
      },
    },
    {
      key: "ingredients",
      label: "Ingredients",
      render: (blueprint: Blueprint) =>
        blueprint.blueprint_data.ingredients.length || 0,
    },
    {
      key: "output",
      label: "Output",
      render: (blueprint: Blueprint) => `${blueprint.output_quantity}x`,
    },
    {
      key: "visibility",
      label: "Visibility",
      render: (blueprint: Blueprint) => (
        <Tag intent={blueprint.is_public ? "success" : "none"}>
          {blueprint.is_public ? "Public" : "Private"}
        </Tag>
      ),
    },
    {
      key: "usage",
      label: "Used",
      render: (blueprint: Blueprint) => blueprint.usage_count || 0,
    },
  ];

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.total / limit) : 1;

  return (
    <DashboardLayout>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: spacing.lg,
        }}
      >
        <H1 style={pageHeader}>Blueprints</H1>
        <Button
          icon="plus"
          text="Create Blueprint"
          intent="primary"
          onClick={() => navigate("/blueprints/new")}
        />
      </div>

      {error && (
        <Callout intent={Intent.DANGER} style={sectionSpacing}>
          Error loading blueprints:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </Callout>
      )}

      <div style={filterRow}>
        <InputGroup
          leftIcon="search"
          placeholder="Search blueprints..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          style={{ flex: 1, maxWidth: "300px" }}
        />
        <HTMLSelect
          value={category}
          onChange={(e) => handleCategoryChange(e.target.value)}
          style={{ marginLeft: spacing.md }}
        >
          <option value="">All Categories</option>
          <option value="Weapons">Weapons</option>
          <option value="Components">Components</option>
          <option value="Food">Food</option>
          <option value="Materials">Materials</option>
          <option value="Other">Other</option>
        </HTMLSelect>
        <HTMLSelect
          value={isPublic}
          onChange={(e) => handlePublicChange(e.target.value)}
          style={{ marginLeft: spacing.md }}
        >
          <option value="">All Visibility</option>
          <option value="true">Public</option>
          <option value="false">Private</option>
        </HTMLSelect>
        <HTMLSelect
          value={sortBy}
          onChange={(e) => handleSortChange(e.target.value)}
          style={{ marginLeft: spacing.md }}
        >
          <option value="name">Sort by Name</option>
          <option value="usage_count">Sort by Usage</option>
          <option value="created_at">Sort by Created</option>
        </HTMLSelect>
        <HTMLSelect
          value={sortOrder}
          onChange={(e) => handleSortOrderChange(e.target.value)}
          style={{ marginLeft: spacing.sm }}
        >
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </HTMLSelect>
      </div>

      {isLoading ? (
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      ) : data && data?.items?.length > 0 ? (
        <>
          <p style={{ color: colors.text.secondary, marginBottom: spacing.md }}>
            Showing {data.items.length} of {data.total} blueprints
          </p>
          <DataTable
            columns={columns}
            data={data.items}
            emptyMessage="No blueprints found"
            keyExtractor={(blueprint) => blueprint.id}
          />
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPrevious={() => setSkip(Math.max(0, skip - limit))}
              onNext={() => setSkip(skip + limit)}
              hasPrevious={skip > 0}
              hasNext={skip + limit < (data?.total || 0)}
            />
          )}
        </>
      ) : (
        <Callout intent={Intent.WARNING} style={sectionSpacing}>
          No blueprints found.{" "}
          {search || category || isPublic
            ? "Try adjusting your filters."
            : "Create your first blueprint!"}
        </Callout>
      )}
    </DashboardLayout>
  );
}
