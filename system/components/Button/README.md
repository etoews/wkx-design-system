# Button

The one control style: condensed, uppercase, tracked, on a 4px radius.

**Use** `default` for most actions, `primary` (an `accent` fill) at most once per view for the action the view exists for, and `danger` (an outline in `danger`) for anything destructive. Use `size="small"` inside panel footers.

**Consumer provides** the label as children (a verb first, plus the exact object where it matters: "Deploy e7d09b4", "Roll back to a3f91c2"), `onClick`, and any native button props. `type` defaults to `button`.

**Don't** fill a danger button, add icons, or put two primaries side by side.
