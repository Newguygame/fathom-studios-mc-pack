# NeoForge 1.21.1 — server branch

This branch contains the **server mod selection** (43 JARs), SHA-256-verified manifest, and automatic Raspberry Pi updater. The 12 identified client-only / client-side supporting files have been removed from this branch; main remains unchanged.

## Automatic updates at server startup (Debian Bookworm)

Download `pi-update-server-mods.py` and `start-with-updates.sh` from this branch into your existing NeoForge server folder (the folder containing `run.sh`).

Run these commands **in the NeoForge server folder**:

```sh
chmod +x start-with-updates.sh
./start-with-updates.sh
```

Use `./start-with-updates.sh` on **every subsequent server startup**. Do not use `run.sh` directly if you want the automatic mod check.

### How it works
- Every startup fetches `server-manifest.tsv` from the `server` branch, downloads its listed `mods/*.jar` files and verifies SHA-256 before applying changes.
- Previous versions of changed files and identified client-only JARs are backed up in `mod-backups/`.
- Client-only files from the original modpack are removed from the existing Pi mods directory after successful download validation.
- The server then starts through NeoForge's `run.sh`.
- On download failure, existing mods are retained and the server still starts. Check the console and back up your world before first use.
- Files outside the managed mod names are **not** automatically removed.

### Caveats
Classification is based on bundled mod metadata and typical server-vs-client functionality, **not a successful live boot test**. Custom Create/Aeronautics mods may need further tuning. In particular, verify dependency resolution and MC/NeoForge versions if NeoForge reports an error. The automatic updater does not install NeoForge itself or update the modloader, and does not replace a separate world-backup strategy.
