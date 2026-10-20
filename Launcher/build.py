#!/usr/bin/env python3
"""Build and ad-hoc sign the Valhall launcher for CodeExp2, without launching it."""
import os
import hashlib
import json
import math
from pathlib import Path
import plistlib
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
APP = BUILD / "CodeExp2.app"
MACOS = APP / "Contents/MacOS"
RESOURCES = APP / "Contents/Resources"


def run(*args):
    subprocess.run([str(a) for a in args], check=True, cwd=ROOT)


def toml_value(value):
    """Serialize the profile's values without interpreting or copying policy."""
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + "=" + toml_value(v)
                              for k, v in sorted(value.items())) + "}"
    if isinstance(value, list):
        return "[" + ",".join(toml_value(v) for v in value) + "]"
    if isinstance(value, (str, bool, int)) or isinstance(value, float) and math.isfinite(value):
        return json.dumps(value, ensure_ascii=False)
    raise ValueError(f"Unsupported profile value: {type(value).__name__}")


def panel_profile(source):
    values = tomllib.loads(source.decode("utf-8"))
    arguments = []
    for key, value in sorted(values.items()):
        # Native CLI override paths split on dots and retain quote characters.
        # Top-level assignments with TOML inline tables preserve plugin IDs and
        # recursively merge with inherited config as native profile layers do.
        if not key or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in key):
            raise ValueError("Unsupported top-level profile key")
        arguments.extend(["--config", key + "=" + toml_value(value)])
    return {"format": "valhall-panel-profile/1", "profile": "valhalla",
            "source_sha256": hashlib.sha256(source).hexdigest(), "arguments": arguments}


def main():
    MACOS.mkdir(parents=True, exist_ok=True)
    RESOURCES.mkdir(parents=True, exist_ok=True)
    cache = BUILD / "module-cache"
    cache.mkdir(exist_ok=True)
    compiler = ["xcrun", "swiftc", "-module-cache-path", cache, "-O", "-framework", "AppKit"]
    run(*compiler, ROOT / "CodeExp2.swift", "-o", MACOS / "CodeExp2")
    run(*compiler, ROOT / "Icon.swift", "-o", BUILD / "make-icon")
    run(BUILD / "make-icon", ROOT / "valhall-icon.png", BUILD / "CodeExp2.iconset")
    run("/usr/bin/iconutil", "-c", "icns", BUILD / "CodeExp2.iconset", "-o", RESOURCES / "Valhall.icns")
    command = RESOURCES / "Start CodeExp2.command"
    shutil.copyfile(ROOT / "Start CodeExp2.command", command)
    os.chmod(command, 0o755)
    shutil.copyfile(ROOT / "valhalla.config.toml", RESOURCES / "valhalla.config.toml")
    (RESOURCES / "valhall-panel-profile.json").write_text(
        json.dumps(panel_profile((ROOT / "valhalla.config.toml").read_bytes()), indent=2) + "\n")
    plist = {
        "CFBundleName": "Valhall",
        "CFBundleDisplayName": "Valhall",
        "CFBundleIdentifier": "local.codeexp2.coordinator-launcher",
        "CFBundleExecutable": "CodeExp2",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "2",
        "CFBundleIconFile": "Valhall.icns",
        "LSMinimumSystemVersion": "13.0",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    }
    with (APP / "Contents/Info.plist").open("wb") as handle:
        plistlib.dump(plist, handle)
    run("/usr/bin/codesign", "--force", "--sign", "-", APP)
    run("/usr/bin/codesign", "--verify", "--strict", APP)
    # Refresh the package timestamp after updating bundled artwork in place.
    os.utime(APP, None)
    run(MACOS / "CodeExp2", "--self-test")
    run(MACOS / "CodeExp2", "--preflight")
    print(f"Built and signed: {APP}")


if __name__ == "__main__":
    main()
