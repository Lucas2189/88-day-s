# Eazy88 TikTok — HostelFridgePOV (version A)

Produit le 19 nov. 2026. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-19_hostel-fridge-pov.md`. Pourquoi ce format : `analytics/2026-11-19_analyse-POV-parking.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_HostelFridgePOV_A.mp4` | 1080×1920, 30 fps, 12,4 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_HostelFridgePOV_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_HostelFridgePOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-19_HostelFridgePOV/render_fridge_pov.py` (notes, positions et minutage en tête de fichier).

## Concept
- **Pour qui :** backpackers qui vivent en auberge de jeunesse ou en colocation.
- **1re image :** « POV: YOU CHECK THE HOSTEL FRIDGE AFTER ONE WEEK. » + la porte du frigo avec l'affiche « PLEASE LABEL YOUR FOOD ».
- **Idée unique :** les petits mots s'empilent, de plus en plus désespérés ; au zoom arrière, le frigo en est couvert.
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO 'BORROWS' YOUR FOOD ».
- **Sans l'app.**

## Déroulé
| Temps | Texte des notes | Son |
|---|---|---|
| 0–1 s | Affiche « PLEASE LABEL YOUR FOOD — Management » | Pizzicato « en douce » |
| 1,1–4,5 s | WHO TOOK MY MILK?? · LABELLED. NOT FREE. · MY HUMMUS HAD MY NAME ON IT · I COUNTED THE EGGS. · IT WAS ROOM 6. · ROOM 6 HERE. IT WASN'T US. | Une claque de papier et une note qui monte à chaque mot |
| 5,3–6,9 s | WHO TOOK THE PEN? · IT'S A FRIDGE, NOT A BUFFET · PLEASE. I'M BEGGING. | Accords d'orchestre de plus en plus forts |
| 7,75 s | Zoom arrière : frigo couvert (+ MINE!! · NOT YOURS · WHY · ROOM 6??) | Roulement, « dun, dun, DUNNN » |
| 8,3 s | « AND STILL NOBODY KNOWS WHO TOOK THE MILK. » | |
| 10,2 s → fin | CTA | Le pizzicato revient |

## Affirmations
Aucune (situation humoristique). « Room 6 » est une chambre fictive.

## Contrôles effectués (sur le MP4 final)
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 12,4 s ✅
- Planche de 18 images : `drafts/2026-11-19_HostelFridgePOV/qc_contact_sheet.png` + images en taille réelle à 6,9 s et 10,5 s ✅
- Corrigé pendant le contrôle : le frigo « plongeait » au début du zoom ; deux notes ajoutées étaient cachées ; trois notes du haut se chevauchaient.
- Texte des notes : 45 à 70 px de haut à l'écran pendant le gros plan ✅
- Son : −15,5 LUFS, pic −2,3 dBFS (corrigé : −0,3 au premier rendu), 4,5 % de l'énergie sous 150 Hz (corrigé : 34 % au premier rendu) ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.**
- Entièrement produite par IA : laisser le label « AI-generated content » activé.
