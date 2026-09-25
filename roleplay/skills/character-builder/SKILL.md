---
name: character-builder
description: Interactive character creation and revision for HammerAI roleplay characters. Creative partner for developing personalities, backstories, voice, scenarios, and lorebooks. Use for building a new character, fleshing out a concept, drafting a complete .character file, or improving an existing character's writing.
---

# Character Builder

Creative partner for building and refining roleplay characters. It guides the user through progressive phases, offers options instead of forms, and gives honest feedback on coherence and depth.

## Scope

**Use for:**
- Building a new character from a rough idea or a detailed concept
- Revising an existing character's content (see *Refine mode*)
- Designing lorebook entries

**Not for:** purely technical file work such as reading a file, validating it, or renaming a section. Use `character-file` for that.

**File I/O boundary:** this skill never reads or writes files itself. Every read, validation, write, and edit goes through the `character-file` skill.

## Modes

Pick a mode from what the user gives you. Say which mode you're using in one line.

- **Guided** (default when the input is thin, like "a sci-fi hacker?"): walk through the phases below one at a time. Offer 3–4 options per phase and ask focused questions.
- **Quick draft** (when the user gives a rich concept, or asks for a draft): write every section in one pass, run the Phase 8 checks, then iterate on whatever the user wants changed. Don't force them through phases they've already answered.
- **Refine** (when the user points at an existing `.character` file): ask `character-file` to read and validate it. Assess it against the Craft rules and the Phase 8 checks. Propose which phases need work, run only those, and hand each changed section back to `character-file` as an edit.

## Tone

- Warm but honest. Tie feedback to specifics ("the betrayal turns 'doesn't trust' into a concrete wound"), never generic praise ("I love this!").
- Name clichés plainly and offer a sharper alternative. Keep them if the user wants them.
- Validation is collaborative: suggestions, not requirements.
- See `references/example-build.md` for the target tone.

## Limits and counting

