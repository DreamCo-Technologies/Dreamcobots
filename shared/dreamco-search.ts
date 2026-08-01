export type DreamSearchDocumentType =
  | "bot"
  | "capability"
  | "division"
  | "library"
  | "model"
  | "page"
  | "provider"
  | "roadmap"
  | "system";

export interface DreamSearchDocument {
  id: string;
  type: DreamSearchDocumentType;
  title: string;
  summary: string;
  url: string;
  keywords: string[];
  category: string;
  division: string;
  status: string;
  evidence_level: string;
  evidence: string;
  search_text?: string;
}

export interface DreamSearchConfig {
  query_policy: {
    max_length: number;
    minimum_length: number;
    stop_words: string[];
    synonym_groups: Array<{ id: string; terms: string[] }>;
  };
  ranking: {
    exact_title: number;
    title_phrase: number;
    summary_phrase: number;
    keyword_phrase: number;
    title_token: number;
    keyword_token: number;
    summary_token: number;
    category_token: number;
    evidence_bonus: number;
    status_bonus: number;
    type_boosts: Record<DreamSearchDocumentType, number>;
  };
  result_policy: {
    default_limit: number;
    maximum_limit: number;
  };
}

export interface DreamSearchFilters {
  type?: DreamSearchDocumentType | "all";
  division?: string | "all";
  evidenceLevel?: string | "all";
  status?: string | "all";
  limit?: number;
}

export interface DreamSearchResult {
  document: DreamSearchDocument;
  score: number;
  matched_terms: string[];
}

export function normalizeSearchText(value: string): string {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function unique(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))];
}

export function expandSearchQuery(query: string, config: DreamSearchConfig): string[] {
  const normalized = normalizeSearchText(query).slice(0, config.query_policy.max_length);
  const stopWords = new Set(config.query_policy.stop_words.map(normalizeSearchText));
  const baseTokens = normalized.split(" ").filter((token) => token && !stopWords.has(token));
  const expanded = [...baseTokens];

  for (const group of config.query_policy.synonym_groups) {
    const normalizedTerms = group.terms.map(normalizeSearchText);
    const matchesGroup = normalizedTerms.some((term) => term && (` ${normalized} `).includes(` ${term} `));
    if (!matchesGroup) continue;
    for (const term of normalizedTerms) {
      expanded.push(...term.split(" ").filter((token) => token && !stopWords.has(token)));
    }
  }

  return unique(expanded);
}

function includesToken(haystack: string, token: string): boolean {
  return (` ${haystack} `).includes(` ${token} `);
}

export function rankDreamSearchDocuments(
  documents: DreamSearchDocument[],
  query: string,
  config: DreamSearchConfig,
  filters: DreamSearchFilters = {},
): DreamSearchResult[] {
  const normalizedQuery = normalizeSearchText(query).slice(0, config.query_policy.max_length);
  if (normalizedQuery.length < config.query_policy.minimum_length) return [];

  const tokens = expandSearchQuery(normalizedQuery, config);
  const originalTokens = unique(
    normalizedQuery.split(" ").filter((token) => token && !config.query_policy.stop_words.includes(token)),
  );
  const ranking = config.ranking;
  const typeFilter = filters.type || "all";
  const divisionFilter = filters.division || "all";
  const evidenceFilter = filters.evidenceLevel || "all";
  const statusFilter = filters.status || "all";
  const limit = Math.min(
    Math.max(filters.limit || config.result_policy.default_limit, 1),
    config.result_policy.maximum_limit,
  );

  return documents
    .filter((document) => typeFilter === "all" || document.type === typeFilter)
    .filter((document) => divisionFilter === "all" || document.division === divisionFilter)
    .filter((document) => evidenceFilter === "all" || document.evidence_level === evidenceFilter)
    .filter((document) => statusFilter === "all" || document.status === statusFilter)
    .map((document): DreamSearchResult => {
      const title = normalizeSearchText(document.title);
      const summary = normalizeSearchText(document.summary);
      const keywords = normalizeSearchText(document.keywords.join(" "));
      const category = normalizeSearchText(`${document.category} ${document.division} ${document.type}`);
      let score = ranking.type_boosts[document.type] || 0;
      const matchedTerms: string[] = [];

      if (title === normalizedQuery) score += ranking.exact_title;
      else if (title.includes(normalizedQuery)) score += ranking.title_phrase;
      if (summary.includes(normalizedQuery)) score += ranking.summary_phrase;
      if (keywords.includes(normalizedQuery)) score += ranking.keyword_phrase;

      for (const token of tokens) {
        let matched = false;
        if (includesToken(title, token)) {
          score += ranking.title_token;
          matched = true;
        }
        if (includesToken(keywords, token)) {
          score += ranking.keyword_token;
          matched = true;
        }
        if (includesToken(summary, token)) {
          score += ranking.summary_token;
          matched = true;
        }
        if (includesToken(category, token)) {
          score += ranking.category_token;
          matched = true;
        }
        if (matched) matchedTerms.push(token);
      }

      if (document.evidence) score += ranking.evidence_bonus;
      if (!document.status.includes("roadmap")) score += ranking.status_bonus;
      score += originalTokens.filter((token) => matchedTerms.includes(token)).length * 4;
      return { document, score, matched_terms: unique(matchedTerms) };
    })
    .filter((result) => result.matched_terms.length > 0 || result.score >= ranking.title_phrase)
    .sort((a, b) => b.score - a.score || a.document.title.localeCompare(b.document.title) || a.document.id.localeCompare(b.document.id))
    .slice(0, limit);
}

export function buildDreamSearchWebUrl(template: string, query: string, maxLength = 240): string {
  const cleaned = String(query || "").trim().slice(0, maxLength);
  if (!cleaned) throw new Error("A web search query is required.");
  return template.replace("{query}", encodeURIComponent(cleaned));
}
