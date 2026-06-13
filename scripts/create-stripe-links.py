# -*- coding: utf-8 -*-
"""Create Stripe Payment Links (live or test) and update project files.

Usage:
  set STRIPE_SECRET_KEY=sk_live_...
  python scripts/create-stripe-links.py

Reads optional .env at project root.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
from pathlib import Path
from urllib import request as urllib_request

ROOT = Path(__file__).resolve().parent.parent
DOCS = [
    {"id": "resiliation-mobile", "name": "ActaExpress - Resiliation mobile", "amount": 1700, "tally": "KYR0yA"},
    {"id": "resiliation-box", "name": "ActaExpress - Resiliation box", "amount": 1700, "tally": "RGrLad"},
    {"id": "resiliation-energie", "name": "ActaExpress - Resiliation energie", "amount": 1700, "tally": "obxO1e"},
    {"id": "resiliation-assurance", "name": "ActaExpress - Resiliation assurance", "amount": 1700, "tally": "Gx704p"},
    {"id": "mise-en-demeure", "name": "ActaExpress - Mise en demeure", "amount": 2400, "tally": "VLx8AJ"},
    {"id": "reclamation-assurance", "name": "ActaExpress - Reclamation assurance", "amount": 2200, "tally": "Eka0EX"},
    {"id": "reclamation-banque", "name": "ActaExpress - Reclamation banque", "amount": 2200, "tally": "jaExYx"},
    {"id": "contestation-amende", "name": "ActaExpress - Contestation amende", "amount": 2900, "tally": "44Gjyk"},
]

TALLY_LABELS = {
    "resiliation-mobile": "Resiliation mobile",
    "resiliation-box": "Resiliation box",
    "resiliation-energie": "Resiliation energie",
    "resiliation-assurance": "Resiliation assurance",
    "mise-en-demeure": "Mise en demeure",
    "reclamation-assurance": "Reclamation assurance",
    "reclamation-banque": "Reclamation banque",
    "contestation-amende": "Contestation amende",
}


def load_secret_key() -> str:
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if key:
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("STRIPE_SECRET_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(
        "Missing STRIPE_SECRET_KEY. Add it to .env or set the environment variable.\n"
        "For production: use sk_live_... from Stripe dashboard."
    )


def stripe_request(secret: str, method: str, path: str, data: dict | None = None) -> dict:
    url = f"https://api.stripe.com/v1{path}"
    body = None
    headers = {"Authorization": f"Bearer {secret}"}
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib_request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib_request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Stripe API error ({e.code}): {err}") from e


def create_payment_link(secret: str, doc: dict) -> str:
    product = stripe_request(
        secret,
        "POST",
        "/products",
        {"name": doc["name"], "description": "Document PDF personnalise ActaExpress"},
    )
    price = stripe_request(
        secret,
        "POST",
        "/prices",
        {
            "product": product["id"],
            "unit_amount": str(doc["amount"]),
            "currency": "eur",
        },
    )
    link = stripe_request(
        secret,
        "POST",
        "/payment_links",
        {
            "line_items[0][quantity]": "1",
            "line_items[0][price]": price["id"],
        },
    )
    return link["url"]


def write_js(links: dict[str, str], mode: str) -> None:
    lines = [
        "/**",
        f" * Stripe Payment Links (mode {mode.upper()}).",
        " * Genere par scripts/create-stripe-links.py",
        " */",
        "const STRIPE_URLS = {",
    ]
    for doc in DOCS:
        lines.append(f'  "{doc["id"]}": "{links[doc["id"]]}",')
    lines.append("};")
    (ROOT / "js" / "stripe-urls.js").write_text("\n".join(lines) + "\n",encoding="utf-8", newline="\n")


def write_tally_redirects(links: dict[str, str], mode: str) -> None:
    out = [
        f"STRIPE ACTAEXPRESS — mode {mode.upper()}",
        "",
        "Tally Settings -> After submission -> Redirect to URL",
        "",
    ]
    for i, doc in enumerate(DOCS, 1):
        out.append(f"Form {i} {TALLY_LABELS[doc['id']]} ({doc['tally']})")
        out.append(f"  -> {links[doc['id']]}")
        out.append("")
    (ROOT / "content" / "stripe" / "STRIPE-TALLY-REDIRECTS.txt").write_text(
        "\n".join(out) + "\n",encoding="utf-8", newline="\n"
    )


def main() -> None:
    secret = load_secret_key()
    mode = "live" if secret.startswith("sk_live_") else "test"
    links: dict[str, str] = {}
    for doc in DOCS:
        print(f"Creating link: {doc['id']}...")
        links[doc["id"]] = create_payment_link(secret, doc)
        print(f"  {links[doc['id']]}")
    write_js(links, mode)
    write_tally_redirects(links, mode)
    print(f"Done ({mode}).")


if __name__ == "__main__":
    main()
