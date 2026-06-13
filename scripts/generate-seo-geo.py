# -*- coding: utf-8 -*-
"""
Génère le maillage SEO géographique ActaExpress — couverture nationale complète.
34 969 communes × 8 services + 101 départements + régions + France.
"""

from __future__ import annotations

import html
import json
import os
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from departements_fr import dept_slug, region_slug, slugify

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "geo"
SEO = ROOT / "content" / "seo"
BASE_URL = "https://actaexpress.fr"
TODAY = date.today().isoformat()
SITEMAP_LIMIT = 45000
WORKERS = 2 if os.environ.get("NETLIFY") else min(8, os.cpu_count() or 4)

SERVICES = {
    "resiliation-mobile": {
        "short": "Résiliation mobile",
        "long": "Lettre de résiliation forfait mobile",
        "page": "resiliation-mobile.html",
        "price": "17 €",
        "detail": "Free, Orange, SFR, Bouygues",
        "verbs": ["résilier votre forfait mobile", "résilier votre abonnement téléphone", "mettre fin à votre contrat mobile"],
        "faq_q": "Comment résilier un forfait mobile à {place} ?",
        "faq_a": "Remplissez le questionnaire ActaExpress en ligne. PDF personnalisé par email, prêt à envoyer en recommandé — depuis {place}, en France métropolitaine et outre-mer.",
    },
    "resiliation-box": {
        "short": "Résiliation box internet",
        "long": "Lettre de résiliation box / fibre",
        "page": "resiliation-box.html",
        "price": "17 €",
        "detail": "Freebox, Livebox, SFR Box, Bouygues",
        "verbs": ["résilier votre box internet", "résilier votre abonnement fibre", "mettre fin à votre connexion internet"],
        "faq_q": "Comment résilier une box internet depuis {place} ?",
        "faq_a": "ActaExpress génère votre lettre avec adresse de raccordement et date d'effet. Service 100 % en ligne — {place}, ville ou campagne.",
    },
    "resiliation-energie": {
        "short": "Résiliation énergie",
        "long": "Lettre de résiliation électricité / gaz",
        "page": "resiliation-energie.html",
        "price": "17 €",
        "detail": "EDF, Engie, TotalEnergies, Mint",
        "verbs": ["résilier votre contrat électricité", "résilier votre contrat gaz", "changer de fournisseur d'énergie"],
        "faq_q": "Comment résilier son contrat énergie à {place} ?",
        "faq_a": "Indiquez votre numéro PDL/PCE. PDF conforme aux usages, utilisable depuis {place} et partout en France.",
    },
    "resiliation-assurance": {
        "short": "Résiliation assurance",
        "long": "Lettre de résiliation assurance / mutuelle",
        "page": "resiliation-assurance.html",
        "price": "17 €",
        "detail": "auto, habitation, santé, mutuelle",
        "verbs": ["résilier votre assurance", "résilier votre mutuelle", "mettre fin à votre contrat d'assurance"],
        "faq_q": "Comment résilier une assurance depuis {place} ?",
        "faq_a": "Questionnaire guidé, PDF avec numéro de contrat et motif. Envoyez en recommandé depuis {place} ou votre bureau de poste.",
    },
    "mise-en-demeure": {
        "short": "Mise en demeure",
        "long": "Mise en demeure personnalisée",
        "page": "mise-en-demeure.html",
        "price": "24 €",
        "detail": "impayé, litige, délai de régularisation",
        "verbs": ["rédiger une mise en demeure", "envoyer une mise en demeure", "formaliser une réclamation avant contentieux"],
        "faq_q": "Comment faire une mise en demeure à {place} ?",
        "faq_a": "ActaExpress structure votre courrier avec les faits, le montant et un délai. PDF par email — imprimez et envoyez en AR depuis {place}.",
    },
    "reclamation-assurance": {
        "short": "Réclamation assurance",
        "long": "Lettre de réclamation assurance",
        "page": "reclamation-assurance.html",
        "price": "22 €",
        "detail": "refus, retard, indemnisation insuffisante",
        "verbs": ["contester un refus d'assurance", "réclamer une indemnisation", "formaliser une réclamation sinistre"],
        "faq_q": "Comment réclamer auprès de son assurance à {place} ?",
        "faq_a": "Document avec références sinistre et historique. Service en ligne depuis {place} et tout le territoire.",
    },
    "reclamation-banque": {
        "short": "Réclamation banque",
        "long": "Lettre de réclamation bancaire",
        "page": "reclamation-banque.html",
        "price": "22 €",
        "detail": "frais, prélèvement, litige compte",
        "verbs": ["contester des frais bancaires", "réclamer auprès de votre banque", "contester un prélèvement"],
        "faq_q": "Comment réclamer auprès de sa banque depuis {place} ?",
        "faq_a": "Réclamation claire avec montant contesté et chronologie. PDF instantané depuis {place}, sans déplacement.",
    },
    "contestation-amende": {
        "short": "Contestation amende",
        "long": "Lettre de contestation d'amende",
        "page": "contestation-amende.html",
        "price": "29 €",
        "detail": "stationnement, radar, feu rouge",
        "verbs": ["contester une amende", "contester un PV de stationnement", "contester une contravention radar"],
        "faq_q": "Comment contester une amende à {place} ?",
        "faq_a": "Références de l'avis et arguments structurés. PDF à envoyer dans les délais — depuis {place} ou ailleurs.",
    },
}


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def commune_slug(name: str, insee: str) -> str:
    return f"ville-{slugify(name)}-{insee}"


