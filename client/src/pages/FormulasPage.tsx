import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState, useMemo } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { FORMULA_CATEGORIES } from "@shared/formula-library";
import type { Formula } from "@shared/schema";
import {
  FlaskConical,
  Lock,
  Pencil,
  Plus,
  Search,
  Trash2,
  X,
  Variable,
  Target,
  Tag,
  Save,
  Loader2,
} from "lucide-react";

const CATEGORY_COLORS: Record<string, string> = {
  "Real Estate": "border-blue-500/40 bg-blue-500/10 text-blue-600 dark:text-blue-400",
  "Car Flipping": "border-amber-500/40 bg-amber-500/10 text-amber-600 dark:text-amber-400",
  "Sales": "border-green-500/40 bg-green-500/10 text-green-600 dark:text-green-400",
  "Capital Deployment": "border-purple-500/40 bg-purple-500/10 text-purple-600 dark:text-purple-400",
  "Risk Management": "border-red-500/40 bg-red-500/10 text-red-600 dark:text-red-400",
  "Revenue Intelligence": "border-teal-500/40 bg-teal-500/10 text-teal-600 dark:text-teal-400",
};

interface FormulaFormData {
  name: string;
  category: string;
  description: string;
  formula: string;
  variables: string;
  target: string;
  tags: string;
}

const EMPTY_FORM: FormulaFormData = {
  name: "",
  category: FORMULA_CATEGORIES[0],
  description: "",
  formula: "",
  variables: "",
  target: "",
  tags: "",
};

