# -*- coding: utf-8 -*-
"""Télécharge et compacte la liste officielle des communes françaises (geo.api.gouv.fr)."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEO = ROOT / "content" / "seo"
COMMUNES_OUT = SEO / "communes-fr.json"
DEPTS_OUT = SEO / "departements-fr.json"
REGIONS_OUT = SEO / "regions-fr.json"

API = "https://geo.api.gouv.fr"


def fetch(path: str) -> list | dict:
    url = f"{API}{path}"
    with urllib.request.urlopen(url, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    SEO.mkdir(parents=True, exist_ok=True)

    regions_raw = fetch("/regions?fields=nom,code&format=json")
    regions = {r["code"]: r["nom"] for r in regions_raw}
    REGIONS_OUT.write_text(json.dumps(regions, ensure_ascii=False, indent=0), encoding="utf-8")

    depts_raw = fetch("/departements?fields=nom,code,codeRegion&format=json")
    depts = {
        d["code"]: {"nom": d["nom"], "region": regions.get(d["codeRegion"], "")}
        for d in depts_raw
    }
    DEPTS_OUT.write_text(json.dumps(depts, ensure_ascii=False, indent=0), encoding="utf-8")

    communes_raw = fetch("/communes?fields=nom,code,codeDepartement,population&format=json")
    communes = [
        {
            "n": c["nom"],
            "c": c["code"],
            "d": c["codeDepartement"],
            "p": c.get("population") or 0,
        }
        for c in communes_raw
    ]
    communes.sort(key=lambda x: (x["d"], x["n"].lower()))
    COMMUNES_OUT.write_text(json.dumps(communes, ensure_ascii=False), encoding="utf-8")

    print(f"Régions    : {len(regions)}")
    print(f"Départements : {len(depts)}")
    print(f"Communes   : {len(communes)}")
    print(f"Écrit      : {COMMUNES_OUT.name}, {DEPTS_OUT.name}, {REGIONS_OUT.name}")


if __name__ == "__main__":
    main()
