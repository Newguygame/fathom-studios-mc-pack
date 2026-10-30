#!/usr/bin/env python3
"""Safe server-only mod sync. Called BEFORE NeoForge starts.

Uses generated server-manifest.tsv in the GitHub server branch.
Does nothing if the manifest is empty or downloads fail.
"""
import hashlib
import os
import pathlib
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

REPO = "Newguygame/fathom-studios-mc-pack"
BRANCH = "server"
BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
ROOT = pathlib.Path(__file__).resolve().parent
MODS = ROOT / "mods"
MANIFEST = "server-manifest.tsv"

def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "FathomStudios-NeoForge-Updater/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()

def main():
    try:
        manifest = get(BASE + MANIFEST).decode("utf-8")
        entries = []
        for raw in manifest.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                raise ValueError("manifest requires SHA256<TAB>relative path")
            digest, filename = parts
            rel = pathlib.PurePosixPath(filename)
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
                raise ValueError("invalid SHA256")
            if rel.is_absolute() or ".." in rel.parts or rel.parts[0] != "mods" or rel.suffix.lower() != ".jar":
                raise ValueError("invalid mod path")
            entries.append((digest.lower(), rel, pathlib.Path(filename).name))
        if not entries:
            print("[mods] No reviewed mods listed; leaving installed mods untouched.")
            return 0
        names = [x[2] for x in entries]
        if len(set(names)) != len(names):
            raise ValueError("duplicate mod filename")

        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".servermods-") as temp:
            stage = pathlib.Path(temp) / "mods"
            stage.mkdir()
            for digest, path, name in entries:
                url = BASE + urllib.parse.quote(path.as_posix(), safe="/")
                data = get(url)
                if hashlib.sha256(data).hexdigest() != digest:
                    raise ValueError("checksum mismatch: " + name)
                (stage / name).write_bytes(data)
            # Preserve arbitrary existing mods until the owner opts in to a full managed directory.
            # The updater handles only the manifest-listed files.
            MODS.mkdir(exist_ok=True)
            changed = []
            for digest, path, name in entries:
                destination = MODS / name
                if not destination.exists() or hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                    changed.append(name)
            excluded = ["appleskin-neoforge-mc1.21-3.0.9.jar","athena-neoforge-1.21.1-4.0.6.jar","BadOptimizations-2.4.1-1.21.1.jar","Controlling-neoforge-1.21.1-19.0.5.jar","CrashAssistant-neoforge-1.20.6-1.21.4-1.11.12.jar","fusion-1.3.16-neoforge-mc1.21.1.jar","ImmediatelyFast-NeoForge-1.6.15+1.21.1.jar","MouseTweaks-neoforge-mc1.21-2.26.1.jar","Searchables-neoforge-1.21.1-1.0.2.jar","sodium-neoforge-0.8.13+mc1.21.1.jar","xaerominimap-neoforge-1.21.1-26.6.0.jar","xaeroworldmap-neoforge-1.21.1-1.47.0.jar"]
            managed_file = ROOT / ".server-managed-mods.txt"
            previous = set(managed_file.read_text().splitlines()) if managed_file.exists() else set()
            unwanted = sorted(name for name in (previous - set(names)) | set(excluded) if (MODS / name).is_file())
            if not changed and not unwanted:
                managed_file.write_text("\n".join(sorted(names))+"\n")
                print("[mods] Already up to date.")
                return 0
            backups = ROOT / "mod-backups"
            backups.mkdir(exist_ok=True)
            import datetime
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = backups / stamp
            backup.mkdir(exist_ok=False)
            for name in changed + unwanted:
                destination = MODS / name
                if destination.exists():
                    shutil.copy2(destination, backup / name)
            completed = []
            try:
                for name in changed:
                    os.replace(stage / name, MODS / name)
                    completed.append(name)
                for name in unwanted:
                    (MODS / name).unlink()
            except Exception:
                for name in completed + unwanted:
                    old = backup / name
                    dest = MODS / name
                    if old.exists():
                        shutil.copy2(old, dest)
                    else:
                        dest.unlink(missing_ok=True)
                raise
            managed_file.write_text("\n".join(sorted(names))+"\n")
            print("[mods] Updated", len(changed), "mod(s), removed", len(unwanted), "client-only mod(s); backups in", backup)
        return 0
    except Exception as exc:
        print("[mods] Update skipped; existing mods retained:", exc, file=sys.stderr)
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
