/**
 * ActaExpress — Automatisation 100 % (Tally + Stripe → PDF → email client)
 *
 * INSTALLATION : voir content/automation/AUTO-PDF-GUIDE.txt
 *
 * Flux :
 *   1. Client remplit Tally → ligne dans Sheet (paye = non)
 *   2. Client paie Stripe → script génère PDF (OpenAI) → email au client
 */

var HEADERS = [
  "date_soumission", "email", "type_doc", "paye", "pdf_envoye",
  "civilite", "nom", "prenom", "adresse", "code_postal", "ville",
  "telephone", "operateur", "operateur_autre", "numero_ligne",
  "numero_client", "date_resiliation", "motif", "motif_autre",
  "arret_prelevements", "infos_complementaires", "reponses_json",
  "stripe_payment_id"
];

var MOBILE_TEMPLATE =
  "Expéditeur en haut à gauche, destinataire opérateur, date, objet, corps formel, signature.\n" +
  "Inclure : numéro de ligne, numéro client, date d'effet, motif, arrêt prélèvements si demandé.";

function doPost(e) {
  try {
    var raw = e.postData ? e.postData.contents : "";
    var payload = raw ? JSON.parse(raw) : {};

    if (isStripeEvent(payload)) {
      return handleStripe(payload);
    }
    if (isTallyEvent(payload)) {
      return handleTally(payload);
    }
    return jsonOut({ ok: false, error: "unknown_payload" });
  } catch (err) {
    Logger.log(err);
    return jsonOut({ ok: false, error: String(err) });
  }
}

function doGet() {
  return jsonOut({ ok: true, service: "ActaExpress auto PDF" });
}

// --- Tally : enregistrer la commande ---

function handleTally(payload) {
  var row = buildRow(payload);
  appendRow(row);
  return jsonOut({ ok: true, step: "tally_saved", email: row[1] });
}

function isTallyEvent(p) {
  if (!p) return false;
  if (p.eventType === "FORM_RESPONSE") return true;
  if (p.data && p.data.fields) return true;
  return false;
}

function buildRow(payload) {
  var data = payload.data || payload;
  var fields = data.fields || [];
  var map = fieldsToMap(fields);
  var formName = (data.formName || data.nom_formulaire || payload.formName || "").toLowerCase();
  if (!formName && data.formId) formName = String(data.formId);
  var typeDoc = guessTypeDoc(formName, map);

  return [
    formatNow(),
    pick(map, ["email", "e-mail", "courriel"]),
    typeDoc,
    "non",
    "non",
    pick(map, ["civilite", "civilité"]),
    pick(map, ["nom"]),
    pick(map, ["prenom", "prénom"]),
    pick(map, ["adresse", "adresse (numero et rue)", "adresse (numéro et rue)"]),
    pick(map, ["code postal"]),
    pick(map, ["ville"]),
    pick(map, ["telephone", "téléphone"]),
    pick(map, ["operateur", "opérateur"]),
    pick(map, ["precisez l'operateur", "précisez l'opérateur"]),
    pick(map, ["numero de ligne", "numéro de ligne"]),
    pick(map, ["numero client", "numéro client", "reference contrat", "référence contrat"]),
    pick(map, ["date souhaitee", "date souhaitée", "date de resiliation"]),
    pick(map, ["motif de resiliation", "motif de résiliation", "motif"]),
    pick(map, ["precisez le motif"]),
    pick(map, ["arret des prelevements", "arrêt des prélèvements"]),
    pick(map, ["informations complementaires", "informations complémentaires"]),
    JSON.stringify(map),
    ""
  ];
}

// --- Stripe : après paiement → PDF + email ---

