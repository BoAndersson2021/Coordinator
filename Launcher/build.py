#!/usr/bin/env python3
"""Build and ad-hoc sign the Valhall launcher for CodeExp2, without launching it."""
import os
from pathlib import Path
import plistlib
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
APP = BUILD / "CodeExp2.app"
MACOS = APP / "Contents/MacOS"
RESOURCES = APP / "Contents/Resources"


def run(*args):
    subprocess.run([str(a) for a in args], check=True, cwd=ROOT)


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
