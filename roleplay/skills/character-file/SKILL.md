---
name: character-file
description: Read, validate, create, and edit HammerAI .character files (roleplay AI character definitions). Use when asked to open or parse a .character file, check it against the section length limits, list/add/edit/delete a section, or write a character file handed over by character-builder. Technical operations only, no creative guidance.
allowed-tools: Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/validate_character.py" *)
---

# Character File Operations

Technical tool for `.character` files used by HammerAI roleplay characters. It reads, writes, validates, and edits sections. It never decides *what* a character should say; that belongs to the `character-builder` skill.

## When to use

- Read or parse an existing `.character` file
- Validate format and length limits (on a file, or on a draft before it is written)
- Write a new file from assembled content (usually handed over by `character-builder`)
- List, add, edit, or delete sections

**Not for:** creating or revising a character creatively (personality, voice, scenario, lorebook content). Use `character-builder`, which calls back into this skill for all file I/O.

## Character File Format

### Name and location

- **The character name is the filename** without the `.character` extension: `Kira Thorne.character` → "Kira Thorne". Max 100 characters.
- Default location: `~/Library/Application Support/HammerAI/RP-CHARS/`. Confirm the path with the user before writing.

### Section headers

Every section starts with a header in this exact format:

```
--- // <Section Name>
```

Nothing may appear before the first header. Content between headers is free-form and passed to the LLM as-is.

### Sections and limits

| Section | Max chars | Notes |
|---|---|---|
| `Introduction` | 80 | One-sentence tagline |
| `Personality` | 4,000 | Traits, appearance, likes/dislikes |
| `Scenario` | 1,800 | Theme, timeframe, opening scene |
| `Example dialogs` | 2,200 | Sample exchanges (format below) |
| `First message` | 1,800 | Opening message of the roleplay |
| `System Prompt` | none | LLM behaviour instructions |
| `Lorebook` | 10,000 | Optional keyword-triggered entries |
| `Author Note` | 2,000 | Optional |
| `Display Name` | 200 | Optional alternative display name |
| `Alternate First Messages` | 10,000 | Optional |

**Required:** `Introduction`, `Personality`, `Scenario`, `Example dialogs`, and `First message`. A missing one is an error. A missing `System Prompt` is a warning.

**Counting rule:** the count covers the section's content with leading and trailing blank lines stripped. It excludes the header and includes inner whitespace and line breaks. Limits are inclusive (80/80 passes).

Other section names are not part of the format. HammerAI will most likely ignore them, so the validator warns about them. Only add a custom section (such as `Abilities`) when the user asks for it explicitly, and tell them about the warning.

### Template variables

- `{{char}}`: replaced with the character name
- `{{user}}`: replaced with the user's name

Any other `{{...}}` is flagged.

### Example dialogs

```
#{{user}}: *leans on the bar* "Busy night?"
#{{char}}: *Esmeralda doesn't look up from the glass she's polishing.* "Always is."
```

- Every dialog line starts with `#{{user}}:` or `#{{char}}:`
- Actions and narration go in asterisks, speech goes in quotes
- Separate exchanges with a blank line

### Personality labels

The `Personality` section usually uses labels such as `Appearance:`, `Personality traits:`, `Likes:`, `Dislikes:`. These are **conventional, not enforced**. Preserve whatever structure the file already uses.

### Lorebook

One entry per line:

```
trigger terms, comma separated | description injected when a term appears
```

**How entries fire:**
- The last 4 messages (2 user and 2 character) are scanned for terms, case-insensitive, with **partial matching**: `fire` matches "fireball".
- A hit injects the description into the prompt once, with no framing. Several matching terms still give one insertion.
- Entries fire independently. Descriptions are not scanned, so lore never triggers other lore.

**Format rules** (the validator enforces them):
- ` | ` (space, pipe, space) separates terms from description. Error if missing.
- At least one term and a non-empty description. Error if missing.
- Lowercase terms, max 10 per entry. Warning.
- Terms under 4 characters partial-match inside common words (`gar` → "garden", "cigar"). Warning.
- The description should echo at least one of its terms. Warning.
- Terms that appear in more than one entry. Warning: check that it's intentional.

Whether each description *reads well on its own* is a content question. `character-builder` owns that.

## Validation: always use the script

Never count characters by hand or estimate them. Run the bundled validator:

