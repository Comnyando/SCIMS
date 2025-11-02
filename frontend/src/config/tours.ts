/**
 * Tour step definitions for onboarding and guided tours.
 *
 * These steps can be used with a tour library like react-joyride when implemented.
 */

export interface TourStep {
  target: string; // CSS selector or element ID
  content: string;
  title?: string;
  placement?: "top" | "bottom" | "left" | "right" | "center";
  disableBeacon?: boolean;
}

export const craftingTourSteps: TourStep[] = [
  {
    target: '[data-tour="crafts-page-header"]',
    title: "Welcome to Crafts Management",
    content:
      "The Crafts page shows all your active and planned crafting operations. From here you can create new crafts, monitor progress, and manage your crafting queue.",
    placement: "bottom",
  },
  {
    target: '[data-tour="create-craft-button"]',
    title: "Create a New Craft",
    content:
      "Click this button to create a new craft from an existing blueprint. You'll be able to select the blueprint, set the output location, and configure priority.",
    placement: "left",
  },
  {
    target: '[data-tour="craft-status-filter"]',
    title: "Filter by Status",
    content:
      "Use this filter to view crafts by their current status: Planned, In Progress, Completed, or Cancelled. This helps you focus on specific craft types.",
    placement: "bottom",
  },
  {
    target: '[data-tour="craft-sort"]',
    title: "Sort Your Queue",
    content:
      "Sort crafts by priority, creation date, start date, or scheduled time. This helps you organize your crafting workflow based on what's most important.",
    placement: "bottom",
  },
  {
    target: '[data-tour="craft-list"]',
    title: "Craft Queue",
    content:
      "Your crafts are displayed here with key information: blueprint name, status, priority, and progress. Click any craft to view details and manage it.",
    placement: "top",
  },
];

export const craftCreationTourSteps: TourStep[] = [
  {
    target: '[data-tour="blueprint-select"]',
    title: "Select a Blueprint",
    content:
      "Choose the blueprint you want to craft from. The preview below will show you the ingredients, output, and crafting time once selected.",
    placement: "bottom",
  },
  {
    target: '[data-tour="blueprint-preview"]',
    title: "Blueprint Preview",
    content:
      "Review the blueprint details including required ingredients, output items, and crafting time. Make sure you have the necessary materials before proceeding.",
    placement: "top",
  },
  {
    target: '[data-tour="output-location"]',
    title: "Choose Output Location",
    content:
      "Select where the crafted items will be placed when the craft completes. This can be any location you have access to (station, ship, warehouse).",
    placement: "bottom",
  },
  {
    target: '[data-tour="priority-input"]',
    title: "Set Priority",
    content:
      "Set a priority from 0-100. Higher priority crafts appear first in your queue. Use this to organize multiple crafts by importance.",
    placement: "bottom",
  },
  {
    target: '[data-tour="reserve-ingredients"]',
    title: "Reserve Ingredients",
    content:
      "Enable this option to immediately reserve the required ingredients. This ensures the materials are available when you start the craft. You can also reserve later when starting the craft.",
    placement: "top",
  },
  {
    target: '[data-tour="create-button"]',
    title: "Create Craft",
    content:
      "Click this button to create the craft and add it to your queue. The craft will start in 'Planned' status and you can start it when ready.",
    placement: "top",
  },
];

export const craftDetailTourSteps: TourStep[] = [
  {
    target: '[data-tour="craft-status"]',
    title: "Craft Status",
    content:
      "The current status of your craft: Planned (not started), In Progress (currently crafting), Completed (finished), or Cancelled.",
    placement: "bottom",
  },
  {
    target: '[data-tour="craft-progress"]',
    title: "Progress Tracking",
    content:
      "For in-progress crafts, you'll see a progress bar showing completion percentage, elapsed time, and estimated time remaining. Progress updates automatically.",
    placement: "top",
  },
  {
    target: '[data-tour="craft-actions"]',
    title: "Craft Actions",
    content:
      "Depending on the craft status, you can start planned crafts, complete in-progress crafts manually, or delete planned crafts. Actions are context-sensitive.",
    placement: "left",
  },
  {
    target: '[data-tour="ingredients-list"]',
    title: "Ingredient Status",
    content:
      "View the status of each required ingredient: Pending (not reserved), Reserved (stock set aside), or Fulfilled (used in the craft).",
    placement: "top",
  },
  {
    target: '[data-tour="craft-timeline"]',
    title: "Craft Timeline",
    content:
      "See when the craft was created, scheduled, started, and completed. This helps you track the full lifecycle of your crafting operations.",
    placement: "right",
  },
];

// Combined full crafting workflow tour
export const fullCraftingWorkflowTourSteps: TourStep[] = [
  ...craftingTourSteps.slice(0, 2), // Introduction and create button
  ...craftCreationTourSteps, // Craft creation process
  ...craftDetailTourSteps.slice(0, 2), // Viewing and progress
];