def load_data() -> tuple[list[dict], list[tuple], dict]:
    communes = json.loads((SEO / "communes-fr.json").read_text(encoding="utf-8"))
    depts_json = json.loads((SEO / "departements-fr.json").read_text(encoding="utf-8"))

    pref_by_dept: dict[str, dict] = {}
    for c in communes:
        d = c["d"]
        if d not in pref_by_dept or c["p"] > pref_by_dept[d]["p"]:
            pref_by_dept[d] = c

    depts: list[tuple] = []
    for code in sorted(depts_json.keys(), key=lambda x: (len(x), x)):
        meta = depts_json[code]
        pref = pref_by_dept.get(code, {})
        depts.append((code, meta["nom"], meta["region"], pref.get("n", meta["nom"])))

    dept_map = {code: {"nom": n, "region": r} for code, n, r, _ in depts}
    return communes, depts, dept_map


def header(depth: int) -> str:
    p = "../" * depth
    return f"""  <header class="site-header">
    <div class="container header-inner">
      <a href="{p}index.html" class="logo">Acta<span>Express</span></a>
      <nav class="nav-desktop">
        <a href="{p}index.html#documents">Documents</a>
        <a href="{p}geo/index.html">France entière</a>
        <a href="{p}tarifs.html">Tarifs</a>
        <a href="{p}contact.html">Contact</a>
      </nav>
      <button class="menu-toggle" aria-label="Menu">&#9776;</button>
    </div>
    <nav class="nav-mobile container">
      <a href="{p}index.html#documents">Documents</a>
      <a href="{p}geo/index.html">France entière</a>
      <a href="{p}tarifs.html">Tarifs</a>
      <a href="{p}contact.html">Contact</a>
      <a href="{p}index.html#documents" class="btn btn-primary">Choisir un document</a>
    </nav>
  </header>"""


def footer(depth: int) -> str:
    p = "../" * depth
    return f"""  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <h4>ActaExpress</h4>
          <p style="font-size:0.85rem;">34 969 communes — France métropolitaine et outre-mer.</p>
        </div>
        <div>
          <h4>Couverture</h4>
          <a href="{p}geo/index.html">Toutes les communes</a>
        </div>
        <div>
          <h4>L&eacute;gal</h4>
          <a href="{p}legal/mentions-legales.html">Mentions l&eacute;gales</a>
          <a href="{p}legal/cgv.html">CGV</a>
          <a href="{p}legal/confidentialite.html">Confidentialit&eacute;</a>
        </div>
        <div>
          <h4>Contact</h4>
          <a href="mailto:acta.express0@gmail.com">acta.express0@gmail.com</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 ActaExpress &mdash; Service de r&eacute;daction, ne remplace pas un avocat.</p>
      </div>
    </div>
  </footer>
  <script src="{p}js/main.js"></script>"""


