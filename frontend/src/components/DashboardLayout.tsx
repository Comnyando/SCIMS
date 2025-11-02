/**
 * Dashboard layout component with navigation using Blueprint.js.
 */

import { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Navbar,
  NavbarGroup,
  NavbarHeading,
  Button,
  Alignment,
} from "@blueprintjs/core";
import { useAuth } from "../contexts/AuthContext";
import { spacing, colors } from "../styles/theme";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: "dashboard" as const },
    { path: "/items", label: "Items", icon: "cube" as const },
    { path: "/locations", label: "Locations", icon: "map-marker" as const },
    { path: "/inventory", label: "Inventory", icon: "box" as const },
    { path: "/blueprints", label: "Blueprints", icon: "build" as const },
    { path: "/crafts", label: "Crafts", icon: "projects" as const },
    { path: "/goals", label: "Goals", icon: "target" as const },
    {
      path: "/analytics",
      label: "Analytics",
      icon: "timeline-bar-chart" as const,
    },
  ];

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: colors.background.secondary,
      }}
    >
      <Navbar>
        <NavbarGroup align={Alignment.LEFT}>
          <NavbarHeading>SCIMS</NavbarHeading>
          <NavbarGroup>
            {navItems.map((item) => (
              <Link key={item.path} to={item.path}>
                <Button
                  minimal
                  icon={item.icon}
                  text={item.label}
                  active={location.pathname === item.path}
                  intent={location.pathname === item.path ? "primary" : "none"}
                />
              </Link>
            ))}
          </NavbarGroup>
        </NavbarGroup>
        <NavbarGroup align={Alignment.RIGHT}>
          <span style={{ marginRight: spacing.md, color: colors.text.primary }}>
            {user?.username || user?.email}
          </span>
          <Button
            icon="log-out"
            text="Logout"
            intent="danger"
            onClick={handleLogout}
          />
        </NavbarGroup>
      </Navbar>
      <main
        style={{ padding: spacing.xl, maxWidth: "1400px", margin: "0 auto" }}
      >
        {children}
      </main>
    </div>
  );
}
