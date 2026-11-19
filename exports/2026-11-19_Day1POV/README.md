# Eazy88 TikTok — Day1POV (version A, v2)

Produit le 19 nov. 2026, **resserré le même jour d'après les données TikTok** (`analytics/2026-11-19_windsor-tiktok-analyse.md`). **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local). La première version (9,8 s) reste dans l'historique Git (commit 31ca2de).
Brief : `briefs/2026-11-19_day1-pov.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_Day1POV_A.mp4` | 1080×1920, 30 fps, **8,2 s**, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_Day1POV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_Day1POV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-19_Day1POV/render_day1_pov.py` (outils communs : `templates/tools/pov_kit.py`).

## Concept
- **Pour qui :** backpackers qui font leurs 88 jours.
- **1re image :** « POV: YOU JUST FINISHED DAY 1 OF YOUR 88 DAYS. » + un tableau papier « MY 88 DAYS » en gros plan, avec un feutre au-dessus de la case 1. La caméra avance déjà.
- **Idée unique :** la fête pour le jour 1, puis le zoom arrière sur les 87 cases vides.
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE DOING THEIR 88 DAYS ».
- **Signature (pas un CTA) :** « Eazy88 · free app to track your 88 days », à partir de 5,6 s.
- Pas d'écran d'app : c'est un tableau en papier dessiné, étiqueté « Illustration ».

## Déroulé
| Temps | Image / texte | Son |
|---|---|---|
| 0–0,35 s | Gros plan, léger zoom avant, feutre qui bouge | Carillon, roulement de caisse claire |
| 0,35–0,7 s | Le feutre coche la case 1 | Crissement du feutre |
| 0,7–2,0 s | Confettis | « Ta-da ! », fanfare |
| 2,0–3,3 s | Disque rayé, zoom arrière : 88 cases, une seule cochée | Trombone triste |
| 3,4 s | « ONLY 87 TO GO. » | Ukulélé |
| 3,95 s | « YOU ARE HERE » + flèche et cercle sur la case 1 | |
| 5,0 s | CTA | |
| 5,6 s → fin | Signature Eazy88 | |

## Affirmations
Aucune affirmation de visa. Signature : app gratuite (vérifié, App Store) qui suit les 88 jours (vérifié, `product/product-facts.md`).

## Contrôles (MP4 final v2)
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 8,2 s ✅
- Planche de 18 images : `drafts/2026-11-19_Day1POV/qc_contact_sheet.png` + dernière image en taille réelle ✅
- Zones : tableau x 357–723, y 300–849 ; chute ≤ y 1039 ; CTA ≤ y 1270 ; signature y 1296–1360 (zone sûre 1380) ✅
- Son : −16,0 LUFS, pic −5,4 dBFS, 4,9 % de l'énergie sous 150 Hz, du son jusqu'à la fin ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.**
- Entièrement produite par IA : laisser le label « AI-generated content » activé.
