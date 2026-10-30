# NeoForge server branch

This branch holds the deployment tooling for **Debian 12 Bookworm**.

## Important
The branch was created from `main`. **Existing mod files inherited from main have not yet been assessed for server compatibility.** Do not copy every mod from this branch into the server.

Only files explicitly entered into `server-manifest.tsv` are downloaded by the Pi updater. Each entry is a reviewed server-compatible `.jar` in the form `SHA256<TAB>mods/filename.jar`. The manifest starts empty to prevent accidental installation of client-only mods.

## Raspberry Pi startup

Place `pi-update-server-mods.py` in the NeoForge server directory (alongside `run.sh`), then use this wrapper as your launcher command:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 pi-update-server-mods.py
exec bash ./run.sh nogui
```

The updater downloads and checks all listed mods before replacing any. Changed existing files are backed up in `mod-backups/`. If downloads or validation fail, the current installation is preserved and the server continues to start.

**Updates happen only at server startup.** The updater does not remove unlisted mods, so removing/renaming a mod in the GitHub manifest currently requires a manual cleanup. Stop the server before replacing the scripts. Keep world backups separately.
