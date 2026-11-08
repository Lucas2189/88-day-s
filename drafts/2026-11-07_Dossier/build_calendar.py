"""Eazy88 posting calendar, Nov 2026: one source of truth -> .ics (phone calendar), one-page PDF, Markdown.

Usage (from repo root): python3 -I build_calendar.py <static_fonts_dir> <out_dir>
Times are Adelaide local time (ACDT, UTC+10:30 in November).
"""
import datetime as dt
import os, sys
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS, OUT = sys.argv[1:3]
ADL = ZoneInfo("Australia/Adelaide")

# kind: post_tt (TikTok), post_ig (Instagram), post_reel, stats, todo
EVENTS = [
    (7, "18:30", "post_tt", "Visa ballot (publiée)", 30,
     "Publiée par Lucas le 7 nov. sur TikTok, YouTube Shorts et Instagram (boostée)."),
    (9, "18:30", "post_tt", "Vidéo · Car checks", 30,
     "Fichier : exports/2026-11-07_CarChecks/Eazy88_TikTok_CarChecks_A.mp4\nAvant : confirmer le prix de 2 $ sur ppsr.gov.au/carcheck.\n"
     "Label AI-generated content. Légende : Eazy88_TikTok_CarChecks_Caption.txt"),
    (10, "18:00", "stats", "Stats 72 h · Visa ballot", 15,
     "TikTok, YouTube, Instagram séparés : comptes atteints, partages, saves, durée moyenne, complétion. Instagram : montant du boost, part payant / organique."),
    (10, "18:30", "post_tt", "Vidéo · 6-month rule", 30,
     "Fichier : exports/2026-11-08_SixMonthRule/Eazy88_TikTok_SixMonthRule_A.mp4\nAvant : revérifier la page Home Affairs condition 8547.\n"
     "Label AI-generated content. Légende : Eazy88_TikTok_SixMonthRule_Caption.txt"),
    (11, "18:30", "post_ig", "Instagram · Carrousel", 30,
     "Fichiers : exports/2026-11-07_LostCount/carousel (5 PNG, ordre 01 à 05).\nLégende : section CAROUSEL de Eazy88_LostCount_Captions.txt"),
    (12, "18:00", "stats", "Stats 72 h · Car checks", 15, "Objectif : saves."),
    (12, "18:30", "post_tt", "Vidéo · Visa location", 30,
     "Fichier : exports/2026-11-08_VisaGrantLocation/Eazy88_TikTok_VisaGrantLocation_A.mp4\nAvant : revérifier Home Affairs WHM latest news.\n"
     "Label AI-generated content. Légende : Eazy88_TikTok_VisaGrantLocation_Caption.txt"),
    (13, "18:00", "stats", "Stats 72 h · 6-month rule", 15, "Objectif : saves."),
    (13, "18:30", "post_ig", "Instagram · 3 Stories", 20,
     "Fichiers : exports/2026-11-07_LostCount/stories, ordre 01, 02, 03.\nStory 1 : sticker sondage. Story 3 : sticker lien https://apps.apple.com/au/app/eazy88/id6759782986"),
    (14, "17:30", "stats", "Votes du sondage (Stories)", 15, "Les Stories disparaissent à 18 h 30 : noter les résultats avant."),
    (14, "18:00", "stats", "Stats 7 j · Visa ballot", 15, "Relevé à 7 jours."),
    (14, "18:15", "stats", "Stats 72 h · Carrousel", 15, "Objectif : saves."),
    (14, "18:30", "todo", "Vidéo à produire", 30, "PAS ENCORE PRODUITE : publier seulement si livrée et validée."),
    (15, "10:00", "todo", "Envoyer l'enregistrement", 30,
     "Compte de démo, fiche de paie EXAMPLE, 20 à 30 s : voir drafts/2026-11-07_LostCount/reel/footage/README.md"),
    (15, "18:00", "stats", "Stats 72 h · Visa location", 15, "Objectif : partages."),
    (15, "18:30", "todo", "Story sondage (à produire)", 15, "Uniquement les vrais chiffres du sondage."),
    (16, "18:00", "stats", "Stats 7 j · Car checks", 15, "Relevé à 7 jours."),
    (16, "18:30", "todo", "Vidéo à produire", 30, "PAS ENCORE PRODUITE : publier seulement si livrée et validée."),
    (17, "18:00", "stats", "Stats 7 j · 6-month rule", 15, "Relevé à 7 jours."),
    (17, "18:30", "todo", "Vidéo à produire", 30, "PAS ENCORE PRODUITE : publier seulement si livrée et validée."),
    (18, "18:00", "stats", "Stats 7 j · Carrousel", 15, "Relevé à 7 jours."),
    (18, "18:30", "post_reel", "Reel · Lost count? (si prêt)", 30,
     "SEULEMENT si l'enregistrement d'écran est reçu et le Reel final validé. Sinon : décaler."),
    (19, "18:00", "stats", "Stats 7 j · Visa location", 15, "Relevé à 7 jours."),
    (21, "18:00", "stats", "Stats 72 h · Reel", 15, "Seulement si le Reel a été publié le 18."),
    (25, "18:00", "stats", "Stats Reel + bilan du mois", 45, "Comparer toutes les publications de novembre et préparer décembre."),
]
KIND = {
    "post_tt": ("Vidéo", "#14110D", "#FEF4E6"),
    "post_ig": ("Instagram", "#DB6530", "#FFFFFF"),
    "post_reel": ("Reel (si prêt)", "#F99660", "#14110D"),
    "stats": ("Statistiques", "#EDFAF1", "#147839"),
    "todo": ("À faire", "#FCD9A8", "#5A3A10"),
}


