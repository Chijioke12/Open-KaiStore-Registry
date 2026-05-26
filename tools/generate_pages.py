#!/usr/bin/env python3
import json
import os
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pages_manifest(app: dict) -> dict:
    # "Mini manifest" for installing packaged apps via mozApps.install():
    # include package_path pointing to the ZIP URL.
    manifest = {
        "name": app.get("name") or app.get("id") or "App",
        "description": app.get("description") or "",
        "developer": {"name": app.get("author") or "Unknown"},
        "icons": {"112": app.get("icon") or ""},
        "package_path": app.get("download_url") or "",
    }
    # Strip empty icon if missing.
    if not manifest["icons"]["112"]:
        manifest.pop("icons", None)
    return manifest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    apps_json_path = root / "apps.json"
    out_dir = Path(os.environ.get("OUT_DIR", str(root / "_pages"))).resolve()

    if not apps_json_path.is_file():
        raise SystemExit(f"Missing {apps_json_path}")

    data = json.loads(apps_json_path.read_text(encoding="utf-8"))
    apps = data.get("apps") if isinstance(data, dict) else None
    if not isinstance(apps, list):
        apps = []

    ensure_dir(out_dir)
    ensure_dir(out_dir / "manifests")

    # Copy apps.json as-is to Pages output.
    (out_dir / "apps.json").write_text(
        json.dumps({"apps": apps}, indent=2) + "\n", encoding="utf-8"
    )

    for app in apps:
        if not isinstance(app, dict):
            continue
        app_id = app.get("id")
        if not app_id:
            continue

        # Generate a Pages-served manifest for packaged apps.
        if app.get("type") == "packaged" and app.get("download_url"):
            manifest = pages_manifest(app)
            (out_dir / "manifests" / f"{app_id}.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

