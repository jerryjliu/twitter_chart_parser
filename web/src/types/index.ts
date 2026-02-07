export type ParseTier = "fast" | "cost_effective" | "agentic" | "agentic_plus";

export type MediaExtractionSource = "x_api" | "syndication" | "fxtwitter_api" | "html_meta";

export interface TableResult {
  page_number: number;
  row_count: number;
  column_count: number;
  markdown: string;
  bbox?: number[] | null;
}

export interface ParsedImageResult {
  image_url: string;
  filename: string;
  success: boolean;
  markdown: string;
  tables: TableResult[];
  error?: string | null;
}

export interface ParseTweetRequest {
  api_key: string;
  tweet_url: string;
  tier: ParseTier;
  enable_chart_parsing: boolean;
  x_bearer_token?: string;
}

export interface ParseTweetResponse {
  tweet_id: string;
  normalized_tweet_url: string;
  source: MediaExtractionSource;
  results: ParsedImageResult[];
  combined_markdown: string;
  warnings: string[];
}

export interface ValidateLlamaKeyResponse {
  valid: boolean;
  message: string;
}

export interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}
