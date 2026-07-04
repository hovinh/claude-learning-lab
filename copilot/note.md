# GitHub Copilot Chat: Practical Usage Guide

A working reference for using GitHub Copilot Chat effectively in VS Code, based on hands-on notes. Intended for internal wiki use — some GitHub Copilot features are in active development, so revisit the official docs periodically for changes.

## 1. Chat Modes

Copilot Chat offers a mode dropdown at the bottom of the chat view. Available modes vary slightly by IDE (VS Code vs. Visual Studio), but the general set is:

| Mode | Purpose |
|---|---|
| **Ask** | Answers coding questions using your current editor context. No code is changed. Good for explanations, refreshers on syntax/libraries, or "how do I..." questions. |
| **Edit** | You select the files to change, describe the update in natural language, and Copilot applies inline, review-ready edits across just those files. |
| **Agent** | Give a high-level goal. Copilot autonomously plans steps, picks files, runs terminal commands/tools, and iterates until the task is done. Most powerful, least predictable — review before accepting. |
| **Plan** | Copilot explores the codebase, asks clarifying questions, and produces a reviewable implementation plan *before* any code changes happen. Useful when you want to sanity-check the approach before letting Agent mode loose. |

**Practical tips:**
- Pick the effort/mode level according to task complexity — don't default to Agent mode for a one-line question.
- You can inspect and selectively keep or discard individual changes rather than accepting everything at once.
- Use a **separate chat session per task/feature** to avoid context pollution from unrelated earlier conversation.
- Tackle **one feature at a time** rather than five at once — smaller scope is easier to review and verify.
- There's a small context-usage indicator (pie-chart-style icon) in the chat view showing how much of the context window has been consumed.
- You can **restore a checkpoint** to undo a change if Copilot's edit isn't what you wanted.

## 2. Adding Context to a Prompt

Ways to bring relevant context into a chat request:

- **`#` references** — attach a specific file, e.g. `#index.html`, or use `#file:` and pick from a list. `#selection` references the currently selected code.
- **`@` domain selectors** — scope the question to a specific context provider, e.g. `@workspace` (whole project structure), `@vscode` (editor settings/commands), `@terminal` (terminal output/commands).
- **Inline chat** — highlight a code snippet directly in the editor and ask a question or request a change without opening the full chat panel.
- **Terminal selection** — you can also highlight text in the integrated terminal and ask about it.
- **Image attachments** — attach a screenshot or mockup as context, useful for asking Copilot to match or update a UI design.
- **Browser mode** — in VS Code you can open a browser preview and highlight specific rendered UI components to reference them in chat.
- **Slash commands** — see below.

## 3. Slash Commands

Slash commands (`/command`) trigger pre-built prompts for common tasks without retyping instructions each time (e.g. setup, generating unit tests, `/explain` on selected code).

- Commands can be scoped — the same command name may exist under different domains/tools, so check which one is being invoked.
- You can combine a slash command with a highlighted code selection (e.g. select a function, then run `/explain`).

## 4. Custom Instructions

Custom instructions let Copilot automatically apply context/preferences to every request without you retyping them.

| File | Scope | Auto-applied? |
|---|---|---|
| `.github/copilot-instructions.md` | Whole repository, all requests | Yes — always included automatically in every chat request for that repo. |
| `.github/instructions/*.instructions.md` | Specific files/folders, defined via an `applyTo` glob pattern in the file's frontmatter | Yes, but **only when the files being worked on match the `applyTo` pattern** — it is not "everything under `.github/instructions` is always in context." Unmatched instruction files are ignored. |
| `AGENTS.md` (repo root) | Cross-tool convention (also recognized by VS Code) | Yes, similar to `copilot-instructions.md`, but not GitHub Copilot–specific — other AI coding tools (Copilot, Cursor, etc.) also look for this file, making it a good choice if your team uses more than one AI tool. |

**Two conventions for organizing instructions across multiple AI tools:**
- **Unofficial (cross-tool):** keep instruction content in separate Markdown files under a `/docs` directory, and reference them explicitly (e.g. via `#docs/api-standards.md`) since not every tool auto-loads arbitrary folders.
- **Official (GitHub Copilot–specific):** use the structured `.github/agents` and `.github/prompts` folders described below.