def faq_json_ld(service: dict, place: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": service["faq_q"].format(place=place),
                "acceptedAnswer": {"@type": "Answer", "text": service["faq_a"].format(place=place)},
            },
            {
                "@type": "Question",
                "name": f"ActaExpress est-il disponible à {place} ?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Oui. Service 100 % en ligne pour {place} et les 34 969 communes du territoire national — ville, bourg et village.",
                },
            },
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def geo_page_shell(
    *,
    depth: int,
    title: str,
    description: str,
    canonical: str,
    breadcrumb: str,
    h1: str,
    body: str,
    service: dict,
    place: str,
    cta_href: str,
) -> str:
    p = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{esc(canonical)}">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}css/style.css">
  <script type="application/ld+json">{faq_json_ld(service, place)}</script>
</head>
<body>
{header(depth)}
  <div class="geo-breadcrumb container">{breadcrumb}</div>
  <article class="legal-page geo-page">
    <h1>{esc(h1)}</h1>
    <p class="legal-updated">Territoire national &mdash; {TODAY}</p>
{body}
    <div class="geo-cta-block">
      <p><strong>{esc(service['long'])}</strong> &mdash; {esc(service['price'])} &mdash; PDF instantan&eacute;</p>
      <a href="{esc(cta_href)}" class="btn btn-primary btn-lg">G&eacute;n&eacute;rer mon document</a>
    </div>
  </article>
{footer(depth)}
</body>
</html>
"""


def dept_body(service: dict, code: str, name: str, region: str, prefecture: str, idx: int, n_communes: int) -> str:
    verb = service["verbs"][idx % len(service["verbs"])]
    slug = dept_slug(code, name)
    return f"""
    <p>D&eacute;partement <strong>{esc(name)} ({esc(code)})</strong>, {esc(region)}. ActaExpress couvre les <strong>{n_communes} communes</strong> du d&eacute;partement — {esc(prefecture)} et toute la campagne.</p>
    <h2>{esc(service['short'])} dans le {esc(name)}</h2>
    <p>{esc(verb.capitalize())} en ligne : questionnaire, Stripe, PDF par email. <a href="communes/{slug}.html">Voir les {n_communes} communes</a>.</p>
    <h2>Campagne et villages</h2>
    <p>Hameaux isol&eacute;s, montagne, littoral : m&ecirc;me service qu'en grande ville. Id&eacute;al quand le bureau de poste est &eacute;loign&eacute;.</p>
    <p class="geo-keywords">{esc(service['short'].lower())} {esc(name.lower())}, {esc(verb)} {esc(name.lower())}, {esc(prefecture.lower())}.</p>
"""


def ville_body(service: dict, ville: str, dept_code: str, dept_name: str, region: str, idx: int) -> str:
    verb = service["verbs"][idx % len(service["verbs"])]
    return f"""
    <p>Commune de <strong>{esc(ville)}</strong> ({esc(dept_name)}, {esc(dept_code)}), {esc(region)}. ActaExpress permet de {esc(verb)} en ligne — village, bourg ou centre-ville.</p>
    <h2>{esc(service['short'])} &agrave; {esc(ville)}</h2>
    <p>PDF personnalis&eacute; ({esc(service['detail'])}), {esc(service['price'])} TTC, re&ccedil;u par email en quelques minutes.</p>
    <h2>Zone rurale</h2>
    <p>Pas d'agence locale n&eacute;cessaire. Depuis {esc(ville)} ou une commune voisine, g&eacute;n&eacute;rez votre document sur telephone ou ordinateur.</p>
    <p class="geo-keywords">{esc(service['short'].lower())} {esc(ville.lower())}, {esc(verb)} {esc(ville.lower())}, {esc(dept_name.lower())} {esc(dept_code)}.</p>
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _build_ville_html(payload: dict) -> tuple[str, str, str]:
    svc = payload["svc"]
    svc_id = payload["svc_id"]
    c = payload["commune"]
    dept = payload["dept"]
    idx = payload["idx"]

    ville = c["n"]
    insee = c["c"]
    dept_code = c["d"]
    dept_name = dept["nom"]
    region = dept["region"]

    slug = commune_slug(ville, insee)
    filename = f"{slug}.html"
    canonical = f"{BASE_URL}/geo/{svc_id}/{filename}"
    rel_path = GEO / svc_id / filename

    breadcrumb = (
        f'<a href="../../index.html">Accueil</a> &rsaquo; '
        f'<a href="../index.html">France</a> &rsaquo; '
        f'<a href="index.html">{esc(svc["short"])}</a> &rsaquo; '
        f'{esc(ville)}'
    )
    title = f"{svc['short']} {ville} ({dept_code}) — PDF en ligne | ActaExpress"
    desc = f"{svc['long']} à {ville} ({dept_name}, {dept_code}). Service en ligne — campagne incluse. PDF {svc['price']}."

    html_out = geo_page_shell(
        depth=2,
        title=title,
        description=desc,
        canonical=canonical,
        breadcrumb=breadcrumb,
        h1=f"{svc['long']} — {ville}",
        body=ville_body(svc, ville, dept_code, dept_name, region, idx),
        service=svc,
        place=f"{ville} ({dept_code})",
        cta_href=f"../../pages/{svc['page']}",
    )
    return canonical, str(rel_path), html_out


