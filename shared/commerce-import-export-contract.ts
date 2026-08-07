import { z } from "zod";

export const COMMERCE_MARKETPLACES = ["amazon","alibaba","aliexpress","walmart","ebay","etsy","shopify","temu","1688","made_in_china","globalsources","dhgate","faire","other"] as const;
export const FULFILLMENT_MODES = ["dropship","fba","fbm","3pl","direct_import","local_stock","print_on_demand","digital"] as const;

export const supplierOfferSchema = z.object({
  supplierId: z.string().trim().min(2).max(160),
  supplierName: z.string().trim().min(2).max(200),
  marketplace: z.enum(COMMERCE_MARKETPLACES),
  productName: z.string().trim().min(2).max(300),
  productUrlOrReference: z.string().trim().min(2).max(1024),
  unitCostUsd: z.number().min(0),
  moq: z.number().int().min(1).default(1),
  leadTimeDays: z.number().int().min(0).max(3650),
  sampleAvailable: z.boolean().default(false),
  customizationAvailable: z.boolean().default(false),
  certificationsClaimed: z.array(z.string().trim().min(1).max(160)).max(100).default([]),
  supplierEvidence: z.array(z.string().trim().min(2).max(1024)).max(100).default([]),
  verifiedStatus: z.enum(["unverified","document_reviewed","sample_tested","third_party_verified","production_verified"]).default("unverified"),
}).strict();

export const landedCostSchema = z.object({
  unitCostUsd: z.number().min(0),
  freightUsd: z.number().min(0).default(0),
  insuranceUsd: z.number().min(0).default(0),
  dutiesUsd: z.number().min(0).default(0),
  brokerageUsd: z.number().min(0).default(0),
  inspectionUsd: z.number().min(0).default(0),
  storageUsd: z.number().min(0).default(0),
  marketplaceFeesUsd: z.number().min(0).default(0),
  fulfillmentFeesUsd: z.number().min(0).default(0),
  returnsAllowanceUsd: z.number().min(0).default(0),
  marketingAllowanceUsd: z.number().min(0).default(0),
  otherUsd: z.number().min(0).default(0),
}).strict();

export const dropshipAgreementSchema = z.object({
  schema: z.literal("dreamco.dropship_agreement.v1"),
  agreementId: z.string().trim().min(3).max(160),
  buyerEntity: z.string().trim().min(2).max(200),
  supplierEntity: z.string().trim().min(2).max(200),
  products: z.array(z.string().trim().min(2).max(300)).min(1).max(500),
  territory: z.array(z.string().trim().min(2).max(120)).min(1).max(100),
  fulfillmentMode: z.enum(FULFILLMENT_MODES),
  serviceLevels: z.object({
    maxHandlingDays: z.number().int().min(0).max(365),
    trackingRequired: z.boolean().default(true),
    packagingStandards: z.string().trim().min(3).max(2000),
    returnWindowDays: z.number().int().min(0).max(365),
  }).strict(),
  commercialTerms: z.object({
    currency: z.string().trim().min(3).max(8).default("USD"),
    paymentTerms: z.string().trim().min(2).max(500),
    priceChangeNoticeDays: z.number().int().min(0).max(365).default(30),
    minimumMarginPercent: z.number().min(-100).max(1000).nullable().default(null),
  }).strict(),
  quality: z.object({
    preShipmentInspectionAllowed: z.boolean().default(true),
    defectThresholdPercent: z.number().min(0).max(100).default(2),
    replacementOrRefundRequired: z.boolean().default(true),
  }).strict(),
  compliance: z.object({
    sellerResponsibleForMarketplacePolicies: z.boolean().default(true),
    supplierResponsibleForAccurateProductClaims: z.boolean().default(true),
    restrictedGoodsReviewRequired: z.boolean().default(true),
    customsAndImportRulesReviewRequired: z.boolean().default(true),
    legalReviewRecommended: z.boolean().default(true),
  }).strict(),
}).strict();

export const importExportProfileSchema = z.object({
  schema: z.literal("dreamco.import_export_profile.v1"),
  category: z.string().trim().min(2).max(160),
  originCountry: z.string().trim().min(2).max(120),
  destinationCountry: z.string().trim().min(2).max(120),
  hsCode: z.string().trim().max(32).nullable().default(null),
  requiredDocuments: z.array(z.string().trim().min(2).max(200)).max(100).default([]),
  licensesOrPermits: z.array(z.string().trim().min(2).max(200)).max(100).default([]),
  productSafetyRequirements: z.array(z.string().trim().min(2).max(500)).max(100).default([]),
  labelingRequirements: z.array(z.string().trim().min(2).max(500)).max(100).default([]),
  restrictedOrProhibitedFlags: z.array(z.string().trim().min(2).max(500)).max(100).default([]),
  officialSourceReferences: z.array(z.string().trim().min(2).max(1024)).max(100).default([]),
  lastVerifiedAt: z.string().datetime().nullable().default(null),
}).strict();

export const botCommerceLaneSchema = z.object({
  schema: z.literal("dreamco.bot_commerce_lane.v1"),
  botSlug: z.string().trim().min(2).max(160),
  category: z.string().trim().min(2).max(160),
  sourceMarketplaces: z.array(z.enum(COMMERCE_MARKETPLACES)).min(1).max(COMMERCE_MARKETPLACES.length),
  salesMarketplaces: z.array(z.enum(COMMERCE_MARKETPLACES)).min(1).max(COMMERCE_MARKETPLACES.length),
  fulfillmentModes: z.array(z.enum(FULFILLMENT_MODES)).min(1).max(FULFILLMENT_MODES.length),
  benchmarkSuiteIds: z.array(z.string().trim().min(2).max(160)).min(1).max(200),
  requiredConnectors: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  marginFloorPercent: z.number().min(-100).max(1000).default(20),
  requireSupplierVerificationBeforeScale: z.boolean().default(true),
  requireLandedCostBeforeListing: z.boolean().default(true),
  requireCategoryComplianceReview: z.boolean().default(true),
}).strict();

export function totalLandedCost(input: z.infer<typeof landedCostSchema>) {
  return Object.values(input).reduce((sum, value) => sum + value, 0);
}