You can either write instruction files by hand or ask Copilot Chat to generate one for you from your existing codebase conventions.

## 5. Custom Agents and Prompt Files (GitHub Copilot–specific)

| | Custom Agents | Custom Prompt Files |
|---|---|---|
| **What it is** | A specialized, named version of Copilot with a restricted/defined set of tools, instructions, and MCP servers it's allowed to use. | A reusable prompt template for a specific, repeatable task. |
| **File location** | `.github/agents/*.agent.md` | `.github/prompts/*.prompt.md` |
| **How it's created** | "Create new agent" in the Copilot UI, then name it. | Create the `.prompt.md` file directly, or ask Copilot Chat to generate one. |
| **How it's invoked** | As a slash command, via the `agent:` field set in its frontmatter. | As a slash command, or by attaching the prompt file to a chat request (Attach context → Prompt...). |
| **Best for** | Tasks where you want to constrain *what the agent is allowed to touch or use* — e.g. a "docs-only" agent, a "refactor-specialist" agent. | Tasks where the *instructions themselves* are what you keep repeating — e.g. "generate a create-instructions prompt," "scaffold a new test file." |

**Bootstrapping pattern:** create a `create-instructions` custom prompt/agent whose job is to generate new `*.instructions.md` files under `.github/instructions` (or `/docs`) whenever you need a new standard captured. Reference the resulting file with `#filename.md` in future prompts.

