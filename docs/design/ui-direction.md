# UI direction

## Status

Accepted design direction. Exact dimensions and control styling will be refined
in implementation.

## Purpose

Streak.txt should feel like a warm, dense habit switchboard: a desktop tool
that is quick to use several times a day and becomes familiar through spatial
memory.

## Principles

- Provide one primary everyday view.
- Show streaks in a compact, fixed-position grid.
- Keep every streak and its action in the same place after ticking; do not
  automatically sort, hide, or move completed streaks.
- Make ticking feel tactile, with an unmistakable pressed/completed state.
- Prefer useful density, clear borders, and compact controls over decorative
  spacing.
- Treat streak statistics as small readouts; recording today's activity is the
  primary task.
- Draw from the efficiency of retro computer interfaces without imitating a
  particular operating system.
- Keep streak data local and stored in plain-text files.

## Palette

Use the four-color
[Dusty4 palette](https://lospec.com/palette-list/dusty4) by ink:

- `#f5f6df`
- `#5a8f78`
- `#3a5068`
- `#372a51`

Use only these colors initially. Assign their exact interface roles while
testing the first implementation, and change the palette only if it creates a
clear usability problem.

## Interaction constraints

- Stable geometry and control placement take priority over automatic
  organization.
- Store panel order and future collection-level settings in
  `streaks-config.json` beside the streak files so they travel with the
  collection.
- Completion must remain clear without relying on color alone.
- Undo should require more intention than tick; its exact interaction remains
  to be decided.
- New streaks must not unexpectedly rearrange existing streaks.

## Open details

- Initial ordering and whether deliberate manual rearrangement is supported.
- Grid dimensions at different desktop window sizes.
- The minimum statistics shown on each streak control.
- Tick, completed, and undo control behavior.
