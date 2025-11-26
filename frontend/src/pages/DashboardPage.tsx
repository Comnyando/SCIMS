/**
 * Dashboard page component using Blueprint.js.
 */

import { Card, H1, H3 } from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import TourButton from "../components/onboarding/TourButton";
import { useItems } from "../hooks/queries/items";
import { useLocations } from "../hooks/queries/locations";
import { useInventory } from "../hooks/queries/inventory";
import {
  spacing,
  colors,
  typography,
  shadows,
  borderRadius,
} from "../styles/theme";

export default function DashboardPage() {
  const { data: itemsData } = useItems({ skip: 0, limit: 5 });
  const { data: locationsData } = useLocations({ skip: 0, limit: 5 });
  const { data: inventoryData } = useInventory({ skip: 0, limit: 5 });

  const statCards = [
    {
      title: "Items",
      value: itemsData?.total ?? 0,
      description: "Total items in catalog",
      icon: "cube",
    },
    {
      title: "Locations",
      value: locationsData?.total ?? 0,
      description: "Total locations",
      icon: "map-marker",
    },
    {
      title: "Inventory Stock",
      value: inventoryData?.total ?? 0,
      description: "Active stock records",
      icon: "box",
    },
  ];

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
        <H1 style={{ margin: 0 }}>Dashboard</H1>
        <TourButton tourName="dashboard-tour" text="Take Tour" />
      </div>
      <p style={{ marginBottom: spacing.xl, color: colors.text.secondary }}>
        Welcome to the Star Citizen Inventory Management System
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: spacing.lg,
        }}
      >
        {statCards.map((card) => (
          <Card
            key={card.title}
            style={{
              backgroundColor: "var(--scims-background-primary)",
              borderRadius: borderRadius.lg,
              boxShadow: shadows.md,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: spacing.md,
              }}
            >
              <H3 style={{ margin: 0, flex: 1 }}>{card.title}</H3>
            </div>
            <p
              style={{
                fontSize: typography.fontSize["3xl"],
                margin: `${spacing.sm} 0`,
                fontWeight: typography.fontWeight.bold,
                color: colors.text.primary,
              }}
            >
              {card.value}
            </p>
            <p style={{ color: colors.text.secondary, margin: 0 }}>
              {card.description}
            </p>
          </Card>
        ))}
      </div>
    </DashboardLayout>
  );
}
