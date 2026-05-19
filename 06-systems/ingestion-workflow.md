# Ingestion Workflow

## Summary
How to ingest new sources into the Second Brain vault. Step-by-step process for converting raw information into structured, linked knowledge.

## Workflow

### Step 1: Classify
Determine type: project update, new knowledge, architecture decision, research, bug, operational.

### Step 2: Choose Location
| Type | Folder |
|------|--------|
| Unprocessed | `00-inbox/` |
| Project-specific | `01-projects/{project}/` |
| Long-term responsibility | `02-areas/` |
| Reusable knowledge | `03-knowledge/` |
| Architecture decision | `04-decisions/` |
| System/workflow | `06-systems/` |
| Deprecated | `08-archive/` |

### Step 3: Write Note
Use standard structure from `CLAUDE.md`. Fill relevant sections only. Keep under 200 lines.

### Step 4: Cross-Link
- Add `[[wikilinks]]` to related pages
- Check `index.md` for existing pages on similar topics
- If page covers same topic as existing: UPDATE, don't create new

### Step 5: Update Index
Add one-line entry to `index.md` under correct section with `[[wikilink]]`.

### Step 6: Update Log
Append: `## [YYYY-MM-DD] type | title` with summary of what was ingested and why.

### Step 7: Review
- Did I duplicate existing knowledge?
- Is this note findable from the index?
- Will future AI understand WHY this matters?

## Rules
- Never ingest without classifying
- Never create without searching existing first
- Never leave orphan pages (always link)
- Always explain WHY in the note

## Related
- [[ai-workflows]]
