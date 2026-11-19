# Eazy88 TikTok — Day1POV (version A)

Produit le 19 nov. 2026. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-19_day1-pov.md`. Pourquoi ce format : `analytics/2026-11-19_analyse-POV-parking.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_Day1POV_A.mp4` | 1080×1920, 30 fps, 9,8 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_Day1POV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_Day1POV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-19_Day1POV/render_day1_pov.py` (textes et minutage en tête de fichier ; outils communs : `templates/tools/pov_kit.py`).

## Concept
- **Pour qui :** backpackers qui font leurs 88 jours.
- **1re image :** « POV: YOU JUST FINISHED DAY 1 OF YOUR 88 DAYS. » + un tableau papier « MY 88 DAYS » en gros plan, un feutre prêt à cocher la case 1.
- **Idée unique :** la fête pour le jour 1, puis le zoom arrière sur les 87 cases vides.
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE DOING THEIR 88 DAYS ».
- **Sans l'app.** C'est un tableau en papier dessiné, étiqueté « Illustration » : pas un écran d'application.

## Déroulé
| Temps | Image | Texte | Son |
|---|---|---|---|
| 0–0,95 s | Gros plan : titre du tableau, cases 1 à 6, feutre au-dessus de la case 1 | Titre POV | Petit carillon, nappe douce, roulement qui monte |
| 0,95–1,3 s | Le feutre coche la case 1 | — | Crissement du feutre |
| 1,3–2,95 s | Confettis, petit rebond de caméra | — | « Ta-da ! » cuivres, cymbale, fanfare |
| 2,95–4,5 s | Disque rayé, zoom arrière : les 88 cases, une seule cochée | — | Trombone triste (« wah wah wah waaah ») |
| 4,55 s | Tableau entier | « ONLY 87 TO GO. » | Ukulélé résigné |
| 5,25 s | Flèche et cercle sur la case 1 | « YOU ARE HERE » | |
| 6,6 s → fin | | CTA | Ukulélé |

## Affirmations
Aucune affirmation factuelle (pas de règle de visa, pas de chiffre). « 88 days » est le nom courant de l'objectif des backpackers ; la vidéo ne dit pas ce qui compte comme jour de travail.

## Contrôles effectués (sur le MP4 final)
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 9,8 s ✅
- Planche de 18 images : `drafts/2026-11-19_Day1POV/qc_contact_sheet.png`, et images en taille réelle à 0,03 s, 1,15 s, 1,7 s, 2 s, 7,5 s ✅
- Corrigé pendant le contrôle : le titre du tableau masquait la case 1 ; le feutre masquait une lettre du titre.
- Zones : titre ≤ y 627 ; tableau x 335–745, y 310–926 ; chute ≤ y 1129 ; CTA ≤ y 1362 (zone sûre 1380) ✅
- Son : −15,4 LUFS, pic −5,1 dBFS, 9 % de l'énergie sous 150 Hz (audible sur un téléphone), du son de la première à la dernière demi-seconde ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure** : personne ne l'a écoutée.
- Entièrement produite par IA (illustration, animation, musique) : laisser le label « AI-generated content » activé.
