# Eazy88 TikTok — FreeCampPOV (version A) · série « van »

Produit le 23 nov. 2026. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-23_free-camp-pov.md`. Pourquoi une série avec le van : `analytics/2026-11-23_van-vs-autres.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_FreeCampPOV_A.mp4` | 1080×1920, 30 fps, 9,4 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_FreeCampPOV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_FreeCampPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-23_FreeCampPOV/render_freecamp_pov.py` (outils communs : `templates/tools/pov_kit.py`, `templates/tools/van_kit.py`).

## Concept
- **Personnage récurrent :** le van orange des vidéos parking et « just down the road » (les deux meilleures du compte).
- **1re image :** « POV: IT'S 9 PM AND YOU NEED A FREE SPOT TO SLEEP IN THE VAN. » + le van, visible tout de suite.
- **Idée unique :** Au coucher du soleil, le van passe devant un panneau « non » après l'autre ; le lendemain matin, il est garé au milieu des vaches.
- **Chute :** « NEXT MORNING: YOUR NEW NEIGHBOURS. »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO SLEEPS IN THE VAN ». Signature (pas un CTA) : « Eazy88 · free app to track your 88 days ».
- **Sans l'app.** Étiquette à l'écran : « Illustration · not real signs ».

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0 s | Coucher de soleil, panneau NO CAMPING | Nappe douce, carillon |
| 0,85–3,4 s | NO OVERNIGHT PARKING · NO SLEEPING IN VEHICLES · RESIDENTS ONLY · SERIOUSLY? NOPE. | Souffle + « nope » à deux notes, grillons |
| 4,25 s | NEXT FREE SPOT 410 km (clin d'œil à la vidéo route) |  |
| 5,0 s | Fondu au noir : la nuit passe |  |
| 5,15 s | Lever du soleil, zoom arrière : 7 vaches autour du van | Oiseaux, cloche à vache |
| 5,6 s | Chute |  |
| 6,8 s / 7,4 s | CTA / signature Eazy88 | Ukulélé |

## Affirmations
Aucune règle citée : les panneaux sont une blague, étiquetés « not real signs ». La légende dit seulement de vérifier les règles locales (conseil général). Signature : app gratuite qui suit les 88 jours (vérifié, `product/product-facts.md`).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 9.4 s ✅
- Planche de 18 images : `drafts/2026-11-23_FreeCampPOV/qc_contact_sheet.png` ; première image vérifiée en grand (titre lisible, van visible) ✅
- Titre ≤ y 633 ; chute ≤ y 528 ; CTA ≤ y 746 ; signature y 1296–1360 (zone sûre 1380) ✅
- Son : -16.0 LUFS, pic -5.0 dBFS, 0.0 % de l'énergie sous 150 Hz, dernière demi-seconde à -35.5 dBFS ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.**
- Entièrement produite par IA : laisser le label « AI-generated content » activé.