def _process_ville_task(payload: dict) -> str:
    payload = {**payload, "svc": SERVICES[payload["svc_id"]]}
    canonical, path_str, html_out = _build_ville_html(payload)
    Path(path_str).write_text(html_out, encoding="utf-8", newline="\n")
    return canonical


def generate_ville_pages(communes: list[dict], dept_map: dict) -> list[str]:
    urls: list[str] = []
    tasks: list[dict] = []
    for svc_id in SERVICES:
        for i, c in enumerate(communes):
            if c["d"] not in dept_map:
                continue
            tasks.append({"svc_id": svc_id, "commune": c, "dept": dept_map[c["d"]], "idx": i})

    print(f"  {len(tasks):,} pages communes ({WORKERS} workers)...")
    batch_size = 8000
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for start in range(0, len(tasks), batch_size):
            chunk = tasks[start : start + batch_size]
            for canonical in pool.map(_process_ville_task, chunk, chunksize=128):
                urls.append(canonical)
            print(f"    {min(start + batch_size, len(tasks)):,} / {len(tasks):,}")

    return urls


def generate_dept_pages(depts: list[tuple], communes_by_dept: dict) -> list[str]:
    urls: list[str] = []
    for svc_id, svc in SERVICES.items():
        for i, (code, name, region, prefecture) in enumerate(depts):
            slug = dept_slug(code, name)
            n = len(communes_by_dept.get(code, []))
            filename = f"{slug}.html"
            canonical = f"{BASE_URL}/geo/{svc_id}/{filename}"
            body = dept_body(svc, code, name, region, prefecture, i, n)
            html_out = geo_page_shell(
                depth=2,
                title=f"{svc['short']} {name} ({code}) — PDF en ligne | ActaExpress",
                description=f"{svc['long']} dans le {name} ({code}). {n} communes. PDF {svc['price']}.",
                canonical=canonical,
                breadcrumb=f'<a href="../../index.html">Accueil</a> &rsaquo; <a href="../index.html">France</a> &rsaquo; <a href="index.html">{esc(svc["short"])}</a> &rsaquo; {esc(name)}',
                h1=f"{svc['long']} — {name} ({code})",
                body=body,
                service=svc,
                place=f"{name} ({code})",
                cta_href=f"../../pages/{svc['page']}",
            )
            write_file(GEO / svc_id / filename, html_out)
            urls.append(canonical)
    return urls


def generate_dept_commune_lists(depts: list[tuple], communes_by_dept: dict) -> list[str]:
    urls: list[str] = []
    for svc_id, svc in SERVICES.items():
        for code, name, _, _ in depts:
            slug = dept_slug(code, name)
            communes = communes_by_dept.get(code, [])
            links = "\n".join(
                f'      <a href="../{commune_slug(c["n"], c["c"])}.html">{esc(c["n"])}</a>'
                for c in communes
            )
            filename = f"{slug}.html"
            path = GEO / svc_id / "communes" / filename
            canonical = f"{BASE_URL}/geo/{svc_id}/communes/{filename}"
            body = f"""
    <p><strong>{len(communes)} communes</strong> du {esc(name)} ({esc(code)}) — {esc(svc['short'].lower())} en ligne.</p>
    <div class="geo-dept-grid">{links}</div>
"""
            html_out = geo_page_shell(
                depth=3,
                title=f"{svc['short']} — Communes du {name} ({code}) | ActaExpress",
                description=f"{svc['long']} dans les {len(communes)} communes du {name}.",
                canonical=canonical,
                breadcrumb=f'<a href="../../../index.html">Accueil</a> &rsaquo; <a href="../../index.html">France</a> &rsaquo; <a href="../index.html">{esc(svc["short"])}</a> &rsaquo; {esc(name)}',
                h1=f"{svc['short']} — Communes du {name}",
                body=body,
                service=svc,
                place=name,
                cta_href=f"../../../pages/{svc['page']}",
            )
            write_file(path, html_out)
            urls.append(canonical)
    return urls


