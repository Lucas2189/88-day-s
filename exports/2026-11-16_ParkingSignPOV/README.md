# Eazy88 TikTok — ParkingSignPOV (version A)

Produit le 16 nov. 2026. **Statut : export final, non publié, date de publication à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-16_parking-sign-pov.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_ParkingSignPOV_A.mp4` | 1080×1920, 30 fps, 11,5 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_ParkingSignPOV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_ParkingSignPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Pas de fichier de sous-titres ni de voix : tout le texte est à l'écran.
Source éditable : `drafts/2026-11-16_ParkingSignPOV/render_parking_pov.py` (textes, panneaux, minutage et musique en tête de fichier).

## Ce qui vient de la vidéo de référence, et ce qui n'en vient pas
- **Repris :** le format « POV » et le thème (un panneau de parking australien incompréhensible), qui est une blague courante.
- **Pas repris :** l'image, le texte et le son de ce compte. Ici, tout est original : illustration dessinée par code, texte écrit pour Eazy88 en anglais, musique générée par code.
- **Différence assumée :** la référence est une vraie scène filmée ; celle-ci est une illustration animée, étiquetée « Illustration · not a real sign ».

## Concept
- **Pour qui :** backpackers qui conduisent en Australie (van, voiture, road trip).
- **Problème, visible dès la première image :** « POV: YOU FOUND PARKING IN AUSTRALIA. **NOW READ THE SIGN.** », avec un van garé sous un panneau.
- **Idée unique :** le panneau n'en finit pas.
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO ALWAYS GETS THE FINE ».
- **Sans l'app.** Seuls l'icône et le nom apparaissent dans l'en-tête.

## Déroulé (temps réels)
| Temps | Image | Texte à l'écran | Son |
|---|---|---|---|
| 0,0–1,0 s | Van garé, poteau, premier panneau « 2P » | Titre POV (3 lignes) | Coup de timbale, nappe grave |
| 1,1–3,7 s | Six panneaux réalistes s'empilent, la caméra monte | P10 MINUTE · NO STOPPING · 4P TICKET · LOADING ZONE · PERMIT HOLDERS · 1/2P | Un coup et une note qui monte à chaque panneau |
| 4,5–6,3 s | Trois panneaux « blague », un par un | EXCEPT WHEN IT RAINS · SEE OTHER SIDE · GOOD LUCK | Accords de cuivres de plus en plus forts |
| 7,25–8,0 s | Zoom arrière : la tour entière à côté du petit van | — | Roulement, cymbale, grand accord |
| 7,75 s → fin | Tour à droite, texte à gauche | « BY THE TIME YOU'VE READ IT, **YOUR 2 HOURS ARE UP.** » | Accord qui s'éteint |
| 9,25 s → fin | Icône d'envoi + CTA | « SEND THIS TO THE MATE WHO **ALWAYS GETS THE FINE** » | Trois notes pincées, nappe douce |

## Affirmations
| Affirmation | Où | Source | Statut |
|---|---|---|---|
| Les panneaux de la vidéo | Vidéo | Aucune : illustration humoristique, étiquetée « not a real sign » | Pas une information |
| « 2P means two-hour parking » ; le chiffre avant le P est la durée limite | Légende | Gouvernement du Queensland, qld.gov.au/transport/safety/rules/road/parking (mis à jour le 8 mai 2026, consulté le 16 nov. 2026) | En vigueur |
| Le panneau peut indiquer les jours et heures où la limite s'applique | Légende | idem | En vigueur |
| Les règles varient selon l'État et la commune | Légende | Précaution générale ; signification des flèches non confirmée sur une source officielle, donc non mentionnée | — |

Citations : `references/official-sources/2026-11-16_parking-signs_and_ballot-check_notes.md`.

## Contrôles effectués
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 11,5 s ✅
- 18 images extraites du MP4 final (planche : `drafts/2026-11-16_ParkingSignPOV/qc_contact_sheet.png`) et 3 images en taille réelle (première image, 4,9 s, 11,2 s) : texte lisible, rien de coupé, rien hors de la zone visible (titre ≤ x 930, tour ≤ x 873, sol à y 1330) ✅
- Première image compréhensible sans le son ; elle reste fixe pendant 0,9 s, le temps de lire le titre ✅
- Orthographe de tous les textes à l'écran et de la légende ✅
- Son : −15,5 LUFS (cible −16), pic −4,7 dBFS, aucun écrêtage. Énergie répartie surtout entre 150 Hz et 3 kHz, donc audible sur un haut-parleur de téléphone. Du son de la première à la dernière demi-seconde ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure : personne ne l'a écoutée.** C'est une musique « épique » de synthèse, faite par code. Si elle ne vous plaît pas, coupez le son d'origine dans l'app et ajoutez un son de sa bibliothèque commerciale.
- **Illustration, pas une vraie scène.** L'effet « c'est vrai » de la référence vient de l'image réelle. Si vous filmez un vrai panneau (5 à 10 s, vertical), je peux refaire la vidéo avec votre clip en gardant le texte.
- Durée de 11,5 s : plus courte que les vidéos habituelles, ce qui est normal pour ce format.
- La vidéo est entièrement produite par une IA (illustration, animation, musique) : par transparence, laissez le label « AI-generated content » activé.
- Même thème que la vidéo de l'autre compte : si la ressemblance vous gêne, les autres idées (« servo », jour 1 des 88 jours, frigo de l'hostel) restent possibles avec le même outil.