**Sample references** (community example repo):
- [AGENTS.md example](https://github.com/tomphill/linkshortenerproject/blob/main/AGENTS.md)
- [Example prompt file](https://github.com/tomphill/linkshortenerproject/blob/main/.github/prompts/create-instructions.prompt.md)
- [Example custom agent](https://github.com/tomphill/linkshortenerproject/blob/main/.github/agents/instructions-generator.agent.md)

## 6. Source Control Integration

In the **Source Control** tab in VS Code, there's a "magic" icon next to the commit message box that generates a commit message from your staged changes automatically.

## 7. Background / Cloud Agents

- The right-arrow icon in the chat view sends a task to run in the **background/cloud** rather than interactively in your editor.
- This creates a new branch and works on the change independently — it can take longer than an interactive Agent-mode session, but multiple background tasks can run in parallel, so you can queue up several independent pieces of work at once.
- You can also trigger cloud tasks by installing the **GitHub Copilot app** and assigning a GitHub issue directly to Copilot, or asking it to open a pull request.
- Review the diff on the resulting branch/PR before merging, same as you would a human contributor's PR.

## 8. Model Context Protocol (MCP)

MCP (Model Context Protocol) is a standard that lets Copilot Chat connect to external tools and services (databases, ticketing systems, design tools, etc.) and call them as part of a conversation. Once an MCP server is configured, its tools become available for Copilot to invoke directly in Agent mode — useful for integrating your team's existing systems (Jira, internal APIs, etc.) into the AI workflow.

## 9. Hooks

Hooks live under the `.github` folder and let you extend/customize agent behavior by running custom shell commands at defined points in the agent's execution lifecycle.

- Example: a **`postToolUse`** hook that runs after every code-generation step, automatically invoking your code formatter/linter so all Copilot-generated code conforms to your formatting rules without manual cleanup.

## 10. Sub-agents / Orchestration

- **Sub-agents** are isolated agent instances with their own context window, spun up to handle a delegated piece of work (e.g. research, a specific refactor, writing tests for one module) without cluttering the main chat session.
- They run independently and report back a result/status to the main session rather than pausing for feedback mid-task.
- Sub-agents can be invoked **automatically** (Copilot decides based on the task description and available custom agents) or **directly** (e.g. "use the testing subagent to write unit tests for the authentication module").
- Useful for orchestrating multiple pieces of a larger task in parallel — each sub-agent tackles one slice and reports success/failure.

## 11. Agent Skills

Agent Skills are folders of instructions, scripts, and resources that Copilot can pull into context **only when relevant** to the task at hand.

- **Key difference from MCP:** MCP tools are front-loaded into context at the start of a session (all tool definitions are always present). Skills instead expose only a short description up front; the model decides whether a skill is relevant, and only then pulls in the fuller instructions/scripts/resources.
- This makes skills more context-efficient for narrow, specialized capabilities that aren't needed on every request.
- Reference: [skills.sh](https://skills.sh) for browsing available skills.
- Prefer skills from reliable providers (e.g. Anthropic) for quality and safety. For building your own, a `skill-creator` skill is available to scaffold new custom skills.

## 12. Choosing the Right Customization Mechanism

| Mechanism | When to use it |
|---|---|
| **Custom Agents** | When you need to restrict or manage which tools an agent has access to for a specific type of task. |
| **Custom Prompts** | When you find yourself typing the same prompt over and over — turn it into a reusable, invokable template. |
| **Agent Skills** | When you want a **determined, repeatable outcome/output** for a specialized task, loaded only on demand. |
| **Custom Instructions** | When you want to **influence style/standards** generally (e.g. coding conventions with example snippets), without requiring one fixed output. |

## 13. Other Notes

- For web app / frontend UI work, [shadcn/ui](https://ui.shadcn.com) is a commonly paired component library when prompting Copilot to scaffold UI.
- Separate the different architectural layers of your application clearly (e.g. API, service, data access) — this makes it much easier for Copilot Chat to understand where a change belongs and to follow your coding standards consistently.

---

## Tips & a Good Corporate Workflow

**General tips:**
- Start new tasks in **Ask** or **Plan** mode to explore/clarify before switching to **Agent** mode to execute — cheaper to catch a wrong approach before code changes start.
- Keep tasks scoped to one feature or bug per chat session. Large, multi-concern prompts are harder to review and more likely to produce unwanted side effects.
- Treat Agent-mode output like a junior developer's PR: review the diff, run tests, don't blindly accept.
- Use checkpoints/restore liberally when experimenting — it's cheaper to roll back than to untangle a bad multi-file edit manually.
- Watch the context-usage indicator; if it's climbing fast, start a new session rather than letting quality degrade from context dilution.
- Use background/cloud agents for well-defined, lower-risk tasks (dependency bumps, boilerplate, test scaffolding) so you can keep working interactively on higher-judgment tasks in parallel.

**A workflow that works well inside a corporate/team setting:**

1. **Establish shared standards first, not ad hoc.** Before teams start relying on Copilot day-to-day, commit a baseline `.github/copilot-instructions.md` (or `AGENTS.md` if the team also uses other AI tools) with architecture conventions, layering rules, and testing expectations. Store it in version control so it's reviewed like any other code and stays in sync with the codebase.
2. **Layer in path-specific instructions as the codebase diversifies.** Add `.github/instructions/*.instructions.md` files scoped with `applyTo` for language- or module-specific rules (e.g. Python service layer vs. frontend components) rather than growing one giant instructions file.
3. **Turn repeated prompts into custom prompt files or custom agents** and commit them alongside the code. This turns "how we ask Copilot to do X" into a shared, reviewable team asset instead of tribal knowledge in someone's head.
4. **Gate risky or destructive actions with hooks and custom agent tool restrictions**, especially for agents that might run in less-supervised background/cloud mode — e.g. auto-format on every generation, or restrict a "docs-only" agent from touching source files.
5. **Use Plan mode (or Ask mode + manual review) for anything touching shared infrastructure, security, or public APIs**, and reserve autonomous Agent/cloud mode for lower-blast-radius, well-tested areas of the codebase.
6. **Review AI-authored PRs with the same rigor as human PRs** — use Copilot code review as a first pass, but treat it as a supplement to, not a replacement for, human sign-off, particularly early on while trust in the workflow is being established.
7. **Iterate on the instructions/skills library as a living asset.** When Copilot repeatedly gets something wrong in the same way, that's a signal to add or refine an instruction file, prompt, or skill — treat it the same way you'd treat updating a team style guide after a recurring code review comment.
8. **Keep an internal "customization library" page** (this wiki is a good place) listing which custom agents, prompts, and skills exist, what they're for, and who owns them — so the tooling doesn't sprawl into duplicated, inconsistent instructions across repos.