def generate_region_pages(depts: list[tuple]) -> list[str]:
    urls: list[str] = []
    regions = sorted({d[2] for d in depts})
    for svc_id, svc in SERVICES.items():
        for ri, region in enumerate(regions):
            depts_in = [(c, n) for c, n, r, _ in depts if r == region]
            links = "\n".join(
                f'      <a href="../{svc_id}/{dept_slug(c, n)}.html">{esc(n)} ({esc(c)})</a>'
                for c, n in depts_in
            )
            filename = f"{region_slug(region)}-{svc_id}.html"
            canonical = f"{BASE_URL}/geo/regions/{filename}"
            body = f"""
    <p>R&eacute;gion <strong>{esc(region)}</strong> — {esc(svc['short'].lower())} dans tous les d&eacute;partements.</p>
    <div class="geo-dept-grid">{links}</div>
"""
            html_out = geo_page_shell(
                depth=2,
                title=f"{svc['short']} {region} | ActaExpress",
                description=f"{svc['long']} en {region}. Tous départements.",
                canonical=canonical,
                breadcrumb=f'<a href="../../index.html">Accueil</a> &rsaquo; {esc(region)}',
                h1=f"{svc['long']} — {region}",
                body=body,
                service=svc,
                place=region,
                cta_href=f"../../pages/{svc['page']}",
            )
            write_file(GEO / "regions" / filename, html_out)
            urls.append(canonical)
    return urls


def generate_france_pages() -> list[str]:
    urls: list[str] = []
    for svc_id, svc in SERVICES.items():
        filename = f"{svc_id}.html"
        canonical = f"{BASE_URL}/geo/france/{filename}"
        body = f"""
    <p><strong>34 969 communes</strong> — {esc(svc['long'])} partout en France (m&eacute;tropole et outre-mer).</p>
    <ul>
      <li>101 d&eacute;partements</li>
      <li>Villes, bourgs, villages et campagne</li>
      <li>PDF {esc(svc['price'])} — remboursement 7 jours</li>
    </ul>
"""
        html_out = geo_page_shell(
            depth=2,
            title=f"{svc['short']} France — 34 969 communes | ActaExpress",
            description=f"{svc['long']} dans toutes les communes de France.",
            canonical=canonical,
            breadcrumb=f'<a href="../../index.html">Accueil</a> &rsaquo; France enti&egrave;re',
            h1=f"{svc['long']} — France entière",
            body=body,
            service=svc,
            place="France",
            cta_href=f"../../pages/{svc['page']}",
        )
        write_file(GEO / "france" / filename, html_out)
        urls.append(canonical)
    return urls


def generate_service_indexes(depts: list[tuple], n_communes: int) -> list[str]:
    urls: list[str] = []
    for svc_id, svc in SERVICES.items():
        dept_links = "\n".join(
            f'      <a href="{dept_slug(c, n)}.html">{esc(n)} ({esc(c)})</a>'
            for c, n, _, _ in depts
        )
        canonical = f"{BASE_URL}/geo/{svc_id}/"
        body = f"""
    <p>{esc(svc['long'])} — <strong>{n_communes:,} communes</strong> couvertes (territoire national).</p>
    <h2>Par d&eacute;partement (101)</h2>
    <div class="geo-dept-grid">{dept_links}</div>
    <p><a href="../france/{svc_id}.html">France enti&egrave;re</a></p>
"""
        html_out = geo_page_shell(
            depth=2,
            title=f"{svc['short']} — Toutes les communes de France | ActaExpress",
            description=f"{svc['long']} dans 34 969 communes. PDF {svc['price']}.",
            canonical=canonical,
            breadcrumb=f'<a href="../../index.html">Accueil</a> &rsaquo; {esc(svc["short"])}',
            h1=f"{svc['long']} — France",
            body=body,
            service=svc,
            place="France",
            cta_href=f"../../pages/{svc['page']}",
        )
        write_file(GEO / svc_id / "index.html", html_out)
        urls.append(canonical)
    return urls


