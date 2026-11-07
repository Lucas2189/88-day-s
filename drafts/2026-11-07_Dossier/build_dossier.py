"""Build the Eazy88 content dossier PDF (publications in posting order).

Usage: python3 -I build_dossier.py <static_fonts_dir> <frames_index.json> <out.pdf>
Run from the repository root.
"""
import json, os, sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

FONTS, FRAMES, OUT = sys.argv[1:4]
pdfmetrics.registerFont(TTFont("Anton", "brand/fonts/Anton-Regular.ttf"))
for w in ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold"]:
    pdfmetrics.registerFont(TTFont(f"PJS-{w}", os.path.join(FONTS, f"PJS-{w}.ttf")))

INK = colors.HexColor("#14110D")
SURF = colors.HexColor("#1F1B16")
CREAM = colors.HexColor("#FEF4E6")
ORANGE = colors.HexColor("#DB6530")
ORANGE_L = colors.HexColor("#F99660")
GREEN = colors.HexColor("#147839")
MUTED = colors.HexColor("#6B6155")
LINE = colors.HexColor("#DDD4C5")
PAPER = colors.HexColor("#F7F2EA")

st = {
    "h1": ParagraphStyle("h1", fontName="Anton", fontSize=30, leading=34, textColor=INK, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="Anton", fontSize=17, leading=21, textColor=INK, spaceBefore=8, spaceAfter=4),
    "kick": ParagraphStyle("kick", fontName="PJS-Bold", fontSize=9, leading=12, textColor=ORANGE, spaceAfter=2),
    "body": ParagraphStyle("body", fontName="PJS-Regular", fontSize=9.5, leading=13.5, textColor=INK, alignment=TA_LEFT),
    "small": ParagraphStyle("small", fontName="PJS-Medium", fontSize=8, leading=11, textColor=MUTED),
    "en": ParagraphStyle("en", fontName="PJS-Medium", fontSize=9.5, leading=13.5, textColor=INK, backColor=PAPER,
                         borderColor=LINE, borderWidth=0.6, borderPadding=6, spaceBefore=4, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName="PJS-Regular", fontSize=8.5, leading=11.5, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="PJS-Bold", fontSize=8.5, leading=11.5, textColor=INK),
}
P = lambda t, s="body": Paragraph(t, st[s])
E = lambda t: escape("".join(ch for ch in t if ord(ch) < 0x2190 or ch in "→·–—")).replace("\n", "<br/>")  # no emoji glyphs in the brand fonts


def badge(text, ok):
    col = GREEN if ok else ORANGE
    from reportlab.pdfbase.pdfmetrics import stringWidth
    t = Table([[Paragraph(f'<font color="white">{text}</font>', ParagraphStyle("b", fontName="PJS-Bold", fontSize=8.5, leading=11))]],
              colWidths=[stringWidth(text, "PJS-Bold", 8.5) + 14])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), col), ("LEFTPADDING", (0, 0), (-1, -1), 6),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    t.hAlign = "LEFT"
    return t


