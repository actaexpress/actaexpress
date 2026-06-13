# -*- coding: utf-8 -*-
"""Crée un dossier netlify-deploy/ sans geo/ (~280k fichiers) pour drag-and-drop Netlify."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "netlify-deploy"

INCLUDE = [
    "index.html",
    "contact.html",
    "tarifs.html",
    "robots.txt",
    "_headers",
    "netlify.toml",
    "pages",
    "css",
    "js",
    "assets",
    "legal",
]

SKIP_NETLIFY_TOML_BUILD = True


def write_simple_sitemap() -> None:
    base = "https://actaexpress.fr"
    pages = [
        "/",
        "/tarifs.html",
        "/contact.html",
        "/pages/resiliation-mobile.html",
        "/pages/resiliation-box.html",
        "/pages/resiliation-energie.html",
        "/pages/resiliation-assurance.html",
        "/pages/mise-en-demeure.html",
        "/pages/reclamation-assurance.html",
        "/pages/reclamation-banque.html",
        "/pages/contestation-amende.html",
        "/legal/mentions-legales.html",
        "/legal/cgv.html",
        "/legal/confidentialite.html",
        "/legal/cookies.html",
    ]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        loc = base if p == "/" else base + p
        lines += ["  <url>", f"    <loc>{loc}</loc>", "  </url>"]
    lines.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_netlify_toml() -> None:
    (OUT / "netlify.toml").write_text(
        '[build]\n  publish = "."\n  # Pas de generate-seo-geo ici — deploy léger\n',
        encoding="utf-8",
    )


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for name in INCLUDE:
        src = ROOT / name
        if not src.exists():
            print(f"SKIP (absent): {name}")
            continue
        dst = OUT / name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"OK {name}")

    write_simple_sitemap()
    write_netlify_toml()

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://actaexpress.fr/sitemap.xml\n",
        encoding="utf-8",
    )

    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"\nPret : {OUT}")
    print(f"Fichiers : {n}")
    print("Glissez le CONTENU de netlify-deploy/ sur Netlify (Deploys).")


if __name__ == "__main__":
    main()
