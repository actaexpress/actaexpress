# -*- coding: utf-8 -*-
"""101 départements métropolitains + helpers slug."""

import unicodedata

DEPTS = [
    ("01", "Ain", "Auvergne-Rhône-Alpes", "Bourg-en-Bresse"),
    ("02", "Aisne", "Hauts-de-France", "Laon"),
    ("03", "Allier", "Auvergne-Rhône-Alpes", "Moulins"),
    ("04", "Alpes-de-Haute-Provence", "Provence-Alpes-Côte d'Azur", "Digne-les-Bains"),
    ("05", "Hautes-Alpes", "Provence-Alpes-Côte d'Azur", "Gap"),
    ("06", "Alpes-Maritimes", "Provence-Alpes-Côte d'Azur", "Nice"),
    ("07", "Ardèche", "Auvergne-Rhône-Alpes", "Privas"),
    ("08", "Ardennes", "Grand Est", "Charleville-Mézières"),
    ("09", "Ariège", "Occitanie", "Foix"),
    ("10", "Aube", "Grand Est", "Troyes"),
    ("11", "Aude", "Occitanie", "Carcassonne"),
    ("12", "Aveyron", "Occitanie", "Rodez"),
    ("13", "Bouches-du-Rhône", "Provence-Alpes-Côte d'Azur", "Marseille"),
    ("14", "Calvados", "Normandie", "Caen"),
    ("15", "Cantal", "Auvergne-Rhône-Alpes", "Aurillac"),
    ("16", "Charente", "Nouvelle-Aquitaine", "Angoulême"),
    ("17", "Charente-Maritime", "Nouvelle-Aquitaine", "La Rochelle"),
    ("18", "Cher", "Centre-Val de Loire", "Bourges"),
    ("19", "Corrèze", "Nouvelle-Aquitaine", "Tulle"),
    ("21", "Côte-d'Or", "Bourgogne-Franche-Comté", "Dijon"),
    ("22", "Côtes-d'Armor", "Bretagne", "Saint-Brieuc"),
    ("23", "Creuse", "Nouvelle-Aquitaine", "Guéret"),
    ("24", "Dordogne", "Nouvelle-Aquitaine", "Périgueux"),
    ("25", "Doubs", "Bourgogne-Franche-Comté", "Besançon"),
    ("26", "Drôme", "Auvergne-Rhône-Alpes", "Valence"),
    ("27", "Eure", "Normandie", "Évreux"),
    ("28", "Eure-et-Loir", "Centre-Val de Loire", "Chartres"),
    ("29", "Finistère", "Bretagne", "Quimper"),
    ("30", "Gard", "Occitanie", "Nîmes"),
    ("31", "Haute-Garonne", "Occitanie", "Toulouse"),
    ("32", "Gers", "Occitanie", "Auch"),
    ("33", "Gironde", "Nouvelle-Aquitaine", "Bordeaux"),
    ("34", "Hérault", "Occitanie", "Montpellier"),
    ("35", "Ille-et-Vilaine", "Bretagne", "Rennes"),
    ("36", "Indre", "Centre-Val de Loire", "Châteauroux"),
    ("37", "Indre-et-Loire", "Centre-Val de Loire", "Tours"),
    ("38", "Isère", "Auvergne-Rhône-Alpes", "Grenoble"),
    ("39", "Jura", "Bourgogne-Franche-Comté", "Lons-le-Saunier"),
    ("40", "Landes", "Nouvelle-Aquitaine", "Mont-de-Marsan"),
    ("41", "Loir-et-Cher", "Centre-Val de Loire", "Blois"),
    ("42", "Loire", "Auvergne-Rhône-Alpes", "Saint-Étienne"),
    ("43", "Haute-Loire", "Auvergne-Rhône-Alpes", "Le Puy-en-Velay"),
    ("44", "Loire-Atlantique", "Pays de la Loire", "Nantes"),
    ("45", "Loiret", "Centre-Val de Loire", "Orléans"),
    ("46", "Lot", "Occitanie", "Cahors"),
    ("47", "Lot-et-Garonne", "Nouvelle-Aquitaine", "Agen"),
    ("48", "Lozère", "Occitanie", "Mende"),
    ("49", "Maine-et-Loire", "Pays de la Loire", "Angers"),
    ("50", "Manche", "Normandie", "Saint-Lô"),
    ("51", "Marne", "Grand Est", "Châlons-en-Champagne"),
    ("52", "Haute-Marne", "Grand Est", "Chaumont"),
    ("53", "Mayenne", "Pays de la Loire", "Laval"),
    ("54", "Meurthe-et-Moselle", "Grand Est", "Nancy"),
    ("55", "Meuse", "Grand Est", "Bar-le-Duc"),
    ("56", "Morbihan", "Bretagne", "Vannes"),
    ("57", "Moselle", "Grand Est", "Metz"),
    ("58", "Nièvre", "Bourgogne-Franche-Comté", "Nevers"),
    ("59", "Nord", "Hauts-de-France", "Lille"),
    ("60", "Oise", "Hauts-de-France", "Beauvais"),
    ("61", "Orne", "Normandie", "Alençon"),
    ("62", "Pas-de-Calais", "Hauts-de-France", "Arras"),
    ("63", "Puy-de-Dôme", "Auvergne-Rhône-Alpes", "Clermont-Ferrand"),
    ("64", "Pyrénées-Atlantiques", "Nouvelle-Aquitaine", "Pau"),
    ("65", "Hautes-Pyrénées", "Occitanie", "Tarbes"),
    ("66", "Pyrénées-Orientales", "Occitanie", "Perpignan"),
    ("67", "Bas-Rhin", "Grand Est", "Strasbourg"),
    ("68", "Haut-Rhin", "Grand Est", "Colmar"),
    ("69", "Rhône", "Auvergne-Rhône-Alpes", "Lyon"),
    ("70", "Haute-Saône", "Bourgogne-Franche-Comté", "Vesoul"),
    ("71", "Saône-et-Loire", "Bourgogne-Franche-Comté", "Mâcon"),
    ("72", "Sarthe", "Pays de la Loire", "Le Mans"),
    ("73", "Savoie", "Auvergne-Rhône-Alpes", "Chambéry"),
    ("74", "Haute-Savoie", "Auvergne-Rhône-Alpes", "Annecy"),
    ("75", "Paris", "Île-de-France", "Paris"),
    ("76", "Seine-Maritime", "Normandie", "Rouen"),
    ("77", "Seine-et-Marne", "Île-de-France", "Melun"),
    ("78", "Yvelines", "Île-de-France", "Versailles"),
    ("79", "Deux-Sèvres", "Nouvelle-Aquitaine", "Niort"),
    ("80", "Somme", "Hauts-de-France", "Amiens"),
    ("81", "Tarn", "Occitanie", "Albi"),
    ("82", "Tarn-et-Garonne", "Occitanie", "Montauban"),
    ("83", "Var", "Provence-Alpes-Côte d'Azur", "Toulon"),
    ("84", "Vaucluse", "Provence-Alpes-Côte d'Azur", "Avignon"),
    ("85", "Vendée", "Pays de la Loire", "La Roche-sur-Yon"),
    ("86", "Vienne", "Nouvelle-Aquitaine", "Poitiers"),
    ("87", "Haute-Vienne", "Nouvelle-Aquitaine", "Limoges"),
    ("88", "Vosges", "Grand Est", "Épinal"),
    ("89", "Yonne", "Bourgogne-Franche-Comté", "Auxerre"),
    ("90", "Territoire de Belfort", "Bourgogne-Franche-Comté", "Belfort"),
    ("91", "Essonne", "Île-de-France", "Évry-Courcouronnes"),
    ("92", "Hauts-de-Seine", "Île-de-France", "Nanterre"),
    ("93", "Seine-Saint-Denis", "Île-de-France", "Bobigny"),
    ("94", "Val-de-Marne", "Île-de-France", "Créteil"),
    ("95", "Val-d'Oise", "Île-de-France", "Cergy"),
    ("2A", "Corse-du-Sud", "Corse", "Ajaccio"),
    ("2B", "Haute-Corse", "Corse", "Bastia"),
]


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFD", name.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("'", "-").replace(" ", "-")
    for old, new in [
        ("ô", "o"), ("é", "e"), ("è", "e"), ("ê", "e"), ("ë", "e"),
        ("à", "a"), ("â", "a"), ("ù", "u"), ("û", "u"), ("ç", "c"),
        ("î", "i"), ("ï", "i"), ("œ", "oe"), ("ü", "u"),
    ]:
        s = s.replace(old, new)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def dept_slug(code: str, name: str) -> str:
    return f"dep-{code.lower()}-{slugify(name)}"


def region_slug(region: str) -> str:
    return slugify(region)
