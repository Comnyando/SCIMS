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
  Menu,
  MenuItem,
  Popover,
} from "@blueprintjs/core";
import { useAuth } from "../contexts/AuthContext";
import { useThemeStore } from "../stores/themeStore";
import { spacing } from "../styles/theme";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { preference, effectiveTheme, setPreference } = useThemeStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Navigation groups
  const managementItems = [
    { path: "/items", label: "Items", icon: "cube" as const },
    { path: "/locations", label: "Locations", icon: "map-marker" as const },
    { path: "/inventory", label: "Inventory", icon: "box" as const },
    { path: "/admin/tags", label: "Tags", icon: "tag" as const },
  ];

  const craftingItems = [
    { path: "/blueprints", label: "Blueprints", icon: "build" as const },
    { path: "/crafts", label: "Crafts", icon: "projects" as const },
  ];

  const toolsItems = [
    {
      path: "/integrations",
      label: "Integrations",
      icon: "git-merge" as const,
    },
    {
      path: "/import-export",
      label: "Import/Export",
      icon: "exchange" as const,
    },
    {
      path: "/commons/my-submissions",
      label: "My Submissions",
      icon: "document" as const,
    },
    {
      path: "/commons/public",
      label: "Public Commons",
      icon: "globe" as const,
    },
  ];

  const isActive = (path: string) => location.pathname === path;
  const isGroupActive = (items: Array<{ path: string }>) =>
    items.some((item) => isActive(item.path));

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "var(--scims-background-secondary)",
      }}
    >
      <Navbar>
        <NavbarGroup align={Alignment.LEFT}>
          <NavbarHeading>SCIMS</NavbarHeading>
          <NavbarGroup>
            <Link to="/dashboard">
              <Button
                minimal
                icon="dashboard"
                text="Dashboard"
                active={isActive("/dashboard")}
                intent={isActive("/dashboard") ? "primary" : "none"}
              />
            </Link>
            <Popover
              content={
                <Menu>
                  {managementItems.map((item) => (
                    <Link key={item.path} to={item.path}>
                      <MenuItem
                        icon={item.icon}
                        text={item.label}
                        active={isActive(item.path)}
                      />
                    </Link>
                  ))}
                </Menu>
              }
              placement="bottom-start"
            >
              <Button
                minimal
                icon="layers"
                text="Management"
                active={isGroupActive(managementItems)}
                intent={isGroupActive(managementItems) ? "primary" : "none"}
                rightIcon="caret-down"
              />
            </Popover>
            <Popover
              content={
                <Menu>
                  {craftingItems.map((item) => (
                    <Link key={item.path} to={item.path}>
                      <MenuItem
                        icon={item.icon}
                        text={item.label}
                        active={isActive(item.path)}
                      />
                    </Link>
                  ))}
                </Menu>
              }
              placement="bottom-start"
            >
              <Button
                variant="minimal"
                icon="build"
                text="Crafting"
                active={isGroupActive(craftingItems)}
                intent={isGroupActive(craftingItems) ? "primary" : "none"}
                rightIcon="caret-down"
              />
            </Popover>
            <Link to="/goals">
              <Button
                variant="minimal"
                icon="target"
                text="Goals"
                active={isActive("/goals")}
                intent={isActive("/goals") ? "primary" : "none"}
              />
            </Link>
            <Link to="/analytics/dashboard">
              <Button
                variant="minimal"
                icon="timeline-bar-chart"
                text="Analytics"
                active={isActive("/analytics/dashboard")}
                intent={isActive("/analytics/dashboard") ? "primary" : "none"}
              />
            </Link>
            <Popover
              content={
                <Menu>
                  {toolsItems.map((item) => (
                    <Link key={item.path} to={item.path}>
                      <MenuItem
                        icon={item.icon}
                        text={item.label}
                        active={isActive(item.path)}
                      />
                    </Link>
                  ))}
                </Menu>
              }
              placement="bottom-start"
            >
              <Button
                minimal
                icon="wrench"
                text="Tools"
                active={isGroupActive(toolsItems)}
                intent={isGroupActive(toolsItems) ? "primary" : "none"}
                rightIcon="caret-down"
              />
            </Popover>
            <Link to="/admin/commons/submissions">
              <Button
                minimal
                icon="clipboard"
                text="Moderation"
                active={isActive("/admin/commons/submissions")}
                intent={
                  isActive("/admin/commons/submissions") ? "primary" : "none"
                }
              />
            </Link>
          </NavbarGroup>
        </NavbarGroup>
        <NavbarGroup align={Alignment.END}>
          <Popover
            content={
              <Menu>
                <MenuItem
                  icon={preference === "light" ? "tick" : undefined}
                  text="Light"
                  onClick={() => setPreference("light")}
                />
                <MenuItem
                  icon={preference === "dark" ? "tick" : undefined}
                  text="Dark"
                  onClick={() => setPreference("dark")}
                />
                <MenuItem
                  icon={preference === "system" ? "tick" : undefined}
                  text="System"
                  onClick={() => setPreference("system")}
                />
              </Menu>
            }
            placement="bottom-end"
          >
            <Button
              icon={effectiveTheme === "dark" ? "moon" : "flash"}
              text={effectiveTheme === "dark" ? "Dark" : "Light"}
              minimal
              title="Theme settings"
            />
          </Popover>
          <Link to="/account">
            <Button
              icon="cog"
              text="Settings"
              minimal
              title="Account settings"
            />
          </Link>
          <span
            style={{
              marginRight: spacing.md,
              color: "var(--scims-text-primary)",
            }}
          >
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
