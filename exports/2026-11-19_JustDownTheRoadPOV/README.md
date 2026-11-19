# Eazy88 TikTok — JustDownTheRoadPOV (version A)

Produit le 19 nov. 2026. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-19_just-down-the-road-pov.md`. Pourquoi ce format : `analytics/2026-11-19_analyse-POV-parking.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_JustDownTheRoadPOV_A.mp4` | 1080×1920, 30 fps, 13,0 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_JustDownTheRoadPOV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_JustDownTheRoadPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-19_JustDownTheRoadPOV/render_road_pov.py` (panneaux, couleurs du ciel et minutage en tête de fichier).

## Concept
- **Pour qui :** backpackers en road trip (même public que la vidéo du parking, qui a le mieux marché).
- **1re image :** « POV: AN AUSSIE SAYS THE NEXT TOWN IS 'JUST DOWN THE ROAD.' » + le van (le même que dans la vidéo du parking) arrêté près d'un panneau « NEXT TOWN 80 km ».
- **Idée unique :** les distances augmentent au lieu de baisser ; le jour tombe, la nuit passe, le jour se lève.
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO SAYS IT'S 'NOT FAR' ».
- **Sans l'app.** Étiquette à l'écran : « Illustration · not a real road ».

## Déroulé
| Temps | Panneau / texte | Ciel | Son |
|---|---|---|---|
| 0 s | NEXT TOWN 80 km | Jour | Groove guitare / ukulélé |
| 1,6 · 2,7 · 3,8 s | NEXT TOWN 160 km · ROOS NEXT 200 km · NEXT FUEL 320 km | Jour | Un souffle et un carillon par panneau |
| 4,9 s | NEXT TOWN 410 km | Coucher de soleil | |
| 6,0 · 7,1 s | STILL NOT THERE · ARE WE THERE YET? NO. | Nuit, étoiles, phares | Batterie coupée, grillons |
| 8,2 s | NEXT TOWN 'JUST DOWN THE ROAD' | Lever du jour | Le groove revient |
| 9,0 s | Zoom arrière : minuscule van sur une route sans fin | Matin | Accord tenu |
| 9,55 s | « 6 HOURS LATER: 'NOT FAR, MATE.' » | | |
| 11,0 s → fin | CTA | | |

## Affirmations
Aucune. Les distances, le « 6 hours » et les panneaux sont une blague, sans lieu réel (étiquette « not a real road »).

## Contrôles effectués (sur le MP4 final)
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 13,0 s ✅
- Planche de 18 images : `drafts/2026-11-19_JustDownTheRoadPOV/qc_contact_sheet.png` + images en taille réelle à 2,7 s et 6,4 s ✅
- Corrigé pendant le contrôle : soleil, lune et étoiles s'affichaient en noir ; plaque « NEXT 200 km » trop étroite ; poteaux des panneaux devant le van.
- Zones : titre ≤ y 633 ; chute ≤ y 564 ; CTA ≤ y 782, au-dessus du décor (y ≥ 812) ; panneaux lus entre x 510 et 890 ✅
- Son : −16,1 LUFS, pic −6,4 dBFS, 4,8 % de l'énergie sous 150 Hz ✅ ; dernière demi-seconde en fondu (−39 dBFS).

## Points non résolus
- **La musique n'a été vérifiée que par mesure.**
- Entièrement produite par IA : laisser le label « AI-generated content » activé.
