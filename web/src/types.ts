// ── 解析结果 ──────────────────────────────────────────────────────────────────

export interface Dataset {
  name: string
  type: string  // 'DBTableData' | 'EmbeddedTableData' | ...
  db_connection?: string
  sql?: string
  sql_params?: string[]
  columns?: string[]
  column_details?: Record<string, ColumnDetail[]>
}

export interface ColumnDetail {
  column: string
  type: string
  comment?: string
  key?: string
}

export interface Widget {
  name: string
  widget_type: string
  bound_dataset?: string
  key_column?: string
  display_column?: string
  custom_options?: Array<{ key: string; value: string }>
}

export interface CellBinding {
  pos: string
  dataset?: string
  column?: string
  data_mode?: string
  format_type?: string
  parent_left?: string
  parent_up?: string
  cell_filter?: string
  widget_type?: string
  expand_dir?: string
}

export interface LabelDataPair {
  label_text: string
  label_pos: string
  data_pos: string
  dataset?: string
  column?: string
  widget_type?: string
}

export interface HighlightRule {
  name: string
  condition: string
  action: string
  color?: string
  affected_columns?: string[]
}

export interface WritebackConfig {
  db_connection?: string
  table?: string
  key_columns?: string[]
  column_mappings?: Array<{ db_column: string; param?: string; is_key?: boolean }>
}

export interface ParsedReport {
  file_name: string
  fr_version: string
  sheet_count: number
  file_size_kb: number
  report_type: 'query' | 'writeback'
  datasets: Dataset[]
  widgets: Widget[]
  cell_bindings: CellBinding[]
  formula_cells: Array<{ pos: string; formula: string; js_events?: string[] }>
  label_data_pairs: LabelDataPair[]
  dataset_shared_keys: Array<{ field: string; shared_by: string[] }>
  highlight_rules_summary: HighlightRule[]
  writeback_config?: WritebackConfig
  db_connections: string[]
  errors?: string[]
}

// ── 分析结果 ──────────────────────────────────────────────────────────────────

export interface InteractionChain {
  widget_name: string
  widget_type?: string
  param_role?: string
  sql_impact?: string
  data_displayed?: string
  why_this_design?: string
}

export interface Indicator {
  indicator_name: string
  source_field: string
  dataset?: string
  type: string
  unit?: string
  formula?: string
  description: string
}

export interface FormulaExplanation {
  pos: string
  formula: string
  meaning: string
}

export interface AnalysisResult {
  purpose?: string
  layout_description?: string
  dataset_relationships?: string
  field_semantics?: string
  interaction_chains?: InteractionChain[]
  formula_explanations?: FormulaExplanation[]
  display_rules?: string
  development_steps?: string[]
  indicator_dict?: Indicator[]
  notes_or_risks?: string[]
  _tokens_used?: number
  _parse_error?: string
}

// ── 血缘图 ────────────────────────────────────────────────────────────────────

export interface LineageResult {
  mermaid: string
  mermaid_raw: string
  dot: string
  sql_driving_widget_names: string[]
  option_driving_widget_names?: string[]
  unmatched_widget_names: string[]
}

// ── 应用状态 ──────────────────────────────────────────────────────────────────

export type AppPhase =
  | 'idle'
  | 'uploading'
  | 'uploaded'
  | 'enriching'
  | 'analyzing'
  | 'done'
  | 'error'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AppState {
  phase: AppPhase
  parsed: ParsedReport | null
  analysis: AnalysisResult | null
  lineage: LineageResult | null
  dbEnriched: boolean
  streamLog: string[]
  chatHistory: ChatMessage[]
  error: string | null
}
