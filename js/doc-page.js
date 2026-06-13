document.addEventListener("DOMContentLoaded", () => {
  const docId = document.body.dataset.doc;
  if (!docId || typeof DOCS === "undefined" || !DOCS[docId]) return;

  const doc = DOCS[docId];

  document.title = doc.title + " — ActaExpress";

  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) metaDesc.content = doc.meta;

  const setText = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  };

  setText("page-title", doc.title.split("—")[0].trim());
  setText("page-price", doc.price);
  setText("page-intro-title", doc.introTitle);
  setText("page-intro", doc.intro);

  const includes = document.getElementById("page-includes");
  if (includes) {
    includes.innerHTML = doc.includes.map((item) => `<li>${item}</li>`).join("");
  }

  const cta = document.getElementById("cta-generate");
  if (cta) {
    const tallyUrl =
      typeof TALLY_URLS !== "undefined" && TALLY_URLS[docId]
        ? TALLY_URLS[docId]
        : "";
    cta.href = tallyUrl || doc.stripePlaceholder || "#";
    cta.textContent = `Générer mon document — ${doc.price}`;
    if (!tallyUrl) cta.title = "Configurer l'URL Tally dans js/tally-urls.js";
    const ctaMobile = document.getElementById("cta-generate-mobile");
    if (ctaMobile) {
      ctaMobile.href = cta.href;
      ctaMobile.textContent = `Générer — ${doc.price}`;
    }
  }
});
