# Eazy88 TikTok — NeverHadAProblemPOV (version A) · série « van »

Produit le 23 nov. 2026. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-23_never-had-a-problem-pov.md`. Pourquoi une série avec le van : `analytics/2026-11-23_van-vs-autres.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_NeverHadAProblemPOV_A.mp4` | 1080×1920, 30 fps, 8,8 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_NeverHadAProblemPOV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_NeverHadAProblemPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-23_NeverHadAProblemPOV/render_neverhadaproblem_pov.py` (outils communs : `templates/tools/pov_kit.py`, `templates/tools/van_kit.py`).

## Concept
- **Personnage récurrent :** le van orange des vidéos parking et « just down the road » (les deux meilleures du compte).
- **1re image :** « POV: THE BACKPACKER WHO SOLD YOU THE VAN SAID 'NEVER HAD A PROBLEM.' » + le van, visible tout de suite.
- **Idée unique :** Le van perd un enjoliveur, pétarade, traîne son pare-chocs, perd sa porte, fume… et sa roue finit par le doubler.
- **Chute :** « DAY 1 OF THE ROAD TRIP: 'NEVER HAD A PROBLEM.' »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE BUYING A VAN ». Signature (pas un CTA) : « Eazy88 · free app to track your 88 days ».
- **Sans l'app.** Étiquette à l'écran : « Illustration ».

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0 s | Van en gros plan qui roule | Groove guitare / ukulélé |
| 0,45 s | L'enjoliveur saute et roule derrière | « Ting » |
| 1,1 s | Pétarade, fumée | « Bang » |
| 1,75 s | Le pare-chocs arrière traîne avec des étincelles, puis reste sur la route | « Clang », raclement |
| 2,45 s | La porte latérale tombe | « Clonk » |
| 3,15 s | Vapeur sous le capot | Sifflement |
| 3,85 s | La roue arrière se détache et double le van ; il s'affaisse et s'arrête | « Boing », raclement |
| 4,7 s | Zoom arrière, chute à 5,2 s | Trombone triste |
| 6,4 s / 7,0 s | CTA / signature Eazy88 |  |

## Affirmations
Aucune dans la vidéo. Légende : « faire inspecter par un mécanicien indépendant avant de payer » (conseil déjà utilisé dans la vidéo Car checks du 9 nov.). Signature : app gratuite qui suit les 88 jours (vérifié, `product/product-facts.md`).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 8.8 s ✅
- Planche de 18 images : `drafts/2026-11-23_NeverHadAProblemPOV/qc_contact_sheet.png` ; première image vérifiée en grand (titre lisible, van visible) ✅
- Titre ≤ y 588 ; chute ≤ y 520 ; CTA ≤ y 738 ; signature y 1296–1360 (zone sûre 1380) ✅
- Son : -16.1 LUFS, pic -4.6 dBFS, 7.4 % de l'énergie sous 150 Hz, dernière demi-seconde à -29.5 dBFS ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.**
- Entièrement produite par IA : laisser le label « AI-generated content » activé.
