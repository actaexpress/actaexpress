/**
 * ActaExpress — Tally → Google Sheet (sans Make.com)
 *
 * INSTALLATION (10 min, une seule fois) :
 * 1. Ouvre ton Google Sheet "ActaExpress Commandes"
 * 2. Extensions → Apps Script
 * 3. Supprime le contenu → colle TOUT ce fichier → Enregistrer
 * 4. Déployer → Nouveau déploiement → Type : Application Web
 *    - Exécuter en tant que : Moi
 *    - Accès : Tout le monde (même anonyme)
 * 5. Copie l'URL du Web App (https://script.google.com/macros/s/.../exec)
 * 6. Tally form Mobile → Integrations → Webhooks → colle cette URL → Connect
 *
 * Test : remplis le form Tally → une ligne apparaît dans le Sheet.
 */

var HEADERS = [
  "date_soumission", "email", "type_doc", "paye", "pdf_envoye",
  "civilite", "nom", "prenom", "adresse", "code_postal", "ville",
  "telephone", "operateur", "operateur_autre", "numero_ligne",
  "numero_client", "date_resiliation", "motif", "motif_autre",
  "arret_prelevements", "infos_complementaires", "reponses_json",
  "stripe_payment_id"
];

function doPost(e) {
  try {
    var raw = e.postData ? e.postData.contents : "";
    var payload = raw ? JSON.parse(raw) : {};
    var row = buildRow(payload);
    appendRow(row);
    return jsonResponse({ ok: true, email: row[1] });
  } catch (err) {
    return jsonResponse({ ok: false, error: String(err) });
  }
}

function doGet() {
  return jsonResponse({ ok: true, service: "ActaExpress Tally webhook" });
}

function buildRow(payload) {
  var data = payload.data || payload;
  var fields = data.fields || data.champs || [];
  var map = fieldsToMap(fields);
  var formName = (data.formName || data.nom_formulaire || "").toLowerCase();
  var typeDoc = guessTypeDoc(formName, map);

  return [
    formatNow(),
    pick(map, ["email", "e-mail", "courriel", "mail"]),
    typeDoc,
    "non",
    "non",
    pick(map, ["civilite", "civilité", "civilite"]),
    pick(map, ["nom", "name"]),
    pick(map, ["prenom", "prénom", "firstname"]),
    pick(map, ["adresse", "adresse (numero et rue)", "adresse (numéro et rue)"]),
    pick(map, ["code postal", "code_postal", "cp"]),
    pick(map, ["ville", "city"]),
    pick(map, ["telephone", "téléphone", "phone", "tel"]),
    pick(map, ["operateur", "opérateur", "operator"]),
    pick(map, ["precisez l'operateur", "précisez l'opérateur", "operateur autre"]),
    pick(map, ["numero de ligne", "numéro de ligne", "numero_ligne", "ligne"]),
    pick(map, ["numero client", "numéro client", "reference contrat", "référence contrat"]),
    pick(map, ["date souhaitee", "date souhaitée", "date de resiliation", "date résiliation"]),
    pick(map, ["motif de resiliation", "motif de résiliation", "motif"]),
    pick(map, ["precisez le motif", "précisez le motif"]),
    pick(map, ["arret des prelevements", "arrêt des prélèvements", "prelevements"]),
    pick(map, ["informations complementaires", "informations complémentaires", "infos"]),
    JSON.stringify(payload),
    ""
  ];
}

function fieldsToMap(fields) {
  var map = {};
  if (!fields || !fields.length) return map;

  for (var i = 0; i < fields.length; i++) {
    var f = fields[i];
    var label = normalizeKey(f.label || f.etiquette || f.title || f.key || ("field_" + i));
    var val = extractValue(f);
    if (val !== "") map[label] = val;
  }
  return map;
}

function extractValue(field) {
  if (field.value !== undefined && field.value !== null && field.value !== "") {
    return String(field.value);
  }
  if (field.text !== undefined && field.text !== null) return String(field.text);
  if (field.answer !== undefined && field.answer !== null) return String(field.answer);
  if (field.options && field.options.length) {
    return field.options.map(function(o) { return o.text || o.label || o; }).join(", ");
  }
  return "";
}

function pick(map, keys) {
  for (var i = 0; i < keys.length; i++) {
    var k = normalizeKey(keys[i]);
    if (map[k] !== undefined) return map[k];
  }
  for (var label in map) {
    for (var j = 0; j < keys.length; j++) {
      if (label.indexOf(normalizeKey(keys[j])) !== -1) return map[label];
    }
  }
  return "";
}

function guessTypeDoc(formName, map) {
  if (formName.indexOf("box") !== -1) return "resiliation-box";
  if (formName.indexOf("energie") !== -1 || formName.indexOf("énergie") !== -1) return "resiliation-energie";
  if (formName.indexOf("assurance") !== -1 && formName.indexOf("reclam") === -1) return "resiliation-assurance";
  if (formName.indexOf("mise en demeure") !== -1) return "mise-en-demeure";
  if (formName.indexOf("reclam") !== -1 && formName.indexOf("banque") !== -1) return "reclamation-banque";
  if (formName.indexOf("reclam") !== -1) return "reclamation-assurance";
  if (formName.indexOf("amende") !== -1) return "contestation-amende";
  return "resiliation-mobile";
}

function normalizeKey(s) {
  return String(s || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function appendRow(row) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Commandes")
    || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  ensureHeaders(sheet);
  sheet.appendRow(row);
}

function ensureHeaders(sheet) {
  if (sheet.getLastRow() > 0) return;
  sheet.appendRow(HEADERS);
}

function formatNow() {
  return Utilities.formatDate(new Date(), "Europe/Paris", "dd/MM/yyyy HH:mm");
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
