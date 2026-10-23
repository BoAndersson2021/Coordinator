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
import sys
import tomllib

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
APP = BUILD / "CodeExp2.app"
MACOS = APP / "Contents/MacOS"
RESOURCES = APP / "Contents/Resources"
FALLBACK_ICON = ROOT / "Valhall.icns"
FALLBACK_ICON_SOURCE_SHA256 = "764f6b2be2da2c249f60907a0db3d4d8755ca2134a754bd83ec64574bf9074de"
FALLBACK_ICON_SHA256 = "5b433d1b98a39144e6dfae282068840a82b591919ceaa1c7e670351b269062a7"


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


def bridge_runtime_manifest(interpreter):
    if not interpreter.is_file() or not os.access(interpreter, os.X_OK):
        interpreter = Path(sys.executable)
    if not interpreter.is_file() or not os.access(interpreter, os.X_OK):
        raise RuntimeError("Desktop bridge build interpreter is unavailable")
    loader = """import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('desktop_bridge_runtime', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps(module.runtime_identity(), sort_keys=True))
"""
    result = subprocess.run([str(interpreter), "-c", loader, str(ROOT / "desktop_bridge.py")],
                            text=True, capture_output=True)
    if result.returncode:
        # Packaging/preflight stays available in a clean source snapshot. The
        # bundled sentinel makes the actual Terminal launch fail closed until
        # its pinned bridge interpreter and transport are provisioned.
        return {"format": "codeexp2-desktop-bridge-runtime/1", "state": "unavailable"}
    return json.loads(result.stdout)


def package_icon(iconset, destination):
    """Prefer native packaging, with a pinned valid fallback for broken iconutil hosts."""
    result = subprocess.run(["/usr/bin/iconutil", "-c", "icns", str(iconset), "-o", str(destination)],
                            cwd=ROOT, text=True, capture_output=True)
    if result.returncode == 0:
        return
    source_hash = hashlib.sha256((ROOT / "valhall-icon.png").read_bytes()).hexdigest()
    fallback = FALLBACK_ICON.read_bytes() if FALLBACK_ICON.is_file() else b""
    if (source_hash == FALLBACK_ICON_SOURCE_SHA256
            and hashlib.sha256(fallback).hexdigest() == FALLBACK_ICON_SHA256
            and fallback.startswith(b"icns")):
        shutil.copyfile(FALLBACK_ICON, destination)
        print("iconutil rejected this host's iconset; using the checked-in Valhall.icns for the verified current artwork.")
        return
    raise RuntimeError("iconutil failed and no fallback matches the current valhall-icon.png:\n" + result.stderr)


def main():
    MACOS.mkdir(parents=True, exist_ok=True)
    RESOURCES.mkdir(parents=True, exist_ok=True)
    cache = BUILD / "module-cache"
    cache.mkdir(exist_ok=True)
    compiler = ["xcrun", "swiftc", "-module-cache-path", cache, "-O", "-framework", "AppKit"]
    run(*compiler, ROOT / "CodeExp2.swift", "-o", MACOS / "CodeExp2")
    run(*compiler, ROOT / "Icon.swift", "-o", BUILD / "make-icon")
    # iconutil is strict about its input directory. Regenerate this disposable
    # staging set rather than reusing stale derived PNGs or metadata.
    iconset = BUILD / "CodeExp2.iconset"
    shutil.rmtree(iconset, ignore_errors=True)
    run(BUILD / "make-icon", ROOT / "valhall-icon.png", iconset)
    package_icon(iconset, RESOURCES / "Valhall.icns")
    command = RESOURCES / "Start CodeExp2.command"
    shutil.copyfile(ROOT / "Start CodeExp2.command", command)
    os.chmod(command, 0o755)
    bridge = RESOURCES / "desktop_bridge.py"
    shutil.copyfile(ROOT / "desktop_bridge.py", bridge)
    os.chmod(bridge, 0o755)
    runtime = bridge_runtime_manifest(BUILD / "native-control-venv/bin/python")
    (RESOURCES / "desktop-bridge-runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
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