function handleStripe(payload) {
  var type = payload.type || "";
  if (type !== "checkout.session.completed") {
    return jsonOut({ ok: true, skipped: type });
  }

  var session = payload.data && payload.data.object ? payload.data.object : {};
  if (session.payment_status && session.payment_status !== "paid") {
    return jsonOut({ ok: true, skipped: "not_paid" });
  }

  var email = extractStripeEmail(session);
  if (!email) {
    return jsonOut({ ok: false, error: "no_email_in_stripe" });
  }

  var sheet = getSheet();
  var rowIndex = findPendingRow(sheet, email);
  if (rowIndex < 0) {
    return jsonOut({ ok: false, error: "no_pending_order", email: email });
  }

  var rowData = rowToObject(sheet, rowIndex);
  var letterText = generateLetter(rowData);
  var pdfBlob = createPdfBlob(letterText, "ActaExpress-" + rowData.type_doc + ".pdf");
  sendClientEmail(email, rowData, pdfBlob);

  updateRow(sheet, rowIndex, {
    paye: "oui",
    pdf_envoye: "oui",
    stripe_payment_id: session.id || session.payment_intent || ""
  });

  notifyAdmin(email, rowData.type_doc);

  return jsonOut({ ok: true, step: "pdf_sent", email: email });
}

function isStripeEvent(p) {
  return !!(p && p.type && String(p.type).indexOf(".") !== -1 && p.data && p.data.object);
}

function extractStripeEmail(session) {
  if (session.customer_details && session.customer_details.email) {
    return String(session.customer_details.email).trim().toLowerCase();
  }
  if (session.customer_email) return String(session.customer_email).trim().toLowerCase();
  return "";
}

function findPendingRow(sheet, email) {
  var data = sheet.getDataRange().getValues();
  var target = email.toLowerCase();
  for (var i = data.length - 1; i >= 1; i--) {
    var rowEmail = String(data[i][1] || "").trim().toLowerCase();
    var paye = String(data[i][3] || "").toLowerCase();
    var pdfEnvoye = String(data[i][4] || "").toLowerCase();
    if (rowEmail === target && paye === "non" && pdfEnvoye === "non") {
      return i + 1;
    }
  }
  return -1;
}

function rowToObject(sheet, rowIndex) {
  var headers = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  var values = sheet.getRange(rowIndex, 1, 1, HEADERS.length).getValues()[0];
  var obj = {};
  for (var i = 0; i < headers.length; i++) {
    obj[String(headers[i])] = values[i];
  }
  return obj;
}

function updateRow(sheet, rowIndex, patch) {
  var headers = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  for (var key in patch) {
    var col = headers.indexOf(key);
    if (col >= 0) sheet.getRange(rowIndex, col + 1).setValue(patch[key]);
  }
}

// --- OpenAI ---

function generateLetter(rowData) {
  var apiKey = getProp("OPENAI_API_KEY");
  if (!apiKey) throw new Error("OPENAI_API_KEY manquante dans Propriétés du script");

  var typeLabel = typeDocLabel(rowData.type_doc);
  var prompt =
    "Tu rédiges un document administratif professionnel en français.\n\n" +
    "RÈGLES STRICTES :\n" +
    "- Utilise UNIQUEMENT les informations fournies\n" +
    "- N'invente AUCUNE date, numéro ou adresse\n" +
    "- Ton formel, format lettre complète (expéditeur, destinataire, objet, corps, politesse, signature)\n" +
    "- Si une info manque, indique [À COMPLÉTER]\n" +
    "- Réponds UNIQUEMENT avec le texte du document, sans commentaire\n\n" +
    "TYPE : " + typeLabel + "\n\n" +
    "MODÈLE : " + MOBILE_TEMPLATE + "\n\n" +
    "DONNÉES CLIENT (JSON) :\n" + (rowData.reponses_json || JSON.stringify(rowData)) + "\n\n" +
    "Date du jour : " + formatNow();

  var body = {
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "Tu es rédacteur de courriers administratifs français." },
      { role: "user", content: prompt }
    ],
    temperature: 0.3
  };

  var res = UrlFetchApp.fetch("https://api.openai.com/v1/chat/completions", {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + apiKey },
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });

  var json = JSON.parse(res.getContentText());
  if (!json.choices || !json.choices[0]) {
    throw new Error("OpenAI error: " + res.getContentText());
  }
  return json.choices[0].message.content.trim();
}

function typeDocLabel(typeDoc) {
  var map = {
    "resiliation-mobile": "Lettre de résiliation forfait mobile",
    "resiliation-box": "Lettre de résiliation box internet",
    "resiliation-energie": "Lettre de résiliation énergie",
    "resiliation-assurance": "Lettre de résiliation assurance",
    "mise-en-demeure": "Mise en demeure",
    "reclamation-assurance": "Réclamation assurance",
    "reclamation-banque": "Réclamation banque",
    "contestation-amende": "Contestation amende"
  };
  return map[typeDoc] || "Document administratif";
}