def facts(rows):
    t = Table([[P(k, "cellb"), P(v, "cell")] for k, v in rows], colWidths=[38 * mm, 136 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def grid(paths, w, h, cols, labels=None):
    cells, row = [], []
    for i, p in enumerate(paths):
        im = Image(p, width=w, height=h)
        item = [im] if not labels else [im, P(labels[i], "small")]
        row.append(item)
        if len(row) == cols:
            cells.append(row)
            row = []
    if row:
        cells.append(row + [""] * (cols - len(row)))
    t = Table(cells, colWidths=[w + 4 * mm] * cols)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    t.hAlign = "LEFT"
    return t


def vo_table(lines):
    t = Table([[P(f"{i}", "cellb"), P(E(x), "cell")] for i, x in enumerate(lines, 1)], colWidths=[8 * mm, 166 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.3, LINE), ("TOPPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def caption_of(path):
    return open(path, encoding="utf-8").read().strip()


def cover(canv, doc):
    W, H = A4
    canv.saveState()
    canv.setFillColor(INK)
    canv.rect(0, 0, W, H, stroke=0, fill=1)
    canv.drawImage("brand/logos/eazy88_app-icon_994px_from-website_2026-11-07.png", 20 * mm, H - 62 * mm, 32 * mm, 32 * mm, mask="auto")
    canv.setFillColor(CREAM)
    canv.setFont("Anton", 46)
    canv.drawString(20 * mm, H - 95 * mm, "DOSSIER DE CONTENUS")
    canv.setFillColor(ORANGE_L)
    canv.drawString(20 * mm, H - 113 * mm, "EAZY88 · NOVEMBRE 2026")
    canv.setFillColor(CREAM)
    canv.setFont("PJS-Medium", 12)
    y = H - 135 * mm
    for ln in ["Toutes les publications créées, dans l'ordre de publication recommandé.",
               "Explications en français · contenu public en anglais.",
               "Rien n'a été publié. Coût de production : 0 crédit."]:
        canv.drawString(20 * mm, y, ln)
        y -= 7 * mm
    canv.setFont("PJS-Bold", 10)
    canv.setFillColor(ORANGE_L)
    canv.drawString(20 * mm, 20 * mm, "Préparé le 7 novembre 2026 · @eazy88llc")
    canv.restoreState()


def later(canv, doc):
    W, H = A4
    canv.saveState()
    canv.setFont("PJS-Medium", 7.5)
    canv.setFillColor(MUTED)
    canv.drawString(18 * mm, 10 * mm, "Eazy88 · Dossier de contenus · 7 nov. 2026")
    canv.drawRightString(W - 18 * mm, 10 * mm, f"{doc.page}")
    canv.setFillColor(ORANGE)
    canv.rect(0, H - 4 * mm, W, 4 * mm, stroke=0, fill=1)
    canv.restoreState()


frames = json.load(open(FRAMES))
fr = lambda k: [p for p, _ in frames[k]]
fl = lambda k: [f"{t:.1f} s" for _, t in frames[k]]

story = [PageBreak()]

# ---------------------------------------------------------------- overview
story += [P("VUE D'ENSEMBLE", "kick"), P("Ordre de publication", "h1"),
          P("L'ordre suit la règle de rotation des thèmes : on commence par l'actualité et le pratique, "
            "et les contenus sur les relevés de travail passent en dernier, car 3 des 4 vidéos déjà publiées "
            "portent déjà sur ce thème. Espacez les publications pour pouvoir comparer leurs résultats. "
            "Heure d'Adélaïde ; 18 h 30 est une heure suggérée à tester. Rappels : Eazy88_Calendrier_Nov2026.ics.")]
order = [
    ["#", "Publication", "Plateforme", "Objectif", "Quand", "Statut"],
    ["1", "Visa ballot: what's confirmed", "TikTok · vidéo 34 s", "Partages", "Sam. 7 nov. 18 h 30", "Prêt"],
    ["2", "Car checks before you pay", "TikTok · vidéo 30 s", "Sauvegardes", "Mar. 10 nov. 18 h 30", "Prêt"],
    ["3", "Record-keeping checklist", "Instagram · carrousel 5 visuels", "Sauvegardes", "Ven. 13 nov. 18 h 30", "Prêt"],
    ["4", "Work records question", "Instagram · 3 Stories", "Réponses + clics", "Sam. 14 nov. 18 h 30", "Prêt"],
    ["5", "88 days. Lost count?", "Reel 20 s (Instagram / TikTok)", "Visites App Store", "Mer. 18 nov. 18 h 30, si l'enregistrement est reçu le 15", "Bloqué"],
]
t = Table([[P(c, "cellb" if r == 0 else "cell") for c in row] for r, row in enumerate(order)],
          colWidths=[8 * mm, 46 * mm, 42 * mm, 27 * mm, 30 * mm, 21 * mm])
ts = [("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("BACKGROUND", (0, 0), (-1, 0), PAPER), ("VALIGN", (0, 0), (-1, -1), "TOP")]
for r in range(1, 6):
    ts.append(("TEXTCOLOR", (5, r), (5, r), GREEN if r < 5 else ORANGE))
t.setStyle(TableStyle(ts))
story += [Spacer(1, 6), t, Spacer(1, 10),
          P("Règles valables pour chaque publication", "h2"),
          P("• Activer le label « AI-generated content » pour les vidéos (voix IA).<br/>"
            "• Revérifier les sources officielles le jour de la publication (dates indiquées sur chaque visuel).<br/>"
            "• Une idée et un seul CTA par publication. Aucune promotion payante sans décision explicite.<br/>"
            "• Relever les statistiques à 72 h et 7 jours dans <i>analytics/</i> (chiffres réels uniquement)."),
          P("Les vidéos ne peuvent pas être lues dans un PDF : chaque vidéo est présentée par des images clés "
            "extraites du fichier MP4 final, avec son script et sa légende. Les fichiers sont dans <i>exports/</i>.", "small")]

# ---------------------------------------------------------------- 1 VisaBallot
vb = json.load(open("drafts/2026-11-07_VisaBallot/audio/vo_timings.json"))
story += [PageBreak(), P("PUBLICATION 1 · TIKTOK · SAMEDI 7 NOV. · 18 H 30", "kick"), P("Visa ballot: what's confirmed", "h1"), badge("PRÊT À PUBLIER", True), Spacer(1, 6),
          facts([("Fichier", "exports/2026-11-07_VisaBallot/Eazy88_TikTok_VisaBallot_A.mp4 · 1080×1920 · 34 s · voix + sous-titres incrustés"),
                 ("Pour qui", "Titulaires d'un visa 417 ou 462 qui font leurs 88 jours et ont entendu parler du ballot"),
                 ("Objectif · CTA", "Partages · « Send this to a mate doing their 88 days. »"),
                 ("À vérifier le jour J", "La page Home Affairs : si le ballot y est publié, la vidéo est périmée")]),
          P("Images clés (MP4 final)", "h2"), grid(fr("VisaBallot"), 32 * mm, 57 * mm, 5, fl("VisaBallot")),
          P("Voix off = sous-titres (anglais)", "h2"), vo_table([v["text"] for v in vb.values()]),
          P("Légende (anglais, prête à coller)", "h2"),
          P(E(caption_of("exports/2026-11-07_VisaBallot/Eazy88_TikTok_VisaBallot_Caption.txt")), "en")]

# ---------------------------------------------------------------- 2 CarChecks
cc = json.load(open("drafts/2026-11-07_CarChecks/audio/vo_timings.json"))
story += [PageBreak(), P("PUBLICATION 2 · TIKTOK · MARDI 10 NOV. · 18 H 30", "kick"), P("Car checks before you pay", "h1"), badge("PRÊT À PUBLIER", True), Spacer(1, 6),
          facts([("Fichier", "exports/2026-11-07_CarChecks/Eazy88_TikTok_CarChecks_A.mp4 · 1080×1920 · 30 s · voix + sous-titres incrustés"),
                 ("Pour qui", "Backpackers qui achètent une voiture ou un van d'occasion pour un road trip"),
                 ("Objectif · CTA", "Sauvegardes · « Save this for when you're car shopping. »"),
                 ("À vérifier le jour J", "Le prix de 2 $ sur ppsr.gov.au/carcheck")]),
          P("Images clés (MP4 final)", "h2"), grid(fr("CarChecks"), 32 * mm, 57 * mm, 5, fl("CarChecks")),
          P("Voix off = sous-titres (anglais)", "h2"), vo_table([v["text"] for v in cc.values()]),
          P("Légende (anglais, prête à coller)", "h2"),
          P(E(caption_of("exports/2026-11-07_CarChecks/Eazy88_TikTok_CarChecks_Caption.txt")), "en")]

# ---------------------------------------------------------------- 3 Carousel
cap = caption_of("exports/2026-11-07_LostCount/Eazy88_LostCount_Captions.txt")
car_cap = cap.split("=== INSTAGRAM CAROUSEL (5 slides) ===")[1].split("===")[0].strip()
st_cap = cap.split("=== INSTAGRAM STORIES (3 frames, no caption field) ===")[1].split("===")[0].strip()
reel_cap = cap.split("=== REEL")[1].split("===", 1)[1].split("Note: hashtags")[0].strip()
slides = [f"exports/2026-11-07_LostCount/carousel/Eazy88_Carousel_RecordsChecklist_0{i}.png" for i in range(1, 6)]
story += [PageBreak(), P("PUBLICATION 3 · INSTAGRAM · VENDREDI 13 NOV. · 18 H 30", "kick"), P("Record-keeping checklist (carrousel)", "h1"), badge("PRÊT À PUBLIER", True), Spacer(1, 6),
          facts([("Fichiers", "exports/2026-11-07_LostCount/carousel/ · 5 PNG 1080×1350, à publier dans l'ordre 1 → 5"),
                 ("Objectif · CTA", "Sauvegardes · « Save this for your next job » (visuel 5)"),
                 ("Sources", "Home Affairs (417, preuves du travail spécifié) · Fair Work Ombudsman · vérifiées le 7 nov. 2026")]),
          Spacer(1, 6), grid(slides[:2], 84 * mm, 105 * mm, 2, ["Visuel 1/5", "Visuel 2/5"]),
          PageBreak(), grid(slides[2:4], 84 * mm, 105 * mm, 2, ["Visuel 3/5", "Visuel 4/5"]),
          grid(slides[4:], 84 * mm, 105 * mm, 2, ["Visuel 5/5"]),
          PageBreak(), P("Légende du carrousel (anglais, prête à coller)", "h2"), P(E(car_cap), "en")]

# ---------------------------------------------------------------- 4 Stories
stories = [f"exports/2026-11-07_LostCount/stories/{n}.png" for n in
           ["Eazy88_Story_RecordsQuestion_01", "Eazy88_Story_RecordsAction_02", "Eazy88_Story_RecordsCTA_03"]]
story += [Spacer(1, 10), P("PUBLICATION 4 · INSTAGRAM · SAMEDI 14 NOV. · 18 H 30", "kick"), P("Work records (3 Stories)", "h1"), badge("PRÊT À PUBLIER", True), Spacer(1, 6),
          facts([("Fichiers", "exports/2026-11-07_LostCount/stories/ · 3 PNG 1080×1920, à publier dans l'ordre 1 → 3"),
                 ("Objectif · CTA", "Réponses au sondage, puis un seul CTA : le lien App Store (Story 3)"),
                 ("Attention", "Story 3 : l'écran d'accueil officiel affiche « 7 validated ». Remplacez-le par votre capture si le mot vous gêne.")]),
          Spacer(1, 4), grid(stories, 52 * mm, 92 * mm, 3, ["Story 1 · question", "Story 2 · action", "Story 3 · CTA"]),
          P("Stickers à ajouter dans Instagram", "h2"), P(E(st_cap), "en")]

# ---------------------------------------------------------------- 5 Reel (blocked)
lc = json.load(open("drafts/2026-11-07_LostCount/reel/audio/vo_timings.json"))
story += [PageBreak(), P("PUBLICATION 5 · REEL · MERCREDI 18 NOV. (SI PRÊT)", "kick"), P("88 days. Lost count?", "h1"),
          badge("BLOQUÉ · BROUILLON NON PUBLIABLE", False), Spacer(1, 6),
          facts([("Blocage", "Le Reel doit montrer le vrai parcours dans l'app (Add › Read › Check › Save › Track). "
                             "Aucun enregistrement d'écran réel n'existe : les images ci-dessous viennent de l'<b>aperçu de travail</b> "
                             "avec des zones PLACEHOLDER. <b>Ce n'est pas une vidéo finie.</b>"),
                 ("Pour débloquer", "Enregistrer l'écran de l'iPhone (compte de démo, 15 à 25 s) en important la fiche de paie EXAMPLE fournie, "
                                    "puis déposer le fichier sous drafts/2026-11-07_LostCount/reel/footage/eazy88_add-payslip_demo.mp4."),
                 ("Objectif · CTA", "Visites App Store · « Try Eazy88 free on the App Store. »")]),
          P("Images clés de l'aperçu (brouillon)", "h2"), grid(fr("LostCount"), 21 * mm, 37 * mm, 7, fl("LostCount")),
          P("Voix off = sous-titres (anglais)", "h2"), vo_table([v["text"] for v in lc.values()]),
          P("Légende prévue (anglais)", "h2"), P(E(reel_cap), "en")]

# ---------------------------------------------------------------- annex
story += [PageBreak(), P("ANNEXE", "kick"), P("Où trouver chaque fichier", "h1"),
          facts([("exports/", "Livrables finaux : vidéos MP4, sous-titres SRT, voix seule WAV, covers, légendes, carrousel, Stories, sources éditables"),
                 ("drafts/", "Brouillons, aperçus, planches de contrôle, accessoires (fiche de paie EXAMPLE)"),
                 ("briefs/", "Un brief par contenu : objectif, recherche, tableau des affirmations"),
                 ("brand/", "Icône officielle, polices Anton et Plus Jakarta Sans, identité de marque"),
                 ("product/product-facts.md", "Fonctionnalités vérifiées, infos non confirmées, assets manquants"),
                 ("templates/tools/", "Voix off (Kokoro), rendu vidéo, rendu des images fixes"),
                 ("analytics/", "Référence TikTok du 7 nov. 2026 et tableau de suivi")]),
          P("Sources officielles utilisées", "h2"),
          P("immi.homeaffairs.gov.au (WHM latest news ; specified work 417 et 462 ; Second Working Holiday visa 417) · "
            "fairwork.gov.au (record-keeping and pay slips) · ppsr.gov.au · scamwatch.gov.au · vicroads.vic.gov.au · "
            "mylicence.sa.gov.au · Time Out Australia (24 sept. 2026) · fiche App Store et site eazy88.com (7 nov. 2026).", "small")]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                        title="Eazy88 — Dossier de contenus", author="Eazy88")
doc.build(story, onFirstPage=cover, onLaterPages=later)
print("ok", OUT)