def when(day, hm, minutes=0):
    h, m = map(int, hm.split(":"))
    return dt.datetime(2026, 11, day, h, m, tzinfo=ADL) + dt.timedelta(minutes=minutes)


# ---------------------------------------------------------------- .ics
def ics_text(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > (75 if not out else 74):
            out.append(cur)
            cur = b""
        cur += b
    out.append(cur)
    return "\r\n ".join(x.decode("utf-8") for x in out)


def write_ics(path):
    z = lambda t: t.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Eazy88//Posting calendar//FR", "CALSCALE:GREGORIAN",
         "METHOD:PUBLISH", "X-WR-CALNAME:Eazy88 · Publications", "X-WR-TIMEZONE:Australia/Adelaide"]
    for i, (day, hm, kind, title, dur, desc) in enumerate(EVENTS):
        start = when(day, hm)
        L += ["BEGIN:VEVENT", f"UID:eazy88-2026-11-{day:02d}-{i}@eazy88-marketing", "DTSTAMP:20261107T000000Z",
              f"DTSTART:{z(start)}", f"DTEND:{z(start + dt.timedelta(minutes=dur))}",
              f"SUMMARY:{ics_text('Eazy88 · ' + title)}", f"DESCRIPTION:{ics_text(desc)}",
              "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{ics_text(title)}",
              f"TRIGGER:-PT{60 if kind == 'todo' else 15}M", "END:VALARM", "END:VEVENT"]
    L.append("END:VCALENDAR")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(fold(l) for l in L) + "\r\n")


