# Persistence

## Overview

DChatty persists QA runtime state so the latest uploaded PDF vector store can be restored after restart.

## Storage Layout

- Primary file: `data/qa_state.pkl.gz`
- Backup directory: `data/backups/`
- Legacy format support: `data/qa_state.pkl` (auto-migrated when detected)

## Save Strategy

State is saved with:

1. Gzip compression
2. Atomic write via temporary file + move
3. Backup creation when overwriting existing state
4. Backup rotation (keeps the most recent 5 backups)

## Load Strategy

On startup/load:

1. Try `data/qa_state.pkl.gz`
2. If invalid/corrupt, attempt latest backup recovery from `data/backups/`
3. If primary format does not exist, attempt legacy `data/qa_state.pkl` and migrate

Only valid state objects containing `vector_store` are restored.

## Limitations

- Current design stores only the most recently processed PDF state.
- Multi-document persistence is not part of the current implementation.

## Troubleshooting

1. Corrupt primary state:
   - App attempts backup recovery automatically.

2. Corrupt backup chain:
   - Remove stale files in `data/` and re-upload a PDF.

3. Permission errors:
   - Ensure process can read/write the `data/` directory.
