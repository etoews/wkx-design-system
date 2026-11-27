/* @ds-bundle: {"format":4,"namespace":"WKX","components":[{"name":"Button"},{"name":"StatusLight"},{"name":"SectionLabel"},{"name":"Panel"},{"name":"Gauge"},{"name":"Meter"},{"name":"DataTable"},{"name":"ListRow"},{"name":"Field"},{"name":"Highlight"},{"name":"Legend"},{"name":"LogView"},{"name":"ThemeToggle"}]} */
(function () {
  "use strict";
  var React = window.React;
  var h = React.createElement;

  function cx() {
    var out = [];
    for (var i = 0; i < arguments.length; i++) if (arguments[i]) out.push(arguments[i]);
    return out.join(" ");
  }
  function omit(obj, keys) {
    var out = {};
    for (var k in obj) if (Object.prototype.hasOwnProperty.call(obj, k) && keys.indexOf(k) < 0) out[k] = obj[k];
    return out;
  }

  function Button(props) {
    var variant = props.variant || "default";
    var rest = omit(props, ["variant", "size", "className", "children"]);
    rest.type = rest.type || "button";
    rest.className = cx("wkx-btn", variant !== "default" && "wkx-btn-" + variant, props.size === "small" && "wkx-btn-small", props.className);
    return h("button", rest, props.children);
  }

  function StatusLight(props) {
    var status = props.status || "good";
    var label = props.label || status;
    return h("span", {
      className: cx("wkx-light", status !== "good" && "wkx-light-" + status, props.className),
      role: "img",
      "aria-label": label
    });
  }

  function SectionLabel(props) {
    return h("p", { className: cx("wkx-label", props.className) },
      props.code ? h("span", { className: "wkx-label-code" }, props.code) : null,
      props.code && props.children ? " · " : null,
      props.children);
  }

  function Panel(props) {
    var head = null;
    if (props.title || props.aside) {
      head = h("div", { className: "wkx-panel-head" },
        h("span", { className: "wkx-panel-title" }, props.title),
        props.aside ? h("span", { className: "wkx-panel-aside" }, props.aside) : null);
    }
    return h("section", {
      className: cx("wkx-panel", props.ruled && "wkx-panel-ruled", props.wide && "wkx-wide", props.className),
      "aria-label": props.ariaLabel
    },
      props.label ? h(SectionLabel, { code: props.labelCode }, props.label) : null,
      head,
      props.children);
  }

  function Meter(props) {
    var value = Math.max(0, Math.min(100, Number(props.value) || 0));
    var tone = props.tone || "good";
    return h("div", {
      className: cx("wkx-meter", tone !== "good" && "wkx-meter-" + tone, props.className),
      role: "meter", "aria-valuemin": 0, "aria-valuemax": 100, "aria-valuenow": value,
      "aria-label": props.label
    },
      h("i", { className: "wkx-meter-fill", style: { width: value + "%" } }),
      props.threshold != null ? h("span", { className: "wkx-meter-tick", style: { left: props.threshold + "%" } }) : null);
  }

  function Gauge(props) {
    return h("div", { className: cx("wkx-gauge", props.className) },
      h("p", { className: "wkx-gauge-key" }, props.label),
      h("p", { className: "wkx-gauge-value" }, props.value,
        props.unit ? h("span", { className: "wkx-gauge-unit" }, " " + props.unit) : null),
      props.detail ? h("p", { className: "wkx-gauge-detail" }, props.detail) : null,
      props.percent != null ? h(Meter, { value: props.percent, threshold: props.threshold, tone: props.tone, label: props.label }) : null);
  }

  /* DataTable sort and filter. A column head cycles ascending, descending, then
     back to the rows' own order. The filter keeps a row when any cell's text
     contains it, ignoring case. Both work controlled (sort/onSortChange,
     filter/onFilterChange) or on their own (defaultSort, defaultFilter). */
  var BLANK = /^(|—|-|·|…|···)$/;
  function cellText(r, key) {
    var v = r[key];
    return typeof v === "string" || typeof v === "number" ? String(v) : "";
  }
  function sortValue(r, key) {
    var v = r.sorts && r.sorts[key] != null ? r.sorts[key] : cellText(r, key);
    return String(v).trim();
  }
  function sortRows(rows, sort) {
    if (!sort || !sort.key || !sort.dir) return rows;
    var key = sort.key, sign = sort.dir === "descending" ? -1 : 1;
    var values = rows.map(function (r) { return sortValue(r, key); });
    var numeric = values.some(function (v) { return !BLANK.test(v); }) &&
      values.every(function (v) { return BLANK.test(v) || !isNaN(parseFloat(v)); });
    return rows.map(function (r, i) { return { r: r, v: values[i], i: i }; }).sort(function (a, b) {
      var ba = BLANK.test(a.v), bb = BLANK.test(b.v);
      if (ba || bb) return ba === bb ? a.i - b.i : (ba ? 1 : -1); /* blanks last, either way */
      var cmp = numeric ? parseFloat(a.v) - parseFloat(b.v)
        : a.v.localeCompare(b.v, undefined, { numeric: true, sensitivity: "base" });
      return cmp * sign || a.i - b.i;
    }).map(function (x) { return x.r; });
  }
  function nextSort(sort, key) {
    if (!sort || sort.key !== key || !sort.dir) return { key: key, dir: "ascending" };
    if (sort.dir === "ascending") return { key: key, dir: "descending" };
    return null;
  }
  function useControlled(value, initial, onChange) {
    var st = React.useState(initial);
    var controlled = value !== undefined;
    return [controlled ? value : st[0], function (next) {
      if (!controlled) st[1](next);
      if (onChange) onChange(next);
    }];
  }

  /* Wrap each case-insensitive occurrence of query in a plain-text cell. */
  function marked(value, query) {
    if (!query || (typeof value !== "string" && typeof value !== "number")) return value;
    var text = String(value), lower = text.toLowerCase(), out = [], at = 0, i;
    while ((i = lower.indexOf(query, at)) >= 0) {
      if (i > at) out.push(text.slice(at, i));
      out.push(h("mark", { key: i, className: "wkx-match" }, text.slice(i, i + query.length)));
      at = i + query.length;
    }
    if (!out.length) return value;
    if (at < text.length) out.push(text.slice(at));
    return out;
  }

  /* The columns menu: a pill that drops a checklist of the table's columns.
     Locked columns stay checked; the last visible column can't be hidden.
     Closes on a click outside or Escape, which hands focus back to the pill. */
  function ColumnsMenu(props) {
    var open = React.useState(false);
    var ref = React.useRef(null), btn = React.useRef(null);
    var isOpen = open[0], setOpen = open[1];
    React.useEffect(function () {
      if (!isOpen) return undefined;
      function onClick(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
      function onKey(e) { if (e.key === "Escape") { setOpen(false); if (btn.current) btn.current.focus(); } }
      document.addEventListener("mousedown", onClick);
      document.addEventListener("keydown", onKey);
      return function () {
        document.removeEventListener("mousedown", onClick);
        document.removeEventListener("keydown", onKey);
      };
    }, [isOpen]);
    var hidden = props.hidden;
    var visible = props.columns.filter(function (c) { return hidden.indexOf(c.key) < 0; }).length;
    return h("div", { className: "wkx-cols", ref: ref },
      h("button", {
        type: "button", ref: btn, className: "wkx-pill wkx-cols-btn",
        "aria-expanded": isOpen ? "true" : "false", "aria-haspopup": "true",
        onClick: function () { setOpen(!isOpen); }
      }, "columns", h("span", { className: "wkx-cols-caret", "aria-hidden": "true" }, "▾")),
      isOpen ? h("div", { className: "wkx-cols-menu", role: "group", "aria-label": "Columns" },
        props.columns.map(function (c) {
          var shown = hidden.indexOf(c.key) < 0;
          var fixed = c.locked || (shown && visible === 1);
          return h("label", { key: c.key, className: cx("wkx-cols-item", fixed && "wkx-cols-fixed") },
            h("input", {
              type: "checkbox", checked: shown, disabled: fixed,
              onChange: function () {
                props.onChange(shown ? hidden.concat([c.key]) : hidden.filter(function (k) { return k !== c.key; }));
              }
            }),
            h("span", { className: "wkx-cols-label" }, c.label),
            c.locked ? h("span", { className: "wkx-cols-note" }, "locked") : null);
        })) : null);
  }

  function DataTable(props) {
    var all = props.columns || [];
    var rows = props.rows || [];
    var sortState = useControlled(props.sort, props.defaultSort || null, props.onSortChange);
    var filterState = useControlled(props.filter, props.defaultFilter || "", props.onFilterChange);
    var hiddenState = useControlled(props.hidden, props.defaultHidden || [], props.onHiddenChange);
    var sort = sortState[0], filter = filterState[0];
    var hidden = props.hideable ? hiddenState[0] || [] : [];
    var columns = all.filter(function (c) { return hidden.indexOf(c.key) < 0; });
    var query = props.filterable ? filter.trim().toLowerCase() : "";
    /* A hidden column is outside the filter's reach. */
    var shown = query ? rows.filter(function (r) {
      var text = r.search != null ? String(r.search) : columns.map(function (c) { return cellText(r, c.key); }).join(" ");
      return text.toLowerCase().indexOf(query) >= 0;
    }) : rows;
    shown = props.sortable ? sortRows(shown, sort) : shown;

    var tools = props.filterable || props.hideable ? h("div", { className: "wkx-table-tools" },
      props.filterable ? h("span", { className: "wkx-table-count", "aria-live": "polite" }, filter ? shown.length + " of " + rows.length : "") : null,
      props.filterable ? h("input", {
        type: "search", className: "wkx-pill wkx-table-filter", placeholder: "filter…",
        "aria-label": props.filterLabel || "Filter " + (props.caption || "rows"),
        value: filter, onChange: function (e) { filterState[1](e.target.value); }
      }) : null,
      props.hideable ? h(ColumnsMenu, { columns: all, hidden: hidden, onChange: hiddenState[1] }) : null) : null;

    var top = props.stickyTop != null ? { top: props.stickyTop } : undefined;
    function head(c) {
      var align = c.num ? "wkx-num" : undefined;
      if (!props.sortable || c.sortable === false) return h("th", { key: c.key, scope: "col", className: align, style: top }, c.label);
      var dir = sort && sort.key === c.key ? sort.dir : null;
      return h("th", { key: c.key, scope: "col", className: align, style: top, "aria-sort": dir || undefined },
        h("button", {
          type: "button", className: cx("wkx-sort", dir && "wkx-sort-on"),
          onClick: function () { sortState[1](nextSort(sort, c.key)); }
        }, c.label, h("span", { className: "wkx-sort-mark", "aria-hidden": "true" }, dir === "descending" ? "▼" : "▲")));
    }

    return h("div", { className: cx("wkx-table-block", props.className) },
      tools,
      h("div", { className: "wkx-table-wrap" },
        h("table", { className: "wkx-table" },
          props.caption ? h("caption", { className: "wkx-label", style: { marginBottom: ".8rem" } }, props.caption) : null,
          h("thead", null, h("tr", null, columns.map(head))),
          h("tbody", null, shown.length || !query ? shown.map(function (r, i) {
            return h("tr", { key: r.id != null ? r.id : i }, columns.map(function (c) {
              var tone = r.tones && r.tones[c.key];
              return h("td", { key: c.key, className: cx(tone && "wkx-cell-" + tone, c.num && "wkx-num") || undefined }, marked(r[c.key], query));
            }));
          }) : h("tr", null, h("td", { colSpan: columns.length || 1, className: "wkx-cell-muted" }, "No rows match “" + filter.trim() + "”."))))));
  }

  function ListRow(props) {
    return h("div", { className: cx("wkx-list-row", props.className) },
      h(StatusLight, { status: props.status || "good", label: props.statusLabel }),
      h("span", { className: "wkx-list-name" }, props.name,
        props.detail ? h("small", { className: "wkx-list-sub" }, props.detail) : null),
      h("span", { className: "wkx-list-stat" }, props.stat != null ? props.stat : "·"));
  }

  var fieldCount = 0;
  function Field(props) {
    var idRef = React.useRef(props.id || "wkx-field-" + (++fieldCount));
    var rest = omit(props, ["label", "className", "id"]);
    rest.id = idRef.current;
    rest.type = rest.type || "text";
    return h("span", { className: cx("wkx-field", props.className) },
      h("label", { htmlFor: idRef.current }, props.label),
      h("input", rest));
  }

  /* Highlight: every <Highlight term="x"> on the page lights up together on
     hover or focus; click or Enter pins it; Escape releases. One document-level
     registry so it works across separately mounted roots. */
  var pinned = null;
  function paint(term, on) {
    var els = document.querySelectorAll(".wkx-term");
    for (var i = 0; i < els.length; i++) {
      var t = els[i].getAttribute("data-term");
      var lit = t === pinned || (on && t === term);
      els[i].classList.toggle("wkx-lit", lit);
      els[i].classList.toggle("wkx-pinned", t === pinned);
    }
  }
  var escBound = false;
  function bindEscape() {
    if (escBound) return;
    escBound = true;
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && pinned !== null) { pinned = null; paint(null, false); }
    });
  }
  function Highlight(props) {
    var term = props.term || (typeof props.children === "string" ? props.children : "");
    React.useEffect(bindEscape, []);
    function toggle() { pinned = pinned === term ? null : term; paint(term, true); }
    return h("span", {
      className: "wkx-term", "data-term": term, tabIndex: 0, role: "button",
      onMouseEnter: function () { paint(term, true); },
      onMouseLeave: function () { paint(term, false); },
      onFocus: function () { paint(term, true); },
      onBlur: function () { paint(term, false); },
      onClick: function (e) { e.preventDefault(); toggle(); },
      onKeyDown: function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } }
    }, props.children);
  }
  function Hint(props) { return h("span", { className: "wkx-hint" }, props.children); }

  function Legend(props) {
    var items = props.items || [];
    return h("div", { className: cx("wkx-legend", props.className), role: "note", "aria-label": props.label || "Legend" },
      items.map(function (it, i) {
        return h("span", { key: i, className: "wkx-legend-item" },
          h("span", { className: cx("wkx-light", it.status !== "good" && "wkx-light-" + it.status), "aria-hidden": "true" }),
          h("span", null, h("b", null, it.term), it.meaning ? ", " + it.meaning : null));
      }));
  }

  function LogView(props) {
    var ref = React.useRef(null);
    var lines = props.lines || [];
    React.useEffect(function () {
      if (ref.current && props.follow !== false) ref.current.scrollTop = ref.current.scrollHeight;
    }, [lines.length, props.follow]);
    return h("div", null,
      h("div", { className: "wkx-log", ref: ref, style: { height: props.height || "11.5rem" }, "aria-live": "off", tabIndex: 0, "aria-label": props.label || "Log" },
        lines.map(function (ln, i) {
          return h("div", { key: ln.id != null ? ln.id : i, className: "wkx-log-line" },
            ln.time ? h("span", { className: "wkx-log-time" }, ln.time + " ") : null,
            (ln.parts || [{ text: ln.text }]).map(function (p, j) {
              return h("span", { key: j, className: p.tone ? "wkx-log-" + p.tone : undefined }, (j ? " " : "") + p.text);
            }));
        })),
      props.footer ? h("div", { className: "wkx-log-foot" }, props.footer) : null);
  }

  /* ThemeToggle: cycles auto, light, dark. Auto follows prefers-color-scheme.
     Sets data-theme on <html>; persists the override when storage allows. */
  var THEMES = ["auto", "light", "dark"];
  function readSaved(key) { try { return window.localStorage.getItem(key); } catch (e) { return null; } }
  function writeSaved(key, v) { try { if (v === "auto") window.localStorage.removeItem(key); else window.localStorage.setItem(key, v); } catch (e) { /* storage blocked: the choice lasts this visit */ } }
  function applyTheme(choice) {
    var mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
    var resolved = choice === "auto" ? (mq && !mq.matches ? "light" : "dark") : choice;
    document.documentElement.setAttribute("data-theme", resolved);
  }
  function ThemeToggle(props) {
    var key = props.storageKey || "wkx-theme";
    var init = readSaved(key);
    var st = React.useState(THEMES.indexOf(init) >= 0 ? init : "auto");
    var theme = st[0], setTheme = st[1];
    React.useEffect(function () {
      applyTheme(theme);
      if (theme !== "auto" || !window.matchMedia) return undefined;
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      var on = function () { applyTheme("auto"); };
      if (mq.addEventListener) mq.addEventListener("change", on);
      return function () { if (mq.removeEventListener) mq.removeEventListener("change", on); };
    }, [theme]);
    return h("span", { className: "wkx-theme-wrap" }, props.label === false ? null : "theme: ",
      h("button", {
        type: "button", className: "wkx-theme-toggle",
        "aria-label": "Theme: " + theme + ". Cycles auto, light, dark.",
        onClick: function () {
          var next = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
          writeSaved(key, next);
          setTheme(next);
        }
      }, theme));
  }

  window.WKX = Object.assign(window.WKX || {}, {
    Button: Button, StatusLight: StatusLight, SectionLabel: SectionLabel,
    Panel: Panel, Gauge: Gauge, Meter: Meter, DataTable: DataTable, ListRow: ListRow,
    Field: Field, Highlight: Highlight, Hint: Hint, Legend: Legend, LogView: LogView,
    ThemeToggle: ThemeToggle
  });
})();
