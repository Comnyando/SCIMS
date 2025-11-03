/**
 * Public Entities Manager page component using Blueprint.js.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  H1,
  Callout,
  Intent,
  Spinner,
  HTMLSelect,
  InputGroup,
  Button,
  Tag,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  usePublicItems,
  usePublicRecipes,
  usePublicLocations,
  useTags,
} from "../hooks/queries/commons";
import DataTable from "../components/common/DataTable";
import Pagination from "../components/common/Pagination";
import { pageHeader, filterRow } from "../styles/common";
import { spacing } from "../styles/theme";
import type { CommonsEntityResponse } from "../types/commons";

const ENTITY_TYPE_OPTIONS = [
  { value: "item", label: "Items" },
  { value: "recipe", label: "Recipes (Blueprints)" },
  { value: "location", label: "Locations" },
];

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

function formatEntityData(data: Record<string, unknown>): string {
  const name = data.name || data.title || "Unknown";
  return String(name);
}

export default function PublicEntitiesPage() {
  const navigate = useNavigate();
  const [entityType, setEntityType] = useState<"item" | "recipe" | "location">(
    "item"
  );
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [search, setSearch] = useState("");
  const [selectedTag, setSelectedTag] = useState<string>("");

  const { data: itemsData, isLoading: isLoadingItems } = usePublicItems({
    skip: entityType === "item" ? skip : 0,
    limit: entityType === "item" ? limit : 50,
    search: entityType === "item" && search ? search : undefined,
    tag: entityType === "item" && selectedTag ? selectedTag : undefined,
  });

  const { data: recipesData, isLoading: isLoadingRecipes } = usePublicRecipes({
    skip: entityType === "recipe" ? skip : 0,
    limit: entityType === "recipe" ? limit : 50,
    search: entityType === "recipe" && search ? search : undefined,
    tag: entityType === "recipe" && selectedTag ? selectedTag : undefined,
  });

  const { data: locationsData, isLoading: isLoadingLocations } =
    usePublicLocations({
      skip: entityType === "location" ? skip : 0,
      limit: entityType === "location" ? limit : 50,
      search: entityType === "location" && search ? search : undefined,
      tag: entityType === "location" && selectedTag ? selectedTag : undefined,
    });

  const { data: tagsData } = useTags();

  const currentData =
    entityType === "item"
      ? itemsData
      : entityType === "recipe"
      ? recipesData
      : locationsData;

  const isLoading =
    (entityType === "item" && isLoadingItems) ||
    (entityType === "recipe" && isLoadingRecipes) ||
    (entityType === "location" && isLoadingLocations);

  const handleEntityTypeChange = (value: string) => {
    setEntityType(value as "item" | "recipe" | "location");
    setSkip(0);
    setSearch("");
    setSelectedTag("");
  };

  const handleSearch = () => {
    setSkip(0);
  };

  const handleEntityClick = (entity: CommonsEntityResponse) => {
    const typePath = entityType === "recipe" ? "recipe" : entityType;
    navigate(`/commons/public/${typePath}/${entity.id}`);
  };

  const handlePageChange = (newSkip: number) => {
    setSkip(newSkip);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (entity: CommonsEntityResponse) => formatEntityData(entity.data),
    },
    {
      key: "version",
      label: "Version",
      render: (entity: CommonsEntityResponse) => <Tag>v{entity.version}</Tag>,
    },
    {
      key: "tags",
      label: "Tags",
      render: (entity: CommonsEntityResponse) => (
        <div style={{ display: "flex", gap: spacing.xs, flexWrap: "wrap" }}>
          {entity.tags && entity.tags.length > 0
            ? entity.tags.map((tag) => (
                <Tag key={tag} minimal>
                  {tag}
                </Tag>
              ))
            : "-"}
        </div>
      ),
    },
    {
      key: "created_at",
      label: "Published",
      render: (entity: CommonsEntityResponse) => formatDate(entity.created_at),
    },
    {
      key: "actions",
      label: "Actions",
      render: (entity: CommonsEntityResponse) => (
        <Button
          small
          text="View"
          onClick={() => handleEntityClick(entity)}
          intent={Intent.PRIMARY}
        />
      ),
    },
  ];

  const totalPages = currentData?.pages || 0;
  const currentPage = Math.floor(skip / limit) + 1;
  const hasPrevious = skip > 0;
  const hasNext = skip + limit < (currentData?.total || 0);

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>Public Commons Entities</H1>

      <div style={filterRow}>
        <div style={{ display: "flex", gap: spacing.md, alignItems: "center" }}>
          <label style={{ minWidth: "100px" }}>Type:</label>
          <HTMLSelect
            value={entityType}
            onChange={(e) => handleEntityTypeChange(e.target.value)}
            options={ENTITY_TYPE_OPTIONS.map((opt) => ({
              value: opt.value,
              label: opt.label,
            }))}
          />
        </div>

        <div
          style={{
            display: "flex",
            gap: spacing.md,
            alignItems: "center",
            flex: 1,
          }}
        >
          <InputGroup
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            leftIcon="search"
            rightElement={
              <Button
                icon="arrow-right"
                minimal
                onClick={handleSearch}
                disabled={!search}
              />
            }
          />
        </div>

        {tagsData && tagsData.tags.length > 0 && (
          <div
            style={{ display: "flex", gap: spacing.md, alignItems: "center" }}
          >
            <label style={{ minWidth: "80px" }}>Tag:</label>
            <HTMLSelect
              value={selectedTag}
              onChange={(e) => {
                setSelectedTag(e.target.value);
                setSkip(0);
              }}
            >
              <option value="">All Tags</option>
              {tagsData.tags.map((tag) => (
                <option key={tag.id} value={tag.name}>
                  {tag.name}
                </option>
              ))}
            </HTMLSelect>
          </div>
        )}

        <div>
          <Tag>Total: {currentData?.total || 0}</Tag>
        </div>
      </div>

      {isLoading ? (
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      ) : currentData && currentData.entities.length > 0 ? (
        <>
          <DataTable
            data={currentData.entities}
            columns={columns}
            keyExtractor={(entity) => entity.id}
          />
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPrevious={() => handlePageChange(Math.max(0, skip - limit))}
              onNext={() => handlePageChange(skip + limit)}
              hasPrevious={hasPrevious}
              hasNext={hasNext}
            />
          )}
        </>
      ) : (
        <Callout intent={Intent.NONE} style={{ marginTop: spacing.lg }}>
          No public entities found.
        </Callout>
      )}
    </DashboardLayout>
  );
}
