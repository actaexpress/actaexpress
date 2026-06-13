# -*- coding: utf-8 -*-
"""Regenerate all service pages with correct UTF-8 encoding."""

from pathlib import Path

PAGES_DIR = Path(__file__).resolve().parent.parent / "pages"

DOCS = {
    "resiliation-mobile": {
        "price": "17 €",
        "checklist": [
            "Envoyez en recommande avec accuse de reception (AR)",
            "Adresse : service resiliation de votre operateur (sur votre facture)",
            "Joignez une copie de votre piece d'identite",
            "Conservez l'AR et une copie de la lettre",
        ],
    },
    "resiliation-box": {
        "price": "17 €",
        "checklist": [
            "Envoyez en recommande avec AR",
            "Precisez la date de retour de la box si demandee",
            "Conservez la preuve d'envoi et de reception",
        ],
    },
    "resiliation-energie": {
        "price": "17 €",
        "checklist": [
            "Envoyez en recommande avec AR au fournisseur",
            "Indiquez le numero PDL (electricite) ou PCE (gaz)",
            "Planifiez la releve de compteur si necessaire",
        ],
    },
    "resiliation-assurance": {
        "price": "17 €",
        "checklist": [
            "Envoyez en recommande avec AR",
            "Respectez les delais de preavis contractuels",
            "Conservez une copie et l'accuse de reception",
        ],
    },
    "mise-en-demeure": {
        "price": "24 €",
        "checklist": [
            "Envoyez en recommande avec AR",
            "Joignez les pieces justificatives (factures, contrats)",
            "Conservez une copie datee de la mise en demeure",
        ],
    },
    "reclamation-assurance": {
        "price": "22 €",
        "checklist": [
            "Envoyez en recommande ou par email avec accuse",
            "Joignez references sinistre et echanges anterieurs",
            "Conservez une copie de votre reclamation",
        ],
    },
    "reclamation-banque": {
        "price": "22 €",
        "checklist": [
            "Envoyez en recommande au service reclamation",
            "Joignez releves et justificatifs",
            "Conservez une copie datee",
        ],
    },
    "contestation-amende": {
        "price": "29 €",
        "checklist": [
            "Envoyez dans les delais indiques sur l'avis",
            "Joignez photos, tickets ou temoignages",
            "Conservez l'accuse de reception",
        ],
    },
}

# French text with proper accents in template
TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ActaExpress</title>
  <meta name="description" content="">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body data-doc="{doc_id}">
  <header class="site-header">
    <div class="container header-inner">
      <a href="../index.html" class="logo">Acta<span>Express</span></a>
      <nav class="nav-desktop">
        <a href="../index.html#documents">Documents</a>
        <a href="../tarifs.html">Tarifs</a>
        <a href="../contact.html">Contact</a>
      </nav>
      <button class="menu-toggle" aria-label="Menu">&#9776;</button>
    </div>
    <nav class="nav-mobile container">
      <a href="../index.html#documents">Documents</a>
      <a href="../tarifs.html">Tarifs</a>
      <a href="../contact.html">Contact</a>
    </nav>
  </header>

  <div class="trust-banner">
    <div class="container trust-banner-inner">
      <span class="trust-banner-item"><span class="trust-icon">&#10003;</span> <strong>Remboursement</strong> 7 jours</span>
      <span class="trust-banner-item"><span class="trust-icon">&#10003;</span> <strong>Paiement</strong> Stripe</span>
      <span class="trust-banner-item"><span class="trust-icon">&#10003;</span> <strong>PDF</strong> instantan&eacute;</span>
      <span class="trust-banner-item"><span class="trust-icon">&#10003;</span> <strong>Support</strong> sous 48 h</span>
    </div>
  </div>

  <div class="page-hero">
    <div class="container">
      <h1 id="page-title">Document</h1>
      <div class="meta">
        <span class="price-tag" id="page-price">{price}</span>
        <span>PDF instantan&eacute; par email</span>
      </div>
    </div>
  </div>

  <div class="page-content">
    <div class="container page-layout">
      <div class="content-block">
        <h2 id="page-intro-title">Description</h2>
        <p id="page-intro"></p>

        <div class="pdf-preview-block">
          <h2>Aper&ccedil;u du document</h2>
          <p style="font-size:0.875rem;color:var(--muted);margin-bottom:0.5rem;">Exemple de mise en page &mdash; vos informations personnelles appara&icirc;tront dans le PDF final.</p>
          <div class="pdf-preview-wrap">
            <img src="../assets/pdf-preview.svg" alt="Exemple de document ActaExpress" width="220" height="286">
          </div>
          <p class="pdf-preview-caption">Document personnalis&eacute; &bull; Format lettre professionnelle</p>
        </div>

        <h2>Ce que contient votre document</h2>
        <ul id="page-includes"></ul>

        <h2>Pourquoi ActaExpress plut&ocirc;t qu'un mod&egrave;le gratuit ?</h2>
        <div class="why-pay-grid" style="margin:0;max-width:100%;">
          <div class="why-col free">
            <h3>Gratuit (Google / ChatGPT)</h3>
            <ul>
              <li>Texte g&eacute;n&eacute;rique</li>
              <li>Format &agrave; refaire</li>
              <li>Doute sur les mentions</li>
            </ul>
          </div>
          <div class="why-col pro">
            <h3>ActaExpress &mdash; {price}</h3>
            <ul>
              <li>Vos donn&eacute;es int&eacute;gr&eacute;es</li>
              <li>PDF pr&ecirc;t &agrave; envoyer</li>
              <li>Checklist incluse</li>
            </ul>
          </div>
        </div>

        <h2>Comment envoyer votre lettre</h2>
        <ul id="page-checklist">
{checklist_items}
        </ul>
      </div>
      <aside class="sidebar-card">
        <div class="sidebar-trust">
          <span class="trust-pill">&#128274; Paiement s&eacute;curis&eacute; Stripe</span>
          <span class="trust-pill">&#8635; Rembours&eacute; sous 7 jours</span>
          <span class="trust-pill">&#9889; PDF en quelques minutes</span>
        </div>
        <h3>Commander maintenant</h3>
        <ul class="sidebar-features">
          <li>Questionnaire guid&eacute; (2 &agrave; 4 min)</li>
          <li>Document 100 % personnalis&eacute;</li>
          <li>PDF professionnel par email</li>
          <li>Checklist d'envoi incluse</li>
        </ul>
        <a href="#" id="cta-generate" class="btn btn-primary btn-lg cta-full">G&eacute;n&eacute;rer mon document</a>
        <div class="guarantee">Pas satisfait ? Remboursement int&eacute;gral sous 7 jours. Contact : acta.express0@gmail.com</div>
      </aside>
    </div>
  </div>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <h4>ActaExpress</h4>
          <p style="font-size:0.85rem;">Service fran&ccedil;ais de r&eacute;daction de documents administratifs.</p>
        </div>
        <div>
          <h4>Contact</h4>
          <a href="../contact.html">Nous contacter</a>
          <a href="mailto:acta.express0@gmail.com">acta.express0@gmail.com</a>
        </div>
        <div>
          <h4>L&eacute;gal</h4>
          <a href="../legal/mentions-legales.html">Mentions l&eacute;gales</a>
          <a href="../legal/cgv.html">CGV</a>
          <a href="../legal/confidentialite.html">Confidentialit&eacute;</a>
          <a href="../legal/cookies.html">Cookies</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 ActaExpress &mdash; Service de r&eacute;daction, ne remplace pas un avocat.</p>
      </div>
    </div>
  </footer>
  <script src="../js/doc-data.js"></script>
  <script src="../js/tally-urls.js"></script>
  <script src="../js/doc-page.js"></script>
  <script src="../js/main.js"></script>
