// WKX components: window.WKX.<Name>. React 18, props as below.
type Status = "good" | "caution" | "danger" | "off";
type Tone = "good" | "caution" | "danger";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** default: quiet; primary: accent fill, once per view; danger: outlined, destructive. */
  variant?: "default" | "primary" | "danger";
  size?: "default" | "small";
}
export interface StatusLightProps { status?: Status; /** State in the app's words; defaults to status. */ label?: string; }
export interface SectionLabelProps { /** Mono identifier ahead of the label. */ code?: string; children?: React.ReactNode; }
export interface PanelProps {
  label?: string; labelCode?: string;
  /** 3px top rule and a mono title/aside head, for top-level groups. */
  ruled?: boolean; title?: React.ReactNode; aside?: React.ReactNode;
  /** Span the full row of a .wkx-grid. */
  wide?: boolean; ariaLabel?: string; children?: React.ReactNode;
}
export interface MeterProps { /** 0–100 */ value: number; /** 0–100, tick position */ threshold?: number; tone?: Tone; label?: string; }
export interface GaugeProps { label: string; value: string; unit?: string; detail?: string; percent?: number; threshold?: number; tone?: Tone; }
type TableSort = { key: string; dir: "ascending" | "descending" } | null;
export interface DataTableProps {
  /** num: right-aligned, sorts as a number. sortable: false keeps one column unsorted. locked: the columns menu can't hide it. */
  columns: { key: string; label: string; num?: boolean; sortable?: boolean; locked?: boolean }[];
  /** sorts: a value to sort by in place of the cell; search: the text the filter reads, for cells that are not plain text. */
  rows: ({ id?: string | number; tones?: Record<string, Tone | "muted">; sorts?: Record<string, string | number>; search?: string } & Record<string, React.ReactNode>)[];
  caption?: string;
  /** Column heads sort on click: ascending, descending, then the rows' own order. */
  sortable?: boolean; sort?: TableSort; defaultSort?: TableSort; onSortChange?: (sort: TableSort) => void;
  /** A filter pill above the table, with an "N of M" count to its left. */
  filterable?: boolean; filter?: string; defaultFilter?: string; onFilterChange?: (text: string) => void; filterLabel?: string;
  /** A columns menu right of the filter; hidden lists the keys of hidden columns. */
  hideable?: boolean; hidden?: string[]; defaultHidden?: string[]; onHiddenChange?: (hidden: string[]) => void;
  /** Offset for the sticky column heads, under a fixed page header (a CSS length). */
  stickyTop?: string;
}
export interface ListRowProps { status?: Status; statusLabel?: string; name: React.ReactNode; detail?: React.ReactNode; stat?: React.ReactNode; }
export interface FieldProps extends React.InputHTMLAttributes<HTMLInputElement> { label: string; id?: string; }
export interface HighlightProps { /** Key shared by every occurrence; defaults to the text. */ term?: string; children: React.ReactNode; }
export interface HintProps { children: React.ReactNode; }
export interface LegendProps { items: { status: Status; term: string; meaning?: string }[]; label?: string; }
export interface LogViewProps {
  lines: { id?: string | number; time?: string; text?: string; parts?: { text: string; tone?: Tone | "muted" }[] }[];
  height?: string; follow?: boolean; label?: string; footer?: React.ReactNode;
}
export interface ThemeToggleProps { storageKey?: string; label?: false; }
