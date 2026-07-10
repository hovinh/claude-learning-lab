# Claude Code: Setup and Usage Guide

> A working reference for using Claude Code effectively in a project, based on hands-on notes from building a sample app (Lifting Diary Course).

## 1. What is Claude Code

Claude Code is Anthropic's agentic coding tool that runs in your terminal (or VS Code's integrated terminal). Instead of copy-pasting snippets into a chat window, it can read your codebase, edit files directly, run commands, and iterate on tasks with your project as live context.

## 2. Project Setup Example

Example scaffold using Next.js:

```bash
npx create-next-app@latest liftingdiarycourse
```

Recommended options when prompted:
- Use "customize settings"
- TypeScript: yes
- Linter: ESLint
- React Compiler: no
- Styling: Tailwind CSS
- Source directory: `src/`
- Routing: App Router
- Import alias: keep default (no customization)

## 3. Installing and Configuring Claude Code

1. Install Claude Code and make sure it's on your `PATH` environment variable.
2. Open your project in VS Code, open the integrated terminal, and run:
   ```bash
   claude
   ```
3. Log in with your Claude/Anthropic account when prompted.

### Useful setup commands
| Command | Purpose |
|---|---|
| `/terminal-setup` | Configures terminal integration (keybindings, rendering) |
| `/theme` | Change the color theme of the CLI |
| `/config` | View/edit Claude Code configuration |
| `/model` | Select which model Claude Code uses |
| `/init` | Scans the codebase and generates a `CLAUDE.md` file documenting the project. This file is automatically attached as context to every chat in that project. |
| `/context` | Shows how much of the context window is currently used |
| `/clear` | Clears the current context window (starts a fresh session) |
| `/install-github-app` | Sets up Claude's GitHub Actions integration |
| `/agents` | Lists existing sub-agents in the project, or creates a new one |

### Modes
- **Shift+Tab** — toggles between **Plan Mode** (Claude proposes an approach before touching any files) and **Implementation Mode** (Claude executes changes directly). Plan mode is useful for reviewing an approach before letting Claude edit code.
- **Extended thinking mode** — when enabled, Claude spends more tokens reasoning before responding. This generally produces higher-quality output and is best reserved for complex, multi-step, or ambiguous tasks (not simple edits, since it costs more tokens/time).

## 4. Custom Slash Commands

If you find yourself repeating the same prompt, you can save it as a reusable slash command.

**Project-scoped commands** live in `.claude/commands/`. Example:

`.claude/commands/merge-and-create-branch.md`:
```
Commit any changes in the current branch with a suitable commit message
based on the code change. Then merge the current branch into main and
resolve any issues from that merge. Finally create a new branch called $ARGUMENTS.
```

Usage:
```
/merge-and-create-branch edit-workout-page
```

- `$ARGUMENTS` captures everything passed after the command name.
- If you need to reference more than one distinct argument, use `$1`, `$2`, etc. for positional arguments.

Another example, for generating documentation on demand:

`create-docs.md`:
```
Create a new documentation file at docs/$1.md to highlight the coding
standards for this layer of the app. Specifically cover: $2
```

**User-scoped commands** live in `~/.claude/commands/` (create the directory with `mkdir -p ~/.claude/commands`). These are personal to you and won't affect other contributors on the same project.

> **Naming conflicts:** if a user-scoped command has the same name as a project-scoped one, Claude Code will only recognize the user-scoped command. To avoid ambiguity, place personal versions inside a `personal/` subdirectory — Claude Code will then show a prefix in the command picker to distinguish the two.

## 5. Skills

Skills are reusable, filesystem-based resources that give Claude domain-specific expertise: workflows, context, and best practices.

**How they differ from prompts:** prompts are one-off, conversation-level instructions. Skills persist across conversations and load on demand, so you don't have to repeat the same guidance every time.

**How they differ from MCP servers:** with an MCP server, its full tool/resource definitions typically have to be front-loaded into context, whether or not you end up using them. Skills use **progressive disclosure** instead — only the skill's short description is loaded upfront. If Claude decides mid-task that a skill is relevant, it then reads the skill's full `SKILL.md` file, and pulls in any additional referenced resources only as needed. This means you can have a large library of skills (e.g. 100+) without bloating the context window.