</body>
</html>
"""

CHECKLIST_FR = {
    "resiliation-mobile": [
        "Envoyez en recommand\u00e9 avec accus\u00e9 de r\u00e9ception (AR)",
        "Adresse : service r\u00e9siliation de votre op\u00e9rateur (indiqu\u00e9e sur votre facture)",
        "Joignez une copie de votre pi\u00e8ce d'identit\u00e9",
        "Conservez l'AR et une copie de la lettre",
    ],
    "resiliation-box": [
        "Envoyez en recommand\u00e9 avec AR \u00e0 l'adresse indiqu\u00e9e sur votre facture",
        "Pr\u00e9cisez la date de retour de la box ou du modem si applicable",
        "Conservez la preuve d'envoi et l'accus\u00e9 de r\u00e9ception",
    ],
    "resiliation-energie": [
        "Envoyez en recommand\u00e9 avec AR \u00e0 votre fournisseur",
        "V\u00e9rifiez le num\u00e9ro PDL (\u00e9lectricit\u00e9) ou PCE (gaz) sur la facture",
        "Planifiez la rel\u00e8ve de compteur si n\u00e9cessaire",
    ],
    "resiliation-assurance": [
        "Envoyez en recommand\u00e9 avec AR \u00e0 l'adresse de l'assureur",
        "Respectez les d\u00e9lais de pr\u00e9avis indiqu\u00e9s au contrat",
        "Conservez une copie et l'accus\u00e9 de r\u00e9ception",
    ],
    "mise-en-demeure": [
        "Envoyez en recommand\u00e9 avec AR",
        "Joignez les pi\u00e8ces justificatives (factures, contrats, emails)",
        "Conservez une copie dat\u00e9e de la mise en demeure",
    ],
    "reclamation-assurance": [
        "Envoyez en recommand\u00e9 ou par email avec accus\u00e9 de r\u00e9ception",
        "Joignez les r\u00e9f\u00e9rences sinistre et vos \u00e9changes ant\u00e9rieurs",
        "Conservez une copie de votre r\u00e9clamation",
    ],
    "reclamation-banque": [
        "Adressez au service r\u00e9clamation de votre banque (AR recommand\u00e9)",
        "Joignez vos relev\u00e9s et justificatifs",
        "Conservez une copie dat\u00e9e",
    ],
    "contestation-amende": [
        "Respectez le d\u00e9lai indiqu\u00e9 sur l'avis de contravention",
        "Joignez photos, tickets de parking ou t\u00e9moignages",
        "Conservez l'accus\u00e9 de r\u00e9ception",
    ],
}

PRICES = {
    "resiliation-mobile": "17 \u20ac",
    "resiliation-box": "17 \u20ac",
    "resiliation-energie": "17 \u20ac",
    "resiliation-assurance": "17 \u20ac",
    "mise-en-demeure": "24 \u20ac",
    "reclamation-assurance": "22 \u20ac",
    "reclamation-banque": "22 \u20ac",
    "contestation-amende": "29 \u20ac",
}


def main():
    for doc_id, items in CHECKLIST_FR.items():
        checklist_html = "\n".join(f"          <li>{item}</li>" for item in items)
        html = TEMPLATE.format(
            doc_id=doc_id,
            price=PRICES[doc_id],
            checklist_items=checklist_html,
        )
        out = PAGES_DIR / f"{doc_id}.html"
        out.write_text(html, encoding="utf-8", newline="\n")
        print(f"OK {out.name}")


if __name__ == "__main__":
    main()
