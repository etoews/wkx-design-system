# WKX Design System

Three design system options for the operational user interfaces of
[wkx-platform](../wkx-platform/), a personal Docker Compose platform running in
two homes: AWS (public-facing) and an on-prem home server (LAN-only).

Each option carries the same operational surface, so they compare like for like:
fleet, host vitals, alarms, deploy history, parameters, and the monthly account
against the NZD $50 cap. Content reflects the platform as at M5, with the M9
home env and M10 backups shown as honest empty states.

## The options

| Option | File | Point of view |
|--------|------|---------------|
| 1 · Red Ledger | [01-red-ledger.html](01-red-ledger.html) | Wing Kong Exchange is a trading house, so the platform keeps a vermilion-ruled trading ledger. Jade chop stamps for state, the budget settled like a monthly book. Light, serif, narrative. |
| 2 · Harbour Watch | [02-harbour-watch.html](02-harbour-watch.html) | Two berths watched at night. Status is a navigation light with documented meaning: starboard green underway, anchor amber holding, port red fault. Dark, dense, signal-driven. |
| 3 · Namespace | [03-namespace.html](03-namespace.html) | The platform's path grammar as the interface. Every panel addressed by `/wkx/<service>/<env>`, Terraform plan symbols for state, hover-to-highlight on every token of the ubiquitous language. Light, monospace, interactive. |

## Viewing

Static HTML and JS only, no build step, no external requests. Open
[index.html](index.html) directly in a browser, or serve the folder:

```sh
python3 -m http.server
```

Typefaces are macOS system stacks (Hoefler Text, Charter, Avenir Next, Menlo,
SF Mono) with standard fallbacks elsewhere. All three respect
`prefers-reduced-motion`, keep visible keyboard focus, and hold up down to
mobile widths.
