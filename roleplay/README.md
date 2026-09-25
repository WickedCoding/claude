# Roleplay - AI Character Building Suite

Skills for creating and managing HammerAI roleplay characters (`.character` files).

## Skills

- **character-builder**: creative partner for building characters. It offers a guided phase-by-phase mode, a quick-draft mode for rich concepts, and a refine mode for improving existing characters, including lorebook design.
- **character-file**: technical operations on `.character` files: read, validate, write, and add/edit/delete sections. A bundled script (`scripts/validate_character.py`) checks format and section length limits exactly.

The builder never touches the filesystem. All reads, writes, and validation go through character-file.

### Validating a file directly

```bash
python3 roleplay/skills/character-file/scripts/validate_character.py "path/to/Name.character"
```

The character name is the filename. Exit code 1 means the file has errors.

## Installation

```bash
/plugin marketplace add https://github.com/WickedSik/claude.git
/plugin install roleplay@wickedsik
```

## Planned

- Narrative tools: scene narration and dialogue coaching
- Roleplay output styles for staying in character

## License

MIT, see [LICENSE](../LICENSE).