The section limits live in the `character-file` skill (the Introduction's 80 characters is the one that constrains a phase directly). The name is the **filename** and must be under 100 characters.

- While drafting, show **approximate** sizes only, marked with `~` (`~1,200/1,800`). Don't present exact counts you haven't measured.
- For exact counts, ask `character-file` to validate the draft (it runs its script on stdin). Do this before the final handoff, and whenever a section looks close to its limit.
- When a section runs over, propose specific cuts that keep the character's essence. Repeated facts are the first thing to cut (see Craft rules).

## Phases

Each phase builds on the previous one. The user can be as detailed or as loose as they want. Fill gaps together.

### 1. Concept

Establish the hook: genre and setting, core archetype, and the one thing that makes this character interesting. A placeholder name is fine.
Ideas: `references/archetypes.md`.

### 2. Tagline (Introduction, max 80 chars)

One sentence that captures essence plus conflict and would make someone stop scrolling. Check that it's specific and not generic.
Formulas: `references/archetypes.md`.

### 3. Appearance

Species/type, age and build, distinctive features (scars, eyes, objects they carry), clothing, how they move. Prefer features that *tell a story* or work as visible tells in play.
Ideas: `references/traits-and-voice.md`.

### 4. Personality

3–5 core traits (surface and depth), the key contradiction, goals, what blocks them, and want vs need. Test each contradiction: does it create tension, or only confusion?
Ideas: `references/traits-and-voice.md`.

### 5. Voice

Formality, vocabulary, sentence structure, verbal quirks, physical mannerisms and emotional tells, and how all of these shift under stress. The voice is *demonstrated* in Example dialogs, which the model copies.
Ideas: `references/traits-and-voice.md`.

### 6. Backstory & Scenario

Origin, formative events and relationships, where and when the roleplay starts, the tone, and the relationship dynamic with `{{user}}`. The scenario should engage the character's goals and wound, not only place them somewhere.
Ideas: `references/scenario-hooks.md`.

### 7. Lorebook *(optional)*

Skip this phase for characters whose world needs no on-demand context.

**How a lorebook fires:** it's a string trigger that injects text. The last 4 messages are scanned for trigger terms (case-insensitive, **partial match**). On a hit, the description is dropped into the prompt once, **with no framing**. The model is never told why the text appeared. Lore never triggers other lore.

**Four traps to write against:**

1. **Anchor every description.** It arrives out of context, so it has to stand alone: name the subject, and leave no pronouns that point to nothing.
   - ❌ `harpoon | She keeps them meticulously clean — sloppy kills leave evidence.`
   - ✅ `harpoon, arm blades, armblades | Rayne's weapons: paired Carpathian arm-blades folded into her gauntlets, plus a harpoon. She keeps them meticulously clean — sloppy kills leave evidence.`
2. **Echo the trigger terms in the description**, so the text anchors to whatever summoned it and keeps re-triggering while the topic continues.
3. **No dead-end references.** Lore can't cascade, so any proper noun a description relies on needs its own entry or an inline explanation.
4. **Put persistent facts elsewhere.** Lore unloads when its term leaves the window. Always-true traits belong in Personality or System Prompt.

**Choosing terms:** use words users and the model actually type, including variants and misspellings (`arm blades`/`armblades`). Avoid short or common terms, because partial matching means `art` fires on "smart". Stick to lowercase and at most ~10 terms per entry.

Capture entries as `terms | description`. `character-file` owns the exact syntax checks.

### 8. Validation

**Coherence checks:**
1. **Appearance ↔ backstory:** do scars, marks, and style have a reason?
2. **Personality ↔ voice:** does the speech match the traits (educated → vocabulary, shy → hesitation)?
3. **Goals ↔ scenario:** does the opening situation engage what they want and what blocks them?
4. **Contradictions:** interesting (surface vs depth, want vs need, past vs present) or problematic (illogical, unexplained shifts, extreme traits without support)?
5. **Lorebook** (if present): every description stands alone, echoes a term, has no dead-end proper nouns, contains no always-true facts, and uses no false-positive-prone terms.
6. **Craft rules** below.

Put questions in this form: "I notice [X] but [Y]. Intentional, or should we align them?" Suggest one or two creative opportunities: unexplored depth, a growth arc from want vs need, scenes that would challenge the character.

Then get exact counts from `character-file` and fix anything over its limit.

## Craft rules

These apply to every mode and are checked in Phase 8:

- **Never act for {{user}}.** The First message and Example dialogs must not narrate `{{user}}`'s actions, words, thoughts, or feelings. The model copies these sections, and a first message that moves `{{user}}` teaches it to keep doing that. End the first message on an opening that `{{user}}` can answer.
- **Examples set the style.** Example dialogs set the reply length, point of view, and tense the model will imitate. Keep them consistent with the First message and with the length of reply you want.
- **Say each fact once.** Don't repeat the same fact across Personality, Scenario, and System Prompt. Each copy costs budget and adds nothing.
- **Show the voice, don't label it.** "Sarcastic" in Personality is weaker than one sarcastic line in the Example dialogs. Use both, but lean on the demonstration.
- **System Prompt is for behaviour**, such as format rules, boundaries, and emotional range. Not for backstory.

## Output format

Assemble the content in this structure. It's content only: `character-file` writes it.

```
--- // Introduction

[Tagline: essence + conflict, max 80 chars]

--- // Personality

Appearance: [species, age, build, distinctive features, clothing, how they move]
Personality traits: [3-5 core traits, key contradiction]
Background: [origin, formative events and relationships]
Likes: [motivations, passions, values]
Dislikes: [fears, what they avoid, boundaries]

--- // Scenario

Theme: [adventure, romance, mystery, ...]
Timeframe: [setting, era, world]
Writing quality: [tone, pacing, description level]
Scene: [where {{char}} meets {{user}} and what is at stake]

--- // Example dialogs

#{{user}}: *sets a data chip on the table* "Heard you're the best."
#{{char}}: *Her cybernetic eye flickers blue as it scans the chip.* "Heard wrong. I'm the only one still taking jobs. Talk."

[3-4 exchanges total, each showing voice, a mannerism, or a contradiction]

--- // First message

[Opening narration in the character's scene. Sets tone and atmosphere and reveals the character through action. Never narrates {{user}}. Ends with something {{user}} can respond to.]

--- // System Prompt

You are {{char}}. Never write actions, speech, or thoughts for {{user}}. Actions go in asterisks, speech in quotes. [Key traits and contradiction to maintain, voice quirks, emotional range, boundaries, thematic focus.]

--- // Lorebook

[Only if Phase 7 produced entries; otherwise omit the section entirely.]
[lowercase terms, variant, misspelling | Self-contained description that names its subject and echoes a term.]
```

## Handoff

Present a summary:

```
**Character:** [Name] (becomes the filename: [Name].character)
**Introduction:** [Tagline]
**Concept:** [one-line hook]
**Personality:** [3 core traits + key contradiction]
**Voice:** [speech pattern summary]
**Setting:** [scenario in one line]
**Lorebook:** [N entries / none]

Validator: [VALID/INVALID, with the per-section counts exactly as character-file reported them]

[Honest assessment: what's strong, and what (if anything) is still thin.]

Ready to write the file?
```

**If yes:**
1. Confirm the target path. The default comes from `character-file`, and the filename is `<Name>.character`.
2. Invoke `character-file` to write it, passing the assembled content and the path.
3. Relay its validation result. If it refuses because of errors, fix them with the user and try again.

**If no:** return to the relevant phase, then present the summary again.

**Refine mode handoff:** the same flow, but each changed section is sent to `character-file` as a section edit, not a full rewrite.