```bash
# Existing file (name = filename stem)
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_character.py" "/path/to/Kira Thorne.character"

# Draft that is not written yet
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_character.py" --stdin --name "Kira Thorne" <<'EOF'
--- // Introduction
...
EOF
```

Claude Code substitutes `${CLAUDE_SKILL_DIR}` with this skill's directory when it loads the skill. It is not a shell variable, so use the command exactly as written.

It prints per-section counts against the limits, then errors and warnings, then `Status: VALID|INVALID`. Exit code 0 means valid (warnings allowed), 1 means errors. Relay its output. Don't paraphrase counts.

## Operations

| Operation | How |
|---|---|
| **Read** | Read the file, then show its sections in order, exactly as stored. Run the validator and append its summary. |
| **List sections** | Run the validator. The `Sections:` line lists them in order. |
| **Write new** | Confirm the path and filename (= character name). Validate the content with `--stdin` **first**. If there are errors, stop and report them. Otherwise write with the Write tool and validate the written file. |
| **Add section** | Check that the section doesn't exist yet. Append `--- // <Name>` plus content at the end (or where the user asks). Leave the other sections untouched. Validate. |
| **Edit section** | Read the file. Replace only that section's content with the Edit tool, keeping the header. Validate. |
| **Delete section** | Remove the header and everything up to the next header. Validate. |
| **Validate** | Run the script and relay its output. |

Rules for every operation:
- Preserve the content exactly as given. No automatic reformatting or "corrections".
- For reads, edits, and deletes, the file must exist. For writes, the parent directory must exist.
- After any change, re-run the validator and show the result.

## Errors

- **File not found:** "Character file not found at [path]."
- **Section already exists** (add): "Section '[name]' already exists. Use edit to change it."
- **Section not found** (edit/delete): "Section '[name]' not found. Available: [list]."
- **Validator errors on write:** don't write. Report the errors and hand them back to the caller (usually `character-builder`) for trimming or fixing.
- **Malformed file:** parse on a best-effort basis, report the validator's errors, and suggest fixes.

## Example Character File

`Mara Vell.character`:

```
--- // Introduction

Sarcastic mercenary seeking redemption by protecting those she once hunted.

--- // Personality

Appearance: human, female, 28, auburn hair, green eyes, athletic build, scar across her left cheek.
Personality traits: brave, loyal, sarcastic, protective, slow to trust.
Likes: sword drills, honest people, strong ale.
Dislikes: cowardice, deception, idle nobility.

--- // Scenario

Theme: adventure, friendship.
Timeframe: medieval fantasy, the Kingdom of Aldoria.
Writing quality: direct narrative, witty dialogue.
Scene: {{char}} sits alone at a table in the Rusty Nail tavern, cleaning her sword, when {{user}} enters.

--- // Example dialogs

#{{user}}: "Mind if I join you?"
#{{char}}: *Mara looks up from her blade, one eyebrow raised.* "Depends. You looking for trouble or trying to avoid it?"

#{{user}}: "Just looking for company."
#{{char}}: *She nudges the empty chair out with her boot.* "Fair enough. Sit. But if you're boring, I'm leaving."

--- // First message

*The door of the Rusty Nail swings open and Mara's hand drifts to her sword's pommel. After a moment's assessment she goes back to cleaning the blade.* "Either sit or stop hovering. You're blocking the light."

--- // System Prompt

You are {{char}}. Never write actions, speech, or thoughts for {{user}}. Actions go in asterisks, speech in quotes. Keep Mara witty, guarded, and quietly protective.

--- // Lorebook

mara's sword, longsword, runeblade | Mara's sword is a runeblade longsword taken from the knight she failed to protect. Its runes glow faintly in moonlight, and she never lets anyone else hold it.
rusty nail, tavern | The Rusty Nail is the busiest tavern in Aldoria's merchant district, where mercenaries find work, strong ale, and the occasional brawl.
aldoria, kingdom, crown | The Kingdom of Aldoria has stood for three centuries under House Blackwood. Border tensions have filled its towns with soldiers and sellswords.
```

## Working with character-builder

`character-builder` decides *what* to write. This skill performs every file operation it needs:

- **New character:** the builder hands over the assembled content and a name. Validate with `--stdin`, then write `<Name>.character`.
- **Refining an existing character:** the builder asks for a read and a validation, then hands back the changed sections one at a time for editing.
- **Drafts:** the builder can ask for a `--stdin` validation at any point to get exact counts.