# ---------------------------------------------------------------- PDF (one page, landscape)
def write_pdf(path):
    from reportlab.pdfgen import canvas
    pdfmetrics.registerFont(TTFont("Anton", "brand/fonts/Anton-Regular.ttf"))
    for w in ["Medium", "SemiBold", "Bold"]:
        pdfmetrics.registerFont(TTFont(f"PJS-{w}", os.path.join(FONTS, f"PJS-{w}.ttf")))
    W, H = landscape(A4)
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Eazy88 — Calendrier de publication, novembre 2026")
    c.setFillColor(colors.HexColor("#DB6530"))
    c.rect(0, H - 4 * mm, W, 4 * mm, stroke=0, fill=1)
    c.drawImage("brand/logos/eazy88_app-icon_994px_from-website_2026-11-07.png", 14 * mm, H - 24 * mm, 13 * mm, 13 * mm, mask="auto")
    c.setFillColor(colors.HexColor("#14110D"))
    c.setFont("Anton", 24)
    c.drawString(31 * mm, H - 19.5 * mm, "CALENDRIER DE PUBLICATION · NOVEMBRE 2026")
    c.setFont("PJS-Medium", 9)
    c.setFillColor(colors.HexColor("#6B6155"))
    c.drawString(31 * mm, H - 25 * mm, "Heure d'Adélaïde (ACDT). Heure suggérée à tester : 18 h 30. Rien n'est publié automatiquement : vous postez vous-même.")
    # legend
    x = W - 14 * mm
    for k in ["todo", "stats", "post_reel", "post_ig", "post_tt"]:
        lab, bg, fg = KIND[k]
        tw = pdfmetrics.stringWidth(lab, "PJS-Bold", 8) + 10
        x -= tw + 4
        c.setFillColor(colors.HexColor(bg))
        c.roundRect(x, H - 20.5 * mm, tw, 6 * mm, 2, stroke=1 if k == "stats" else 0, fill=1)
        c.setFillColor(colors.HexColor(fg))
        c.setFont("PJS-Bold", 8)
        c.drawString(x + 5, H - 18.2 * mm, lab)
    # grid: weeks of 2, 9, 16, 23 Nov (Mon..Sun)
    days = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]
    gx, gy0 = 14 * mm, H - 32 * mm
    cw = (W - 28 * mm) / 7
    ch = (gy0 - 12 * mm - 7 * mm) / 4
    c.setFont("PJS-Bold", 8)
    for i, dname in enumerate(days):
        c.setFillColor(colors.HexColor("#6B6155"))
        c.drawString(gx + i * cw + 3, gy0 - 5 * mm, dname)
    top = gy0 - 7 * mm
    by_day = {}
    for e in EVENTS:
        by_day.setdefault(e[0], []).append(e)
    for wk in range(4):
        for i in range(7):
            day = 2 + wk * 7 + i
            x0, y1 = gx + i * cw, top - wk * ch
            past = day < 8
            c.setStrokeColor(colors.HexColor("#DDD4C5"))
            c.setFillColor(colors.HexColor("#F7F2EA" if past else "#FFFFFF"))
            c.rect(x0, y1 - ch, cw, ch, stroke=1, fill=1)
            c.setFillColor(colors.HexColor("#CFC4B4" if past else ("#DB6530" if day == 8 else "#14110D")))
            c.setFont("Anton", 15)
            c.drawString(x0 + 3, y1 - 6.5 * mm, str(day))
            if day == 8:
                c.setFont("PJS-Bold", 7)
                c.drawString(x0 + 12 * mm, y1 - 5.2 * mm, "AUJOURD'HUI")
            yy = y1 - 9.5 * mm
            for (_, hm, kind, title, _, _) in by_day.get(day, []):
                lab, bg, fg = KIND[kind]
                c.setFillColor(colors.HexColor(bg))
                c.setStrokeColor(colors.HexColor("#147839"))
                c.roundRect(x0 + 2, yy - 6.4 * mm, cw - 4, 6.0 * mm, 2, stroke=1 if kind == "stats" else 0, fill=1)
                c.setFillColor(colors.HexColor(fg))
                c.setFont("PJS-Bold", 6.3)
                hh = hm.replace(":", "h")
                c.drawString(x0 + 4, yy - 4.3 * mm, hh)
                tx = x0 + 4 + pdfmetrics.stringWidth(hh + " ", "PJS-Bold", 6.3)
                c.setFont("PJS-SemiBold", 6.3)
                t = title
                while pdfmetrics.stringWidth(t, "PJS-SemiBold", 6.3) > x0 + cw - 4 - tx and len(t) > 4:
                    t = t[:-2]
                if t != title:
                    t = t.rstrip() + "…"
                c.drawString(tx, yy - 4.3 * mm, t)
                yy -= 6.9 * mm
    c.setFont("PJS-Medium", 7.5)
    c.setFillColor(colors.HexColor("#6B6155"))
    c.drawString(14 * mm, 8 * mm, "Mis à jour le 8 nov. Jaune = pas encore produit. Le Reel du 18 n'est publié que si l'enregistrement d'écran est reçu le 15 et le Reel validé. "
                                  "Importez Eazy88_Calendrier_Nov2026.ics dans votre app Calendrier pour avoir les rappels.")
    c.showPage()
    c.save()


# ---------------------------------------------------------------- Markdown
def write_md(path):
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    L = ["# Calendrier de publication Eazy88 · novembre 2026", "",
         "Heure d'Adélaïde (ACDT, UTC+10:30). Heure suggérée à tester : 18 h 30 (pas encore de données d'audience).", "",
         "| Date | Heure | Type | Action | Détails |", "|---|---|---|---|---|"]
    for (day, hm, kind, title, _, desc) in EVENTS:
        d = when(day, hm)
        L.append(f"| {jours[d.weekday()]} {day} nov. | {hm.replace(':', ' h ')} | {KIND[kind][0]} | {title} | {desc.replace(chr(10), ' · ')} |")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


os.makedirs(OUT, exist_ok=True)
write_ics(os.path.join(OUT, "Eazy88_Calendrier_Nov2026.ics"))
write_pdf(os.path.join(OUT, "Eazy88_Calendrier_Nov2026.pdf"))
write_md(os.path.join(OUT, "Eazy88_Calendrier_Nov2026.md"))
print("ok", len(EVENTS), "events")