def generate_geo_index(n_communes: int) -> str:
    svc_cards = "\n".join(
        f"""        <article class="geo-service-card">
          <h3><a href="{sid}/index.html">{esc(s['short'])}</a></h3>
          <p>{n_communes:,} communes — {esc(s['price'])}</p>
          <a href="{sid}/index.html" class="btn btn-primary">Par d&eacute;partement</a>
        </article>"""
        for sid, s in SERVICES.items()
    )
    content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>34 969 communes — Documents admin France | ActaExpress</title>
  <meta name="description" content="Résiliations, mises en demeure, réclamations dans les 34 969 communes de France. Métropole et outre-mer.">
  <link rel="canonical" href="{BASE_URL}/geo/">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
{header(1)}
  <article class="legal-page geo-page geo-hub">
    <h1>ActaExpress — {n_communes:,} communes</h1>
    <p class="legal-updated">101 d&eacute;partements &bull; M&eacute;tropole &amp; outre-mer &bull; Campagne incluse</p>
    <div class="geo-service-grid">{svc_cards}</div>
  </article>
{footer(1)}
</body>
</html>
"""
    write_file(GEO / "index.html", content)
    return f"{BASE_URL}/geo/"


def write_sitemaps(all_urls: list[str]) -> None:
    static = [
        f"{BASE_URL}/",
        f"{BASE_URL}/tarifs.html",
        f"{BASE_URL}/contact.html",
        f"{BASE_URL}/geo/",
        f"{BASE_URL}/legal/mentions-legales.html",
        f"{BASE_URL}/legal/cgv.html",
        f"{BASE_URL}/legal/confidentialite.html",
        f"{BASE_URL}/legal/cookies.html",
    ]
    for sid in SERVICES:
        static.append(f"{BASE_URL}/pages/{SERVICES[sid]['page']}")

    combined = static + all_urls
    unique = sorted(set(combined))
    shards = [unique[i : i + SITEMAP_LIMIT] for i in range(0, len(unique), SITEMAP_LIMIT)]
    shard_names: list[str] = []

    for i, shard in enumerate(shards, 1):
        name = f"sitemap-{i}.xml"
        shard_names.append(name)
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for u in shard:
            lines += [f"  <url>", f"    <loc>{u}</loc>", f"    <lastmod>{TODAY}</lastmod>", "  </url>"]
        lines.append("</urlset>")
        (ROOT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    index_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name in shard_names:
        index_lines += [f"  <sitemap>", f"    <loc>{BASE_URL}/{name}</loc>", f"    <lastmod>{TODAY}</lastmod>", "  </sitemap>"]
    index_lines.append("</sitemapindex>")
    (ROOT / "sitemap.xml").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"  Sitemaps : {len(shard_names)} fichiers, {len(unique):,} URLs")


def generate_robots() -> None:
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://actaexpress.fr/sitemap.xml\n",
        encoding="utf-8",
    )


def main() -> None:
    communes, depts, dept_map = load_data()
    communes_by_dept: dict[str, list] = {}
    for c in communes:
        communes_by_dept.setdefault(c["d"], []).append(c)
    for code in communes_by_dept:
        communes_by_dept[code].sort(key=lambda x: x["n"].lower())

    n_communes = len(communes)
    print(f"Communes : {n_communes:,} | Départements : {len(depts)}")

    if GEO.exists():
        print("Suppression ancien dossier geo/...")
        shutil.rmtree(GEO)

    all_urls: list[str] = []
    print("Départements...")
    all_urls += generate_dept_pages(depts, communes_by_dept)
    print("Listes communes par département...")
    all_urls += generate_dept_commune_lists(depts, communes_by_dept)
    print("Régions...")
    all_urls += generate_region_pages(depts)
    print("France...")
    all_urls += generate_france_pages()
    print("Index services...")
    all_urls += generate_service_indexes(depts, n_communes)
    all_urls.append(generate_geo_index(n_communes))
    print("Communes (×8 services)...")
    all_urls += generate_ville_pages(communes, dept_map)
    print("Sitemaps...")
    write_sitemaps(all_urls)
    generate_robots()

    total = len(all_urls)
    print(f"TOTAL URLs : {total:,}")


if __name__ == "__main__":
    main()
