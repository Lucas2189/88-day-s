# Eazy88 TikTok — FliesPOV (version A) · série « van »

Produit le 25 nov. 2026. **Statut : export final, non publié.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-25_flies-pov.md`. Pourquoi la série : `analytics/2026-11-23_van-vs-autres.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_FliesPOV_A.mp4` | 1080×1920, 30 fps, 8,6 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_FliesPOV_Cover.png` | Cover (= première image) |
| `Eazy88_TikTok_FliesPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-25_FliesPOV/render_flies_pov.py` (outils : `templates/tools/pov_kit.py`, `templates/tools/van_kit.py`).

## Concept
- **1re image :** « POV: YOU OPEN THE VAN DOOR IN THE OUTBACK FOR 2 SECONDS. » + le van orange.
- **Idée unique :** La porte latérale s'ouvre ; un compteur « FLIES » s'emballe (1, 3, 12, 47, 180, 600, « YES. ») et l'essaim envahit le décor.
- **Chute :** « YOU'VE NOW MASTERED THE AUSSIE SALUTE. »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO HATES FLIES ». Signature : « Eazy88 · free app to track your 88 days ».
- **Sans l'app.** Étiquette : « Illustration ».

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0–0,3 s | Van garé en plein soleil, titre | Riff de guitare |
| 0,3 s | La porte s'ouvre | Clic, souffle |
| 0,4–3,75 s | Compteur 1 → 3 → 12 → 47 → 180 → 600 → YES. ; l'essaim grossit | Bourdonnement de plus en plus dense, une note qui monte par palier |
| 4,4 s | Zoom arrière : le van dans un nuage de mouches | Cymbale, accord |
| 4,9 s / 6,2 s / 6,8 s | Chute / CTA / signature | Riff |

## Affirmations
Aucune (le compteur est une blague). Signature : app gratuite qui suit les 88 jours (vérifié). À changer après le 1er mars 2027 (passage à 120 jours pour les nouvelles demandes).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 8.6 s ✅
- Planche de 18 images : `drafts/2026-11-25_FliesPOV/qc_contact_sheet.png` ✅
- Titre ≤ y 633 ; chute ≤ y 532 ; CTA ≤ y 750 ; signature y 1296–1360 ✅
- Son : -16.0 LUFS, pic -5.3 dBFS, 0.0 % sous 150 Hz, dernière demi-seconde à -32.8 dBFS ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.** Laisser le label « AI-generated content » activé.
