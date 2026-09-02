---
name: browser-use-enhanced
description: "Use persistent local Chrome automation via Browser Use for interactive websites, logged-in sessions, scraping, form filling, screenshots, uploads, downloads, and web-app QA when plain HTTP or a purpose-built connector is insufficient."
---

# Browser Use Enhanced

Use the plugin's `browser_exec` and `browser_screenshot` MCP tools to control a persistent local Chrome session through Browser Use 0.13.7.

## Routing

- Prefer a purpose-built connector or direct HTTP fetch for semantic reads and simple public pages.
- Use Browser Use Enhanced when the task needs clicks, typing, JavaScript rendering, authenticated browser state, uploads/downloads, screenshots, or end-to-end web testing.
- Do not use Browser Use Cloud unless the user explicitly accepts its external service and possible cost. The installed default is local-only.

## Safe workflow

1. Inspect current tabs and page state before acting.
2. Use accessibility/DOM state for element targeting; use screenshots only when visual layout matters.
3. Perform one coherent action at a time, then verify the resulting URL or state.
4. Never enter passwords, OTPs, payment data, private keys, or consent choices for the user.
5. Ask before destructive actions, purchases, publishing, permission changes, or transmitting sensitive files.
6. Close only tabs or browser sessions created for the task unless the user asks otherwise.

## Reliability

- Keep the same persistent session through a workflow.
- Re-inspect after navigation; do not reuse stale element indices.
- On failure, report the exact page state and retry only after checking whether the previous action already succeeded.
- For local app testing, verify both expected success paths and one meaningful failure path.

Upstream source: https://github.com/browser-use/browser-use (MIT). Installed runtime is pinned to 0.13.7.
