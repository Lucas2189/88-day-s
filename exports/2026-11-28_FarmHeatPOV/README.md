# Eazy88 TikTok — FarmHeatPOV (version A) · hors série « van »

Produit le 28 nov. 2026. **Statut : export final, non publié.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-28_farm-heat-pov.md`. Pourquoi : Lucas veut varier l'humour (28 nov.), au-delà du van.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_FarmHeatPOV_A.mp4` | 1080×1920, 30 fps, 8,4 s, H.264 + AAC stéréo, sons et musique originaux, **sans voix off** |
| `Eazy88_TikTok_FarmHeatPOV_Cover.png` | Cover (= première image) |
| `Eazy88_TikTok_FarmHeatPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-28_FarmHeatPOV/render_heat_pov.py` (outil : `templates/tools/pov_kit.py`).

## Concept
- **1re image :** « POV: DAY 1 OF FARM WORK IN THE AUSSIE SUMMER. » + vous, souriant, dans les rangs au lever du soleil, seau de fraises et gourde pleine ; carte « 6:00 AM · 24° ».
- **Idée unique :** L'heure avance à peine, la chaleur explose : 7:00 → 29°, 8:00 → 34°, 8:45 → 39°, 9:15 → 43°, 9:30 → « 47°?! ». Le soleil monte, grossit et blanchit, l'air ondule, les plants jaunissent, la gourde se vide, vous transpirez puis fondez en flaque (il ne reste que la casquette et deux yeux). Le thermomètre éclate : « POP! ».
- **Chute :** « AND IT'S ONLY 9:30 AM. »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WITH ONE WATER BOTTLE ». Signature : « Eazy88 · free app to track your 88 days ».
- **Sans l'app, sans van.** Étiquette : « Illustration · not a weather report » (les températures sont une exagération comique, pas une donnée météo).

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0–0,5 s | Lever du soleil, vous cueillez (le bras bouge), titre | Cigales légères, guitare paresseuse |
| 0,5 / 1,2 / 1,9 / 2,5 / 3,05 s | L'heure et la température montent ; sueur, langue tirée, gourde vide | Clic d'horloge + une note plus haute à chaque palier, cigales de plus en plus fortes |
| 1,9–3,5 s | Vous fondez | Sifflet à coulisse qui descend |
| 3,4 s | « POP! » : le mercure jaillit du thermomètre | Pop + boing |
| 3,95–4,45 s | Le décor descend, le titre s'efface | Les cigales retombent |
| 4,2 s | Chute « AND IT'S ONLY 9:30 AM. » | Deux gouttes |
| 5,6 s / 6,2 s | CTA / signature | Ukulélé, carillon final |

## Affirmations
Aucune. Les températures sont volontairement exagérées et marquées « not a weather report » à l'écran. Pas de conseil de sécurité chiffré ni de statistique sur la chaleur (le CTA sur la gourde reste une blague). Signature : app gratuite qui suit les 88 jours (vérifié). À changer après le 1er mars 2027 (passage à 120 jours pour les nouvelles demandes).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 8.4 s ✅
- Planche de 18 images : `drafts/2026-11-28_FarmHeatPOV/qc_contact_sheet.png` ✅ ; 1re image, 2,2 s et 7,5 s revues en taille réelle (la flaque reste visible au-dessus de la signature) ✅
- Titre ≤ y 648 ; chute ≤ y 582 ; CTA ≤ y 800 ; carte x 540–940 ; signature y 1296–1360 ✅
- Rythme : bras et soleil en mouvement dès la 1re image, 1re action à 0,5 s, 1re blague (sueur + langue tirée) vers 1,2–1,9 s, chute à 4,2 s, CTA à 5,6 s ✅
- Son : -16.3 LUFS, pic -4.5 dBFS, 0.0 % sous 150 Hz, dernière demi-seconde à -26.6 dBFS ✅

## Points non résolus
- **Le son n'a été vérifié que par mesure.** Laisser le label « AI-generated content » activé.