function FormulaForm({
  initial,
  onSave,
  onCancel,
  isPending,
}: {
  initial: FormulaFormData;
  onSave: (data: FormulaFormData) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const [form, setForm] = useState<FormulaFormData>(initial);

  const update = (field: keyof FormulaFormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  return (
    <div className="space-y-4 p-5 rounded-md border border-border bg-card">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <Label className="text-xs text-muted-foreground">Name</Label>
          <Input
            value={form.name}
            onChange={update("name")}
            placeholder="Formula name"
            className="mt-1"
            data-testid="input-formula-name"
          />
        </div>
        <div>
          <Label className="text-xs text-muted-foreground">Category</Label>
          <Select
            value={form.category}
            onValueChange={(v) => setForm((prev) => ({ ...prev, category: v }))}
          >
            <SelectTrigger className="mt-1" data-testid="select-formula-category">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {FORMULA_CATEGORIES.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      <div>
        <Label className="text-xs text-muted-foreground">Description</Label>
        <Textarea
          value={form.description}
          onChange={update("description")}
          placeholder="What this formula calculates"
          className="mt-1 resize-none"
          rows={2}
          data-testid="input-formula-description"
        />
      </div>
      <div>
        <Label className="text-xs text-muted-foreground">Formula</Label>
        <Input
          value={form.formula}
          onChange={update("formula")}
          placeholder="e.g. ROI = (Net Profit / Cost) * 100"
          className="mt-1 font-mono"
          data-testid="input-formula-expression"
        />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <Label className="text-xs text-muted-foreground">Variables (comma-separated)</Label>
          <Input
            value={form.variables}
            onChange={update("variables")}
            placeholder="e.g. Net Profit, Cost"
            className="mt-1"
            data-testid="input-formula-variables"
          />
        </div>
        <div>
          <Label className="text-xs text-muted-foreground">Target</Label>
          <Input
            value={form.target}
            onChange={update("target")}
            placeholder="e.g. ROI >= 20%"
            className="mt-1"
            data-testid="input-formula-target"
          />
        </div>
      </div>
      <div>
        <Label className="text-xs text-muted-foreground">Tags (comma-separated)</Label>
        <Input
          value={form.tags}
          onChange={update("tags")}
          placeholder="e.g. roi, profitability, analysis"
          className="mt-1"
          data-testid="input-formula-tags"
        />
      </div>
      <div className="flex items-center gap-2 pt-1">
        <Button
          onClick={() => onSave(form)}
          disabled={!form.name.trim() || !form.formula.trim() || isPending}
          data-testid="btn-save-formula"
        >
          {isPending ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Save className="h-4 w-4 mr-2" />
          )}
          Save
        </Button>
        <Button variant="ghost" onClick={onCancel} data-testid="btn-cancel-formula">
          Cancel
        </Button>
      </div>
    </div>
  );
}

function FormulaCard({
  formula,
  onEdit,
  onDelete,
}: {
  formula: Formula;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const variables = Array.isArray(formula.variables) ? (formula.variables as string[]) : [];
  const tags = Array.isArray(formula.tags) ? (formula.tags as string[]) : [];
  const colorClass = CATEGORY_COLORS[formula.category] || "";

  return (
    <Card className="hover-elevate" data-testid={`card-formula-${formula.id}`}>
      <CardHeader className="flex flex-row items-start justify-between gap-2 pb-3">
        <div className="min-w-0 flex-1">
          <CardTitle className="text-base leading-tight" data-testid={`text-formula-name-${formula.id}`}>
            {formula.name}
          </CardTitle>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <Badge
              variant="outline"
              className={cn("text-xs rounded-full", colorClass)}
              data-testid={`badge-category-${formula.id}`}
            >
              {formula.category}
            </Badge>
            {formula.isSystem && (
              <Badge variant="secondary" className="text-xs rounded-full" data-testid={`badge-system-${formula.id}`}>
                <Lock className="h-3 w-3 mr-1" />
                System
              </Badge>
            )}
          </div>
        </div>
        {!formula.isSystem && (
          <div className="flex items-center gap-1 shrink-0">
            <Button
              size="icon"
              variant="ghost"
              onClick={onEdit}
              data-testid={`btn-edit-formula-${formula.id}`}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={onDelete}
              data-testid={`btn-delete-formula-${formula.id}`}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-3 pt-0">
        {formula.description && (
          <p className="text-sm text-muted-foreground" data-testid={`text-formula-desc-${formula.id}`}>
            {formula.description}
          </p>
        )}

        <div
          className="p-3 rounded-md bg-muted/40 border border-border/40 font-mono text-sm break-all"
          data-testid={`text-formula-expression-${formula.id}`}
        >
          {formula.formula}
        </div>

        {variables.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Variable className="h-3 w-3" /> Variables
            </p>
            <div className="flex flex-wrap gap-1">
              {variables.map((v, i) => (
                <Badge key={i} variant="secondary" className="text-xs">
                  {v}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {formula.target && (
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Target className="h-3 w-3" /> Target
            </p>
            <p className="text-sm" data-testid={`text-formula-target-${formula.id}`}>
              {formula.target}
            </p>
          </div>
        )}

        {tags.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Tag className="h-3 w-3" /> Tags
            </p>
            <div className="flex flex-wrap gap-1">
              {tags.map((t, i) => (
                <Badge key={i} variant="outline" className="text-xs">
                  {t}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function FormulasPage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  const { data: formulas = [], isLoading } = useQuery<Formula[]>({
    queryKey: ["/api/formulas"],
  });

  const createMutation = useMutation({
    mutationFn: async (data: Record<string, unknown>) =>
      await apiRequest("POST", "/api/formulas", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/formulas"] });
      toast({ title: "Formula created" });
      setShowAddForm(false);
    },
    onError: (e: Error) => {
      toast({ title: "Failed to create formula", description: e.message, variant: "destructive" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Record<string, unknown> }) =>
      await apiRequest("PATCH", `/api/formulas/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/formulas"] });
      toast({ title: "Formula updated" });
      setEditingId(null);
    },
    onError: (e: Error) => {
      toast({ title: "Failed to update formula", description: e.message, variant: "destructive" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => await apiRequest("DELETE", `/api/formulas/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/formulas"] });
      toast({ title: "Formula deleted" });
      setDeleteConfirmId(null);
    },
    onError: (e: Error) => {
      toast({ title: "Failed to delete formula", description: e.message, variant: "destructive" });
    },
  });

  const filtered = useMemo(() => {
    let list = formulas;
    if (activeTab !== "All") {
      list = list.filter((f) => f.category === activeTab);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (f) =>
          f.name.toLowerCase().includes(q) ||
          f.description.toLowerCase().includes(q) ||
          f.formula.toLowerCase().includes(q),
      );
    }
    return list;
  }, [formulas, activeTab, searchQuery]);

  const parseFormData = (form: FormulaFormData) => ({
    name: form.name.trim(),
    category: form.category,
    description: form.description.trim(),
    formula: form.formula.trim(),
    variables: form.variables
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
    target: form.target.trim(),
    tags: form.tags
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
  });

  const handleCreate = (form: FormulaFormData) => {
    createMutation.mutate(parseFormData(form));
  };

  const handleUpdate = (id: number, form: FormulaFormData) => {
    updateMutation.mutate({ id, data: parseFormData(form) });
  };

  const formulaToFormData = (f: Formula): FormulaFormData => ({
    name: f.name,
    category: f.category,
    description: f.description,
    formula: f.formula,
    variables: Array.isArray(f.variables) ? (f.variables as string[]).join(", ") : "",
    target: f.target,
    tags: Array.isArray(f.tags) ? (f.tags as string[]).join(", ") : "",
  });

  return (
    <AppShell>
      <Seo title="Formula Vault | DreamCo Empire OS" description="Manage and explore business formulas for deal analysis, risk management, and revenue intelligence." />
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center">
              <FlaskConical className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold" data-testid="text-page-title">Formula Vault</h1>
              <p className="text-sm text-muted-foreground" data-testid="text-formula-count">
                {formulas.length} formula{formulas.length !== 1 ? "s" : ""}
              </p>
            </div>
          </div>
          <Button
            onClick={() => {
              setShowAddForm(true);
              setEditingId(null);
            }}
            data-testid="btn-add-formula"
          >
            <Plus className="h-4 w-4 mr-2" /> Add Formula
          </Button>
        </div>

        {showAddForm && (
          <FormulaForm
            initial={EMPTY_FORM}
            onSave={handleCreate}
            onCancel={() => setShowAddForm(false)}
            isPending={createMutation.isPending}
          />
        )}

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search formulas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
            data-testid="input-search-formulas"
          />
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="flex flex-wrap h-auto gap-1" data-testid="tabs-category-filter">
            <TabsTrigger value="All" data-testid="tab-all">
              All
            </TabsTrigger>
            {FORMULA_CATEGORIES.map((c) => (
              <TabsTrigger key={c} value={c} data-testid={`tab-${c.toLowerCase().replace(/\s/g, "-")}`}>
                {c}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value={activeTab} className="mt-4">
            {isLoading ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i}>
                    <CardHeader>
                      <Skeleton className="h-5 w-40" />
                      <Skeleton className="h-4 w-24 mt-2" />
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <Skeleton className="h-12 w-full" />
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-48" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <FlaskConical className="h-12 w-12 text-muted-foreground/40 mb-4" />
                <h3 className="text-lg font-semibold" data-testid="text-empty-state">
                  No formulas found
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {searchQuery || activeTab !== "All"
                    ? "Try adjusting your filters or search query."
                    : "Add your first formula to get started."}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {filtered.map((f) =>
                  editingId === f.id ? (
                    <div key={f.id} className="lg:col-span-2">
                      <FormulaForm
                        initial={formulaToFormData(f)}
                        onSave={(data) => handleUpdate(f.id, data)}
                        onCancel={() => setEditingId(null)}
                        isPending={updateMutation.isPending}
                      />
                    </div>
                  ) : deleteConfirmId === f.id ? (
                    <Card key={f.id} className="border-destructive/40" data-testid={`card-delete-confirm-${f.id}`}>
                      <CardContent className="p-5">
                        <p className="text-sm font-medium mb-1">Delete "{f.name}"?</p>
                        <p className="text-xs text-muted-foreground mb-4">
                          This action cannot be undone.
                        </p>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="destructive"
                            onClick={() => deleteMutation.mutate(f.id)}
                            disabled={deleteMutation.isPending}
                            data-testid={`btn-confirm-delete-${f.id}`}
                          >
                            {deleteMutation.isPending ? (
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4 mr-2" />
                            )}
                            Delete
                          </Button>
                          <Button
                            variant="ghost"
                            onClick={() => setDeleteConfirmId(null)}
                            data-testid={`btn-cancel-delete-${f.id}`}
                          >
                            Cancel
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ) : (
                    <FormulaCard
                      key={f.id}
                      formula={f}
                      onEdit={() => {
                        setEditingId(f.id);
                        setShowAddForm(false);
                      }}
                      onDelete={() => setDeleteConfirmId(f.id)}
                    />
                  ),
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
