# Eazy88 TikTok — RoofStackPOV (version A) · série « van »

Produit le 23 nov. 2026. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-23_roof-stack-pov.md`. Pourquoi une série avec le van : `analytics/2026-11-23_van-vs-autres.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_RoofStackPOV_A.mp4` | 1080×1920, 30 fps, 9,2 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_RoofStackPOV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_RoofStackPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-23_RoofStackPOV/render_roofstack_pov.py` (outils communs : `templates/tools/pov_kit.py`, `templates/tools/van_kit.py`).

## Concept
- **Personnage récurrent :** le van orange des vidéos parking et « just down the road » (les deux meilleures du compte).
- **1re image :** « POV: 4 BACKPACKERS PACK ONE VAN FOR A ROAD TRIP. » + le van, visible tout de suite.
- **Idée unique :** Les affaires s'empilent sur le toit (glacière, matelas, surf, vélo, chaises, guitare, kayak… puis l'évier de cuisine et un kangourou) ; le van repart en tanguant.
- **Chute :** « AND SOMEONE STILL FORGOT THE TENT. »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO ALWAYS OVERPACKS ». Signature (pas un CTA) : « Eazy88 · free app to track your 88 days ».
- **Sans l'app.** Étiquette à l'écran : « Illustration ».

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0–0,35 s | Van garé, titre | Petit carillon, ukulélé |
| 0,35–3 s | 7 objets tombent sur le toit, un toutes les ~0,45 s | Un « toc » et une note qui monte par objet |
| 3,45 s | L'évier de cuisine | « Clang » métallique |
| 4,05 s | Un kangourou s'assoit en haut | « Boing » |
| 4,65 s | Zoom arrière : la tour entière sur le van | Roulement, cymbale, accord |
| 5,2 s | Chute (encadré sombre à gauche) |  |
| 6,0 s | Le van repart doucement, la tour tangue | Ukulélé |
| 6,6 s / 7,2 s | CTA / signature Eazy88 |  |

## Affirmations
Aucune (objets dessinés, situation inventée). Signature : app gratuite qui suit les 88 jours (vérifié, `product/product-facts.md`).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 9.2 s ✅
- Planche de 18 images : `drafts/2026-11-23_RoofStackPOV/qc_contact_sheet.png` ; première image vérifiée en grand (titre lisible, van visible) ✅
- Titre ≤ y 648 ; chute ≤ y 713 ; CTA ≤ y 1013 ; signature y 1296–1360 (zone sûre 1380) ✅
- Son : -16.2 LUFS, pic -4.4 dBFS, 0.1 % de l'énergie sous 150 Hz, dernière demi-seconde à -38.9 dBFS ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.**
- Entièrement produite par IA : laisser le label « AI-generated content » activé.