// --- PDF + emails ---

function createPdfBlob(text, filename) {
  var doc = DocumentApp.create("ActaExpress_temp_" + Date.now());
  var body = doc.getBody();
  body.clear();
  body.setText(text);
  body.setFontFamily("Arial").setFontSize(11);
  doc.saveAndClose();

  var docFile = DriveApp.getFileById(doc.getId());
  var pdf = docFile.getAs("application/pdf").setName(filename);
  docFile.setTrashed(true);
  return pdf;
}

function sendClientEmail(email, rowData, pdfBlob) {
  var subject = "ActaExpress — Votre document est prêt";
  var body =
    "Bonjour,\n\n" +
    "Merci pour votre commande ActaExpress.\n\n" +
    "Vous trouverez en pièce jointe votre document personnalisé, prêt à imprimer et à envoyer en recommandé avec accusé de réception.\n\n" +
    "Checklist :\n" +
    "- Imprimez et signez le document\n" +
    "- Joignez les pièces indiquées dans la lettre\n" +
    "- Conservez l'accusé de réception\n\n" +
    "Une question ? Répondez à cet email.\n\n" +
    "Bien cordialement,\n" +
    "ActaExpress\n" +
    "https://actaexpress.fr\n" +
    "acta.express0@gmail.com";

  GmailApp.sendEmail(email, subject, body, {
    attachments: [pdfBlob],
    name: "ActaExpress"
  });
}

function notifyAdmin(clientEmail, typeDoc) {
  var admin = getProp("ADMIN_EMAIL") || Session.getActiveUser().getEmail();
  if (!admin) return;
  GmailApp.sendEmail(
    admin,
    "ActaExpress — Commande traitée (" + typeDoc + ")",
    "PDF envoyé à : " + clientEmail + "\nType : " + typeDoc + "\n" + formatNow()
  );
}

// --- Helpers ---

function fieldsToMap(fields) {
  var map = {};
  for (var i = 0; i < fields.length; i++) {
    var f = fields[i];
    var label = normalizeKey(f.label || f.title || f.key || ("field_" + i));
    var val = extractFieldValue(f);
    if (val) map[label] = val;
  }
  return map;
}

function extractFieldValue(field) {
  if (field.value !== undefined && field.value !== null && field.value !== "") {
    return String(field.value);
  }
  if (field.text) return String(field.text);
  if (field.answer) return String(field.answer);
  return "";
}

function pick(map, keys) {
  for (var i = 0; i < keys.length; i++) {
    var k = normalizeKey(keys[i]);
    if (map[k]) return map[k];
  }
  for (var label in map) {
    for (var j = 0; j < keys.length; j++) {
      if (label.indexOf(normalizeKey(keys[j])) !== -1) return map[label];
    }
  }
  return "";
}

function guessTypeDoc(formName, map) {
  formName = (formName || "").toLowerCase();
  if (formName.indexOf("box") !== -1) return "resiliation-box";
  if (formName.indexOf("energie") !== -1 || formName.indexOf("énergie") !== -1) return "resiliation-energie";
  if (formName.indexOf("assurance") !== -1 && formName.indexOf("reclam") === -1) return "resiliation-assurance";
  if (formName.indexOf("mise en demeure") !== -1) return "mise-en-demeure";
  if (formName.indexOf("banque") !== -1) return "reclamation-banque";
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

function getSheet() {
  var id = getProp("SPREADSHEET_ID");
  var ss = id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Commandes") || ss.getActiveSheet();
  ensureHeaders(sheet);
  return sheet;
}

function ensureHeaders(sheet) {
  if (sheet.getLastRow() > 0) return;
  sheet.appendRow(HEADERS);
}

function appendRow(row) {
  getSheet().appendRow(row);
}

function formatNow() {
  return Utilities.formatDate(new Date(), "Europe/Paris", "dd/MM/yyyy HH:mm");
}

function getProp(key) {
  return PropertiesService.getScriptProperties().getProperty(key);
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
