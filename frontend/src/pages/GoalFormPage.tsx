/**
 * Goal creation/edit form page component using Blueprint.js.
 */

import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  H1,
  H3,
  Callout,
  Intent,
  Spinner,
  Button,
  FormGroup,
  InputGroup,
  HTMLSelect,
  NumericInput,
  Card,
  TextArea,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import { useItems } from "../hooks/queries/items";
import { useCreateGoal, useUpdateGoal, useGoal } from "../hooks/queries/goals";
import { pageHeader } from "../styles/common";
import { spacing } from "../styles/theme";
import type { GoalCreate, GoalUpdate, GoalItemCreate } from "../types/goal";

export default function GoalFormPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;

  const { data: itemsData } = useItems({ skip: 0, limit: 1000 });
  const { data: existingGoal, isLoading: isLoadingGoal } = useGoal({
    id: id || "",
    enabled: isEdit,
  });
  const createGoal = useCreateGoal();
  const updateGoal = useUpdateGoal();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [organizationId, setOrganizationId] = useState<string>("");
  const [goalItems, setGoalItems] = useState<GoalItemCreate[]>([
    { item_id: "", target_quantity: 0 },
  ]);
  const [targetDate, setTargetDate] = useState("");

  // Load existing goal data when editing
  useEffect(() => {
    if (existingGoal) {
      setName(existingGoal.name);
      setDescription(existingGoal.description || "");
      setOrganizationId(existingGoal.organization_id || "");
      setGoalItems(
        existingGoal.goal_items.length > 0
          ? existingGoal.goal_items.map((gi) => ({
              item_id: gi.item_id,
              target_quantity: gi.target_quantity,
            }))
          : [{ item_id: "", target_quantity: 0 }]
      );
      setTargetDate(
        existingGoal.target_date
          ? new Date(existingGoal.target_date).toISOString().slice(0, 16)
          : ""
      );
    }
  }, [existingGoal]);

  const handleAddItem = () => {
    setGoalItems([...goalItems, { item_id: "", target_quantity: 0 }]);
  };

  const handleRemoveItem = (index: number) => {
    if (goalItems.length > 1) {
      setGoalItems(goalItems.filter((_, i) => i !== index));
    }
  };

  const handleItemChange = (
    index: number,
    field: "item_id" | "target_quantity",
    value: string | number
  ) => {
    const updated = [...goalItems];
    updated[index] = { ...updated[index], [field]: value };
    setGoalItems(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate that all items have valid item_id and quantity > 0
    const validItems = goalItems.filter(
      (item) => item.item_id && item.target_quantity > 0
    );

    if (!name || validItems.length === 0) {
      return;
    }

    const goalData = {
      name,
      description: description || null,
      organization_id: organizationId || null,
      goal_items: validItems,
      target_date: targetDate ? new Date(targetDate).toISOString() : null,
    };

    if (isEdit && id) {
      try {
        const result = await updateGoal.mutateAsync({
          id,
          data: goalData as GoalUpdate,
        });
        navigate(`/goals/${result.id}`);
      } catch (error) {
        console.error("Failed to update goal:", error);
      }
    } else {
      try {
        const result = await createGoal.mutateAsync(goalData as GoalCreate);
        navigate(`/goals/${result.id}`);
      } catch (error) {
        console.error("Failed to create goal:", error);
      }
    }
  };

  const isSaving = createGoal.isPending || updateGoal.isPending;

  if (isEdit && isLoadingGoal) {
    return (
      <DashboardLayout>
        <div style={{ textAlign: "center", padding: spacing.xl }}>
          <Spinner size={50} />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <H1 style={pageHeader}>{isEdit ? "Edit Goal" : "Create Goal"}</H1>

      <form onSubmit={handleSubmit}>
        <Card style={{ marginBottom: spacing.lg }}>
          <FormGroup label="Goal Name" labelFor="name">
            <InputGroup
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter goal name"
              required
            />
          </FormGroup>

          <FormGroup label="Description" labelFor="description">
            <TextArea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter goal description (optional)"
              rows={3}
              fill
            />
          </FormGroup>

          <FormGroup label="Organization" labelFor="organization">
            <InputGroup
              id="organization"
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              placeholder="Organization UUID (optional, leave empty for personal goal)"
              fill
            />
          </FormGroup>

          <div style={{ marginBottom: spacing.lg }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: spacing.md,
              }}
            >
              <H3 style={{ margin: 0 }}>Goal Items</H3>
              <Button
                icon="plus"
                text="Add Item"
                intent="primary"
                onClick={handleAddItem}
              />
            </div>

            {goalItems.map((item, index) => (
              <Card
                key={index}
                style={{
                  marginBottom: spacing.md,
                  padding: spacing.md,
                  position: "relative",
                }}
              >
                {goalItems.length > 1 && (
                  <Button
                    icon="cross"
                    minimal
                    small
                    intent="danger"
                    style={{
                      position: "absolute",
                      top: spacing.xs,
                      right: spacing.xs,
                    }}
                    onClick={() => handleRemoveItem(index)}
                  />
                )}
                <FormGroup
                  label={`Item ${index + 1}`}
                  labelFor={`item-${index}`}
                >
                  <HTMLSelect
                    id={`item-${index}`}
                    value={item.item_id}
                    onChange={(e) =>
                      handleItemChange(index, "item_id", e.target.value)
                    }
                    fill
                    required
                  >
                    <option value="">Select an item</option>
                    {itemsData?.items.map((itemOption) => (
                      <option key={itemOption.id} value={itemOption.id}>
                        {itemOption.name}{" "}
                        {itemOption.category ? `(${itemOption.category})` : ""}
                      </option>
                    ))}
                  </HTMLSelect>
                </FormGroup>
                <FormGroup
                  label="Target Quantity"
                  labelFor={`quantity-${index}`}
                >
                  <NumericInput
                    id={`quantity-${index}`}
                    value={item.target_quantity}
                    onValueChange={(value) =>
                      handleItemChange(index, "target_quantity", value || 0)
                    }
                    min={0.001}
                    stepSize={1}
                    majorStepSize={10}
                    fill
                    required
                  />
                </FormGroup>
              </Card>
            ))}
          </div>

          <FormGroup label="Target Date" labelFor="targetDate">
            <InputGroup
              id="targetDate"
              type="datetime-local"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              fill
            />
          </FormGroup>
        </Card>

        {(createGoal.error || updateGoal.error) && (
          <Callout intent={Intent.DANGER} style={{ marginBottom: spacing.md }}>
            Error:{" "}
            {createGoal.error?.message ||
              updateGoal.error?.message ||
              "Unknown error"}
          </Callout>
        )}

        <div style={{ display: "flex", gap: spacing.md }}>
          <Button
            type="submit"
            intent="primary"
            text={isEdit ? "Update Goal" : "Create Goal"}
            loading={isSaving}
            disabled={
              !name ||
              goalItems.filter(
                (item) => item.item_id && item.target_quantity > 0
              ).length === 0
            }
          />
          <Button
            text="Cancel"
            onClick={() => navigate("/goals")}
            disabled={isSaving}
          />
        </div>
      </form>
    </DashboardLayout>
  );
}
