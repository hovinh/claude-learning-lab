Implementation begins with Project setup, then progresses to navigation, targeted refactors, and full-scale operations.

## Step 1: Ingesting the codebase into a project

Process:
- Create a dedicated Project. "Next.js E-commerce Refactor".
- Upload repository (zip the root directory) or connect Github for auto-sync.
- Add custom instruction:
```
You are refactoring a large Next.js 15 monorepo.
- Use App Router exclusively.
- Enforce tRPC for type-safe APIs.
- All components use shadcn/ui and Tailwind.
- Maintain 95% test coverage.
- Never break existing types.
```
- Let Claude index: Prompt "Summarize the overall architecture and key dependencies.", Given Claude responds with a structured overview, it primes subsequent reasoning.

## Step 2: Navigating large codebase with Semantic search pattern

Direct file-by-file requests fail at scale. Instead, use discovery/navigation prompts.

- Architecture Map
```
Create a high-level architecture diagram (text-based) of this codebase.
List major directories, their responsibilities, and key data flows.
```

- Dependency Graph
```
Trace all imports of '@/lib/auth' across the codebase.
List files that use it and how (direct import, hook, middleware).
```

- Semantic Search
```
Find all places where we manually validate user input with Zod.
Suggest consolidation into shared schemas.
```

## Step 3: Artifacts for Iterative Multi-file Editing

Artifacts are the bridge from planning to implementation. Prompt pattern for artifact generation:
```
Analyze the codebase and propose a multi-file refactor to migrate from React Query to tRPC.

Output as an Artifact with:
- Directory tree showing affected files
- Diff previews for each change
- Explanation of why each change is necessary
- Migration plan with verification steps

Use Git-style diffs. Preserve all existing functionality.
```

## Step 4: Apply this change across the entire codebase patterns

```
Task: {CLEAR DESCRIPTION OF CHANGE}

Follow this process:
1. <search> Identify ALL files and locations that need this change. Be exhaustive.
2. <plan> Detailed plan per file/group, handling variations in implementation.
3. <implement> Output as Artifact with precise diffs for each affected file.
4. <verify> Suggest tests or manual checks to confirm no regressions.

Constrains:
- Never hallucinate new files
- Preserve existing comments and formatting
- Handle edge cases differently if needed
- Group similar changes

Change: {SPECIFIC PATTERN OF INTENT}
```

# Best Practices

- Always start with discovery: never assume structure.
- Use Artifacts religiously: text diffs are error-prone at scale.
- Break large refactors into phases: Auth, UI, then tests.
- Verify incrementally: run proposed tests after each Artifact application.
- Over-ambitious prompt yields shallow changes.
- Always demand verification steps.