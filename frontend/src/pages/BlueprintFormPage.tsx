/**
 * Blueprint create/edit form page component using Blueprint.js.
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  H1,
  H3,
  Callout,
  Intent,
  Spinner,
  Button,
  FormGroup,
  InputGroup,
  TextArea,
  HTMLSelect,
  NumericInput,
  Switch,
  Card,
  Divider,
} from "@blueprintjs/core";
import DashboardLayout from "../components/DashboardLayout";
import {
  useBlueprint,
  useCreateBlueprint,
  useUpdateBlueprint,
} from "../hooks/queries/blueprints";
import { useItems } from "../hooks/queries/items";
import { pageHeader } from "../styles/common";
import { spacing, colors } from "../styles/theme";
import type {
  BlueprintIngredient,
  BlueprintCreate,
  BlueprintUpdate,
} from "../types/blueprint";

export default function BlueprintFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditMode = !!id;

  const { data: blueprint, isLoading: isLoadingBlueprint } = useBlueprint({
    id: id || "",
    enabled: isEditMode,
  });
  const { data: itemsData } = useItems({ skip: 0, limit: 1000 });
  const createBlueprint = useCreateBlueprint();
  const updateBlueprint = useUpdateBlueprint();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [craftingTimeMinutes, setCraftingTimeMinutes] = useState(0);
  const [outputItemId, setOutputItemId] = useState("");
  const [outputQuantity, setOutputQuantity] = useState(1);
  const [isPublic, setIsPublic] = useState(false);
  const [ingredients, setIngredients] = useState<BlueprintIngredient[]>([]);

  useEffect(() => {
    if (blueprint && isEditMode) {
      setName(blueprint.name);
      setDescription(blueprint.description || "");
      setCategory(blueprint.category || "");
      setCraftingTimeMinutes(blueprint.crafting_time_minutes);
      setOutputItemId(blueprint.output_item_id);
      setOutputQuantity(blueprint.output_quantity);
      setIsPublic(blueprint.is_public);
      setIngredients(blueprint.blueprint_data.ingredients || []);
    }
  }, [blueprint, isEditMode]);

  const handleAddIngredient = () => {
    setIngredients([
      ...ingredients,
      { item_id: "", quantity: 1, optional: false },
    ]);
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleIngredientChange = (
    index: number,
    field: keyof BlueprintIngredient,
    value: string | number | boolean
  ) => {
    const updated = [...ingredients];
    updated[index] = { ...updated[index], [field]: value };
    setIngredients(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const blueprintData: BlueprintCreate | BlueprintUpdate = {
      name,
      description: description || undefined,
      category: category || undefined,
      crafting_time_minutes: craftingTimeMinutes,
      output_item_id: outputItemId,
      output_quantity: outputQuantity,
      blueprint_data: {
        ingredients: ingredients.filter((ing) => ing.item_id !== ""),
      },
      is_public: isPublic,
    };

    try {
      if (isEditMode && id) {
        await updateBlueprint.mutateAsync({ id, data: blueprintData });
      } else {
        await createBlueprint.mutateAsync(blueprintData as BlueprintCreate);
      }
      navigate("/blueprints");
    } catch (error) {
      console.error("Failed to save blueprint:", error);
    }
  };

  const isLoading = isEditMode && isLoadingBlueprint;
  const isSaving = createBlueprint.isPending || updateBlueprint.isPending;

  if (isLoading) {
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
      <H1 style={pageHeader}>
        {isEditMode ? "Edit Blueprint" : "Create Blueprint"}
      </H1>

      <form onSubmit={handleSubmit}>
        <Card style={{ marginBottom: spacing.lg }}>
          <FormGroup label="Name" labelFor="name" helperText="Blueprint name">
            <InputGroup
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter blueprint name"
              required
            />
          </FormGroup>

          <FormGroup
            label="Description"
            labelFor="description"
            helperText="Optional description"
          >
            <TextArea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter blueprint description"
              rows={3}
              fill
            />
          </FormGroup>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: spacing.md,
            }}
          >
            <FormGroup label="Category" labelFor="category">
              <HTMLSelect
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                fill
              >
                <option value="">Select category...</option>
                <option value="Weapons">Weapons</option>
                <option value="Components">Components</option>
                <option value="Food">Food</option>
                <option value="Materials">Materials</option>
                <option value="Other">Other</option>
              </HTMLSelect>
            </FormGroup>

            <FormGroup
              label="Crafting Time (minutes)"
              labelFor="craftingTime"
              helperText="Time required to craft"
            >
              <NumericInput
                id="craftingTime"
                value={craftingTimeMinutes}
                onValueChange={(value) => setCraftingTimeMinutes(value)}
                min={0}
                fill
              />
            </FormGroup>
          </div>
        </Card>

        <Card style={{ marginBottom: spacing.lg }}>
          <H3 style={{ marginBottom: spacing.md }}>Output</H3>
          <Divider style={{ marginBottom: spacing.md }} />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "2fr 1fr",
              gap: spacing.md,
            }}
          >
            <FormGroup label="Output Item" labelFor="outputItem">
              <HTMLSelect
                id="outputItem"
                value={outputItemId}
                onChange={(e) => setOutputItemId(e.target.value)}
                fill
                required
              >
                <option value="">Select output item...</option>
                {itemsData?.items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} {item.category ? `(${item.category})` : ""}
                  </option>
                ))}
              </HTMLSelect>
            </FormGroup>

            <FormGroup label="Quantity" labelFor="outputQuantity">
              <NumericInput
                id="outputQuantity"
                value={outputQuantity}
                onValueChange={(value) => setOutputQuantity(value)}
                min={0.001}
                stepSize={0.1}
                fill
                required
              />
            </FormGroup>
          </div>
        </Card>

        <Card style={{ marginBottom: spacing.lg }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: spacing.md,
            }}
          >
            <H3 style={{ margin: 0 }}>Ingredients</H3>
            <Button
              icon="plus"
              text="Add Ingredient"
              onClick={handleAddIngredient}
            />
          </div>
          <Divider style={{ marginBottom: spacing.md }} />

          {ingredients.length === 0 ? (
            <Callout intent={Intent.WARNING}>
              No ingredients added. Click "Add Ingredient" to add required
              materials.
            </Callout>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: spacing.md,
              }}
            >
              {ingredients.map((ingredient, index) => (
                <Card
                  key={index}
                  style={{ backgroundColor: colors.background.tertiary }}
                >
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "2fr 1fr auto auto",
                      gap: spacing.md,
                      alignItems: "end",
                    }}
                  >
                    <FormGroup
                      label="Item"
                      labelFor={`ingredient-item-${index}`}
                    >
                      <HTMLSelect
                        id={`ingredient-item-${index}`}
                        value={ingredient.item_id}
                        onChange={(e) =>
                          handleIngredientChange(
                            index,
                            "item_id",
                            e.target.value
                          )
                        }
                        fill
                        required
                      >
                        <option value="">Select item...</option>
                        {itemsData?.items.map((item) => (
                          <option key={item.id} value={item.id}>
                            {item.name}{" "}
                            {item.category ? `(${item.category})` : ""}
                          </option>
                        ))}
                      </HTMLSelect>
                    </FormGroup>

                    <FormGroup
                      label="Quantity"
                      labelFor={`ingredient-qty-${index}`}
                    >
                      <NumericInput
                        id={`ingredient-qty-${index}`}
                        value={ingredient.quantity}
                        onValueChange={(value) =>
                          handleIngredientChange(index, "quantity", value)
                        }
                        min={0.001}
                        stepSize={0.1}
                        fill
                        required
                      />
                    </FormGroup>

                    <FormGroup
                      label="Optional"
                      labelFor={`ingredient-opt-${index}`}
                    >
                      <Switch
                        id={`ingredient-opt-${index}`}
                        checked={ingredient.optional || false}
                        onChange={(e) =>
                          handleIngredientChange(
                            index,
                            "optional",
                            e.currentTarget.checked
                          )
                        }
                      />
                    </FormGroup>

                    <Button
                      icon="trash"
                      intent="danger"
                      onClick={() => handleRemoveIngredient(index)}
                    />
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <FormGroup label="Visibility" labelFor="isPublic">
            <Switch
              id="isPublic"
              label="Make this blueprint public"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.currentTarget.checked)}
            />
          </FormGroup>
        </Card>

        <div
          style={{ marginTop: spacing.xl, display: "flex", gap: spacing.md }}
        >
          <Button
            type="submit"
            intent="primary"
            text={isEditMode ? "Update Blueprint" : "Create Blueprint"}
            loading={isSaving}
            large
          />
          <Button
            text="Cancel"
            onClick={() => navigate("/blueprints")}
            disabled={isSaving}
          />
        </div>
      </form>

      {(createBlueprint.error || updateBlueprint.error) && (
        <Callout intent={Intent.DANGER} style={{ marginTop: spacing.lg }}>
          Error:{" "}
          {createBlueprint.error?.message ||
            updateBlueprint.error?.message ||
            "Failed to save blueprint"}
        </Callout>
      )}
    </DashboardLayout>
  );
}