This also means you can wrap something that would normally require front-loaded MCP context — e.g. a Neon database MCP server — as a skill instead, so its details are only read into context when actually queried.

### Installing / creating a skill
1. Install the `skill-creator` skill (Anthropic's official one) into your project. There are also community sites (e.g. skills.sh) with pre-made skills, though you should review/scan any third-party skill before installing.
2. This creates `.claude/skills/skill-creator/` containing:
   - `SKILL.md` — explains explicitly what the skill does
   - supporting scripts
   - reference files for specific information the skill needs
3. From there, you can ask Claude Code to build a new skill for you, e.g.:
   > "Create a new skill that queries the database for all workout entries from the past year using the database URL connection string in the `.env` file. Plot this data as a bar chart with a Python script (x-axis: month, y-axis: number of workouts), and export the chart as an image."

## 6. Sub-agents

Sub-agents (managed via `/agents`) let you define focused, automated helpers scoped to a specific trigger and task, each with its own allowed tools and model.

Example: a `docs-reference-updater` agent —
- **Trigger:** whenever a new file is added to the `/docs` directory
- **Task:** update `CLAUDE.md` to reference the new file under the `## Code Generation Guideline` section
- **Setup:** when creating the agent, you choose which tools it's allowed to access, and which model runs it.

## 7. Feature Comparison: Skills vs Commands vs Sub-agents vs Prompts vs MCP

These features overlap conceptually — they're all ways of getting Claude to do something in a repeatable way — but they solve different problems. This table is meant to remove the guesswork on "which one should I reach for."

| Feature | What it actually is | Persists across sessions? | How it's invoked | Context cost | Best for | Example |
|---|---|---|---|---|---|---|
| **Prompt** (regular chat message) | A one-off instruction typed directly into the conversation | No — gone once the conversation/context is cleared | Manually, every time | Only costs tokens for that one turn | Ad hoc, one-time tasks you won't repeat | "Refactor this function to use async/await" |
| **Custom slash command** | A saved prompt template stored as a file (`.claude/commands/*.md`), optionally parameterized with `$ARGUMENTS`/`$1`/`$2` | Yes — saved to disk, reused across sessions | Explicitly, by typing `/command-name args` | Only loads when called | A repeated instruction with a fixed shape/wording that you (or your team) trigger by hand | `/merge-and-create-branch edit-workout-page` |
| **Skill** | A folder-based package (`SKILL.md` + optional scripts/references) describing domain-specific expertise or a workflow | Yes — lives in `.claude/skills/` | Automatically — Claude decides on its own whether a skill is relevant to the current task, based on its short description | Very low until triggered; only the description is front-loaded, full contents load on demand (progressive disclosure) | Reusable expertise/workflows you want Claude to pull in *without* you having to remember to ask (e.g. "how we do database migrations here") | A skill that knows how to query the DB and generate a workout chart |
| **Sub-agent** | A named, scoped agent (via `/agents`) with its own trigger condition, allowed tools, and model | Yes — configured once, runs repeatedly | Automatically, based on its defined trigger (e.g. "a file is added to `/docs`") | Isolated — runs its own focused task/context, separate from your main session | Automating a specific recurring housekeeping task that should happen without manual prompting | `docs-reference-updater`: auto-updates `CLAUDE.md` when a new file lands in `/docs` |
| **MCP server** | An external tool/data source (e.g. a database, a ticketing system) exposed to Claude Code over the Model Context Protocol | Yes — configured once as a connection | Claude calls its exposed tools as needed during a task | Higher — tool/resource definitions are typically front-loaded into context as soon as the server is connected | Giving Claude live access to an external system (a real database, an API) rather than static knowledge | Neon's MCP server, letting Claude query your Postgres DB directly |
| **`CLAUDE.md`** | A standing project-level context file, auto-attached to every chat in the project | Yes — one file per project | Always active, no invocation needed | Loaded on every single turn, so keep it lean | Persistent project-wide ground rules and pointers (e.g. "always check `/docs` before generating code") | Generated via `/init`, then hand-edited to reference `/docs` files |
| **`/docs` standards files** | Plain markdown files describing team/project conventions (UI rules, data-fetching rules, etc.) | Yes — version-controlled like any other file | Only read when explicitly pointed to (usually via `CLAUDE.md`, or `@docs/file.md`) | Only loaded when referenced | Detailed, topic-specific rules that would bloat `CLAUDE.md` if inlined | `docs/ui.md`, `docs/data-fetching.md` |

**Rule of thumb for picking one:**
- Need Claude to do it *right now, once*? → just prompt it.
- Typing the same request repeatedly, verbatim-ish? → make it a **slash command**.
- Want Claude to *automatically* know how to approach a certain kind of task without you asking? → make it a **skill**.
- Want a background job to fire automatically on a specific trigger, independent of your main conversation? → make it a **sub-agent**.
- Need live access to an external system/data source, not just static knowledge? → connect an **MCP server**.
- Want a rule that should apply to *every* piece of code Claude writes in this project, all the time? → put it in **`CLAUDE.md`** (and push the details into a linked `/docs` file if it's long).

## 8. GitHub Actions Integration

After running `/install-github-app` and completing the setup steps:

1. Create a new issue in your GitHub repo describing the work.
2. Comment on the issue tagging `@claude`, e.g. "implement this."
3. Claude Code works the issue in the background and pushes a new branch.
4. Review the diff/branch, then create a pull request.

This pairs well with **Vercel**, which is free for web deployment: connect it to your GitHub repo and it will spin up a preview deployment for every branch — including the branches Claude's GitHub Action creates — so you can review changes live before merging.

## 9. Working with Files and Context

- **Referencing code:** highlight code in your editor (auto-selected as Claude Code input), drag files into the chat, or use `@` to point directly to a relevant file.
- **Context hygiene:** once you finish a piece of work, run `/clear` to reset the context window before starting the next task. This avoids polluting future prompts with irrelevant history and helps you avoid running out of context.
- **Inline bash commands:** prefix a command with `!` to run it directly — this doesn't cost tokens itself, but its output is added to context.
- **Long-running/background jobs:** for something like `npm run dev`, press **Ctrl+B** to send it to the background. Use `/tasks` to check on background jobs. Since background task output can be pulled into context, if an error appears in the logs you can simply prompt: "fix the error being emitted from the dev server in the background task."

## 10. Documentation-Driven Development

A useful pattern is to keep a `/docs` directory of standards documents, and have `CLAUDE.md` explicitly point to them, so Claude Code consults them before generating code.

Example prompts used to build this out:

> "Create a `docs/ui.md` file outlining the coding standard for the UI throughout this project. The document should state that ONLY shadcn/ui components should be used — ABSOLUTELY NO custom components. Dates should be formatted via `date-fns`, styled like `1st Sep 2025`."

> "Create a `docs/data-fetching.md` file stating that ALL data fetching in this app must be done via server components — NOT route handlers, NOT client components. Database queries must always go through helper functions in `/data`, using Drizzle ORM — DO NOT USE RAW SQL. A logged-in user should only ever be able to access their own data."

> "Update `CLAUDE.md` to state that all generated code should ALWAYS first refer to the relevant docs file within the `/docs` directory."

**Practical notes:**
- Using CAPITAL WORDS for the non-negotiable constraints (e.g. "ABSOLUTELY NO", "DO NOT USE RAW SQL") helps emphasize hard rules.
- Claude may not automatically consult a docs file just because `CLAUDE.md` vaguely references "docs" — you often need to state the exact file path explicitly (e.g. `docs/ui.md`), otherwise it may not read it before generating new code.
- Test this by clearing context and prompting for new code, then check whether the output conforms to your documented standards.
- If Claude repeats the same mistake across sessions, the fix is to explicitly add a note about it into the relevant documentation file — this "closes the loop" so future generations don't repeat it.

## 11. Third-Party Tooling Referenced

| Tool | Role |
|---|---|
| **Clerk** | Authentication-as-a-service. After creating a project on their site, Clerk gives you a setup prompt you can hand to Claude Code to wire up auth in your project. |
| **Neon** (console.neon.tech) | Free hosted Postgres database. Also ships an MCP server, so Claude Code can query/manage the database directly as a tool. |
| **Drizzle** | Open-source, TypeScript-first ORM for relational databases (used here instead of raw SQL). |
| **shadcn/ui** (ui.shadcn.com) | A library of composable, copy-into-your-project UI components. Constraining Claude Code to only use these components (rather than inventing custom ones) keeps the UI consistent. |
| **Vercel** | Free hosting/deployment platform, tightly integrated with GitHub — deploys a preview for every branch. |

## 12. Running Multiple Claude Code Instances

You don't have to wait for one Claude Code session to finish before starting another — multiple instances can run concurrently on the same project. However, be aware that if two instances touch the **same files**, they can conflict and produce a broken result. Best used when tasks are scoped to clearly separate files/areas of the codebase.

## 13. Local Models (Ollama)

Claude Code can also be pointed at a local, free, open-source model via [Ollama](https://ollama.com) instead of Anthropic's hosted models. As of these notes, local model output quality is noticeably behind Claude's hosted models — useful for experimentation or offline use, but not yet a like-for-like substitute for production work.

## 14. Reference Example

A full working example of the `CLAUDE.md` setup described above:
https://github.com/tomphill/liftingdiarycourse/blob/main/CLAUDE.md

---

## 15. Tips and a Recommended Workflow for Corporate Settings

**General tips**
- Treat `CLAUDE.md` as your project's onboarding doc for Claude — keep it current, and explicitly enumerate which `/docs` files must be consulted for which kind of change.
- Split standards into focused docs (`docs/ui.md`, `docs/data-fetching.md`, `docs/security.md`, etc.) rather than one giant file — this keeps each reference short and Claude more reliably reads the one relevant file.
- Use CAPITALIZED constraints sparingly, only for genuinely hard rules (security boundaries, forbidden patterns) — overusing emphasis dilutes it.
- When Claude repeats a mistake, don't just correct it in chat — encode the fix into the relevant docs file so it's caught earlier next time.
- Use `/clear` between unrelated tasks. Long, accumulated context degrades output quality and wastes tokens.
- Use Plan Mode (Shift+Tab) for any change with meaningful blast radius (schema changes, auth, data access) so you can review the approach before Claude edits files.
- Reserve extended thinking mode for genuinely complex/ambiguous tasks — it's slower and costs more tokens, so it's wasteful for small, well-defined edits.

**Suggested corporate workflow**

1. **Bootstrap the project context**
   - Run `/init` to generate a baseline `CLAUDE.md`.
   - Add a `/docs` directory with standards docs for UI, data access, security, and any team-specific conventions.
   - Update `CLAUDE.md` to explicitly point to each relevant doc.

2. **Scope the task**
   - Pull the ticket/issue into context (via `@file`, drag-and-drop, or by referencing the GitHub issue).
   - For non-trivial changes, start in Plan Mode so you and Claude agree on the approach before code is touched.

3. **Implement**
   - Switch to Implementation Mode (Shift+Tab) once the plan looks right.
   - Run dev servers or test suites as background tasks (Ctrl+B) so you can keep iterating while watching for errors.
   - Use inline `!` bash commands for quick checks (lint, type-check, git status) without burning extra turns.

4. **Review before merge**
   - Treat Claude's output like a junior engineer's PR: read the diff, don't just trust it.
   - For access-control or data-layer changes especially, manually verify the constraints in `docs/data-fetching.md` (or equivalent) were actually followed.
   - If using GitHub Actions integration, review the auto-created branch's diff on its Vercel preview deployment before opening a PR.

5. **Automate repetitive asks**
   - Once you notice yourself typing the same instruction more than twice, turn it into a project-scoped slash command (`.claude/commands/`) so the whole team benefits, or a user-scoped one if it's personal.
   - Turn recurring "go do X and report back" tasks into a sub-agent with a clear trigger, so it runs automatically rather than needing to be invoked by hand.

6. **Parallelize carefully**
   - When running multiple Claude Code instances at once, split work across files/modules that don't overlap, to avoid two instances editing the same file and producing conflicting or broken changes.

7. **Close the loop**
   - After each significant task, ask: did Claude make a mistake that a documentation update could have prevented? If so, update the doc immediately rather than relying on remembering to correct it verbally next time.
   - Periodically `/clear` and re-run `/init` (or manually refresh `CLAUDE.md`) as the codebase evolves, so the generated documentation doesn't drift from the real project structure.