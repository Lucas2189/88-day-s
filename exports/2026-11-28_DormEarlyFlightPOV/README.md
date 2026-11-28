# Eazy88 TikTok — DormEarlyFlightPOV (version A) · hors série « van »

Produit le 28 nov. 2026. **Statut : export final, non publié.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-28_dorm-early-flight-pov.md`. Pourquoi : Lucas veut varier l'humour (28 nov.), au-delà du van.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_DormEarlyFlightPOV_A.mp4` | 1080×1920, 30 fps, 8,8 s, H.264 + AAC stéréo, sons et musique originaux, **sans voix off** |
| `Eazy88_TikTok_DormEarlyFlightPOV_Cover.png` | Cover (= première image) |
| `Eazy88_TikTok_DormEarlyFlightPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-28_DormEarlyFlightPOV/render_dorm_pov.py` (outil : `templates/tools/pov_kit.py`).

## Concept
- **1re image :** « POV: SOMEONE IN YOUR 10-BED DORM HAS AN EARLY FLIGHT. » + le dortoir dans le noir (4:58), vous dormez en haut, une silhouette à lampe frontale fouille ses sacs.
- **Idée unique :** Les bruits s'enchaînent et s'écrivent à l'écran (« rustle… », « RUSTLE RUSTLE », « ZZZIIIP », « CLUNK! », « BEEP BEEP BEEP », « CLICK! », « SORRY!! ») : la vidéo se comprend sans le son. Le faisceau finit dans votre figure, puis la lumière de la chambre s'allume à 5:00.
- **Chute :** sa carte d'embarquement monte : « DEPARTS 14:00 » → « THEIR FLIGHT IS AT 2 PM. »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO PACKS AT 5 AM ». Signature : « Eazy88 · free app to track your 88 days ».
- **Sans l'app, sans van.** Étiquette : « Illustration ». La carte d'embarquement est inventée (« GATE 8 », aucune compagnie ni numéro de vol réels).

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0–0,35 s | Dortoir de nuit, « zzz », le faisceau de la lampe balaie la pièce, titre | Ronflement léger, pizzicato sur la pointe des pieds |
| 0,35–1,45 s | « rustle… », « RUSTLE RUSTLE » : les sacs plastique tremblent | Crépitements de plastique |
| 1,45 s | « ZZZIIIP » (4:59) | Fermeture éclair |
| 2,0 s | « CLUNK! » : le casier claque, l'image tremble, vous ouvrez les yeux | Coup sourd |
| 2,5 s | « BEEP BEEP BEEP » (5:00), le faisceau se pose sur votre visage | 3 bips |
| 3,05 s | « CLICK! » : l'ampoule s'allume, la chambre devient claire, vous sursautez | Clic + accord éblouissant |
| 3,6 s | « SORRY!! » | Petite voix qui descend |
| 4,6–5,2 s | La carte d'embarquement monte : DEPARTS 14:00 | Trombone triste |
| 4,9 s / 6,3 s / 6,9 s | Chute / CTA / signature | Ukulélé, carillon final |

## Affirmations
Aucune (situation de dortoir, carte d'embarquement fictive). Signature : app gratuite qui suit les 88 jours (vérifié). À changer après le 1er mars 2027 (passage à 120 jours pour les nouvelles demandes).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 8.8 s ✅
- Planche de 18 images : `drafts/2026-11-28_DormEarlyFlightPOV/qc_contact_sheet.png` ✅ ; 1re image, 2,6 s et 3,9 s revues en taille réelle ✅
- Titre ≤ y 639 ; chute ≤ y 582 ; CTA ≤ y 800 ; signature y 1296–1360 ✅
- Rythme : première action à 0,35 s (le faisceau bouge dès la 1re image), première blague avant 2 s, chute à 4,9 s, CTA à 6,3 s ✅
- Son : -16.1 LUFS, pic -4.1 dBFS, 0.1 % sous 150 Hz, dernière demi-seconde à -29.5 dBFS ✅

## Points non résolus
- **Le son n'a été vérifié que par mesure.** Laisser le label « AI-generated content » activé.
