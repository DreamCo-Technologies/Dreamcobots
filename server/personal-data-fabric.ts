import { createHash, randomUUID } from "node:crypto";
import { z } from "zod";

export const personalDataClassSchema = z.enum([
  "notes", "documents", "images", "audio", "video", "spreadsheets", "presentations", "pdfs",
  "email_exports", "calendar_exports", "contact_exports", "chat_exports", "browser_bookmarks",
  "photos_metadata", "app_exports", "health_exports", "finance_exports", "receipts", "invoices",
  "projects", "code", "links", "tasks", "preferences", "custom_records"
]);

export const personalDataRecordSchema = z.object({
  id: z.string().min(3),
  ownerId: z.string().min(1),
  dataClass: personalDataClassSchema,
  title: z.string().min(1).max(500),
  source: z.string().min(1).max(1000),
  storageRef: z.string().min(1).max(2000),
  mimeType: z.string().min(1).max(200),
  size: z.number().int().nonnegative(),
  contentHash: z.string().regex(/^sha256:[a-f0-9]{64}$/),
  consentScope: z.string().min(1).max(1000),
  sensitivity: z.enum(["public", "normal", "private", "sensitive", "highly_sensitive"]).default("private"),
  importedAt: z.string().datetime(),
  retention: z.enum(["session", "30_days", "1_year", "until_user_deletes", "source_managed"]).default("until_user_deletes"),
  exportable: z.boolean().default(true),
  deletable: z.boolean().default(true),
  tags: z.array(z.string().min(1).max(120)).max(100).default([]),
  summary: z.string().max(4000).optional(),
  appConnector: z.string().max(200).optional(),
}).strict();

export const ingestionPlanSchema = z.object({
  ownerId: z.string().min(1),
  dataClass: personalDataClassSchema,
  title: z.string().min(1).max(500),
  source: z.string().min(1).max(1000),
  mimeType: z.string().min(1).max(200),
  byteLength: z.number().int().nonnegative(),
  sha256Hex: z.string().regex(/^[a-f0-9]{64}$/),
  userSelectedStorageRef: z.string().min(1).max(2000),
  consentScope: z.string().min(1).max(1000),
  sensitivity: z.enum(["public", "normal", "private", "sensitive", "highly_sensitive"]).default("private"),
  retention: z.enum(["session", "30_days", "1_year", "until_user_deletes", "source_managed"]).default("until_user_deletes"),
  tags: z.array(z.string().min(1).max(120)).max(100).default([]),
  appConnector: z.string().max(200).optional(),
}).strict();

export type PersonalDataRecord = z.infer<typeof personalDataRecordSchema>;
export type IngestionPlan = z.infer<typeof ingestionPlanSchema>;

export class PersonalDataFabric {
  private readonly records = new Map<string, PersonalDataRecord>();

  createRecord(input: IngestionPlan): PersonalDataRecord {
    const plan = ingestionPlanSchema.parse(input);
    const idSeed = `${plan.ownerId}:${plan.sha256Hex}:${plan.source}:${plan.userSelectedStorageRef}`;
    const id = `data-${createHash("sha256").update(idSeed).digest("hex").slice(0, 24)}`;
    const record = personalDataRecordSchema.parse({
      id,
      ownerId: plan.ownerId,
      dataClass: plan.dataClass,
      title: plan.title,
      source: plan.source,
      storageRef: plan.userSelectedStorageRef,
      mimeType: plan.mimeType,
      size: plan.byteLength,
      contentHash: `sha256:${plan.sha256Hex}`,
      consentScope: plan.consentScope,
      sensitivity: plan.sensitivity,
      importedAt: new Date().toISOString(),
      retention: plan.retention,
      exportable: true,
      deletable: true,
      tags: plan.tags,
      appConnector: plan.appConnector,
    });
    this.records.set(id, record);
    return record;
  }

  addValidatedRecord(record: PersonalDataRecord) {
    const parsed = personalDataRecordSchema.parse(record);
    this.records.set(parsed.id, parsed);
    return parsed;
  }

  search(ownerId: string, query = "", options: { dataClass?: z.infer<typeof personalDataClassSchema>; source?: string; tag?: string } = {}) {
    const q = query.trim().toLowerCase();
    return [...this.records.values()]
      .filter((row) => row.ownerId === ownerId)
      .filter((row) => !options.dataClass || row.dataClass === options.dataClass)
      .filter((row) => !options.source || row.source === options.source)
      .filter((row) => !options.tag || row.tags.includes(options.tag))
      .filter((row) => !q || `${row.title} ${row.source} ${row.summary || ""} ${row.tags.join(" ")}`.toLowerCase().includes(q))
      .sort((a, b) => b.importedAt.localeCompare(a.importedAt));
  }

  exportOwnerManifest(ownerId: string) {
    return {
      schema: "dreamco.personal_data_export.v1",
      exportId: randomUUID(),
      ownerId,
      exportedAt: new Date().toISOString(),
      records: this.search(ownerId).filter((row) => row.exportable),
      rawBytesIncluded: false,
      note: "This manifest exports metadata and storage references. Raw user files remain in the user-selected storage location unless a separate explicit export copies them."
    } as const;
  }

  deleteRecord(ownerId: string, id: string) {
    const row = this.records.get(id);
    if (!row || row.ownerId !== ownerId || !row.deletable) return false;
    return this.records.delete(id);
  }

  revokeConnector(ownerId: string, connector: string) {
    let detached = 0;
    for (const [id, row] of this.records) {
      if (row.ownerId === ownerId && row.appConnector === connector) {
        this.records.set(id, { ...row, appConnector: undefined, source: `${row.source} (connector revoked)` });
        detached += 1;
      }
    }
    return detached;
  }

  summary(ownerId: string) {
    const rows = this.search(ownerId);
    return {
      schema: "dreamco.personal_data_summary.v1",
      ownerId,
      recordCount: rows.length,
      byClass: Object.fromEntries([...new Set(rows.map((row) => row.dataClass))].map((dataClass) => [dataClass, rows.filter((row) => row.dataClass === dataClass).length])),
      exportableCount: rows.filter((row) => row.exportable).length,
      deletableCount: rows.filter((row) => row.deletable).length,
      localOrUserSelectedStorage: true,
      cloudCopyDefault: false,
    } as const;
  }
}
