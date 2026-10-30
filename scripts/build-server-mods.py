#!/usr/bin/env python3
"""Build server mod directory from main. Unknown mods are included by default."""
from pathlib import Path
import hashlib, json, shutil, zipfile
SOURCE=Path("mods")
TARGET=Path("server-worktree/mods")
MANIFEST=Path("server-worktree/server-manifest.tsv")
CLIENT_NAMES={"appleskin","athena","badoptimizations","controlling","crashassistant","fusion","immediatelyfast","mousetweaks","searchables","sodium","xaerominimap","xaeroworldmap"}
def client_only(path):
    stem=path.stem.lower().replace("_","").replace("-","")
    if any(stem.startswith(x) for x in CLIENT_NAMES):
        return True
    try:
        with zipfile.ZipFile(path) as jar:
            if "META-INF/neoforge.mods.toml" in jar.namelist():
                # NeoForge side-only mods are normally specified by displayTest,
                # but displayTest=IGNORE_SERVER_VERSION does not mean client-only.
                pass
            if "fabric.mod.json" in jar.namelist():
                data=json.loads(jar.read("fabric.mod.json"))
                if data.get("environment")=="client":
                    return True
    except (OSError,ValueError,zipfile.BadZipFile):
        print("WARNING: unreadable JAR metadata, including as unknown:",path)
    return False
def main():
    if not SOURCE.is_dir():
        raise SystemExit("Missing mods/ on main; refusing to modify server")
    TARGET.mkdir(parents=True,exist_ok=True)
    selected=[]
    excluded=[]
    for src in sorted(SOURCE.glob("*.jar")):
        if client_only(src):
            excluded.append(src.name)
        else:
            selected.append(src)
    if not selected:
        raise SystemExit("No server mods selected; refusing empty deployment")
    # Sync only the JARs in the dedicated server mods directory.
    expected={p.name for p in selected}
    for old in TARGET.glob("*.jar"):
        if old.name not in expected:
            old.unlink()
    lines=["# SHA256<TAB>mods/filename.jar; generated from main, unknown mods included"]
    for src in selected:
        dst=TARGET/src.name
        if not dst.exists() or hashlib.sha256(dst.read_bytes()).digest()!=hashlib.sha256(src.read_bytes()).digest():
            shutil.copy2(src,dst)
        lines.append(f"{hashlib.sha256(src.read_bytes()).hexdigest()}\tmods/{src.name}")
    MANIFEST.write_text("\n".join(lines)+"\n")
    print(f"Selected {len(selected)} server mods, skipped {len(excluded)} client-only")
    for name in excluded: print("SKIP",name)
if __name__=="__main__": main()
