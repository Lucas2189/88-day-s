# Eazy88 TikTok — AussieSlangPOV (version A) · hors série « van »

Produit le 28 nov. 2026. **Statut : export final, non publié.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-28_aussie-slang-pov.md`. Pourquoi : Lucas veut varier l'humour (28 nov.), au-delà du van.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_AussieSlangPOV_A.mp4` | 1080×1920, 30 fps, 8,6 s, H.264 + AAC stéréo, sons et musique originaux, **sans voix off** |
| `Eazy88_TikTok_AussieSlangPOV_Cover.png` | Cover (= première image) |
| `Eazy88_TikTok_AussieSlangPOV_Caption.txt` | Légende (anglais, avec mini-glossaire) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-28_AussieSlangPOV/render_slang_pov.py` (outil : `templates/tools/pov_kit.py`).

## Concept
- **1re image :** « POV: YOUR AUSSIE BOSS EXPLAINS THE JOB ON DAY 1. » + une ferme en plein soleil : le patron (chapeau à large bord, moustache, gilet haute visibilité) montre le ute du doigt ; vous, sac à dos et casquette.
- **Idée unique :** Cinq bulles d'argot qui s'empilent de plus en plus vite (« G'DAY! GRAB THE ESKY FROM THE UTE. », « THEN CHUCK A U-EY AT THE SERVO. », « SMOKO'S AT 10. », « BRING YOUR SUNNIES THIS ARVO. », « RECKON YOU'LL BE RIGHT? »), mots d'argot en orange. Un « ? » de plus au-dessus de votre tête à chaque bulle, vos yeux s'agrandissent. Silence gêné (grillons).
- **Chute :** « YOU: “YEAH… NAH… YEAH?” », pouce levé. Le patron répond « GOOD ON YA! ».
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO NODS ANYWAY ». Signature : « Eazy88 · free app to track your 88 days ».
- **Sans l'app, sans van.** Étiquette : « Illustration ». La voix du patron est un « wah-wah » de trombone : aucune voix humaine ni IA, tout le texte est à l'écran.
- **Valeur ajoutée :** la légende traduit les 8 mots (de quoi enregistrer le post).

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0–0,3 s | Ferme, titre, le patron parle déjà (bouche, bras) | Petit groove de cordes pincées |
| 0,3 / 1,25 / 2,1 / 2,6 / 3,25 s | 5 bulles ; les anciennes montent et pâlissent ; un « ? » apparaît 0,3 s après chaque bulle | « Wah-wah » de plus en plus rapide, « bloop » à chaque « ? » |
| 3,55–4,1 s | Silence, vos yeux écarquillés | La musique s'arrête, deux grillons |
| 4,1–4,6 s | Le décor descend, le titre s'efface | — |
| 4,35 s | Chute « YOU: “YEAH… NAH… YEAH?” », vous levez le pouce | 3 notes : monte, descend, monte (question) |
| 5,25 s | « GOOD ON YA! », le patron lève le pouce | Clochettes |
| 6,1 s / 6,7 s | CTA / signature | Ukulélé, carillon final |

## Affirmations
Aucune affirmation chiffrée. Glossaire (usage courant de l'anglais australien) : esky = glacière, ute = pick-up, chuck a U-ey = faire demi-tour, servo = station-service, smoko = pause, sunnies = lunettes de soleil, arvo = après-midi, reckon = penser. « Yeah, nah » = non ; « good on ya » = bravo. Signature : app gratuite qui suit les 88 jours (vérifié). À changer après le 1er mars 2027 (passage à 120 jours pour les nouvelles demandes).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 8.6 s ✅
- Planche de 18 images : `drafts/2026-11-28_AussieSlangPOV/qc_contact_sheet.png` ✅ ; 1re image et 3,85 s revues en taille réelle ✅
- Titre ≤ y 633 ; chute ≤ y 532 ; CTA ≤ y 750 ; bulles en 54 px, entre x 90 et 940 ; signature y 1296–1360 ✅
- Rythme : le patron bouge dès la 1re image, 1re bulle à 0,3 s, 1re blague (« CHUCK A U-EY AT THE SERVO » + « ?? ») vers 1,3–1,6 s, chute à 4,35 s, CTA à 6,1 s ✅
- Son : -16.0 LUFS, pic -7.0 dBFS, 0.0 % sous 150 Hz, dernière demi-seconde à -30.1 dBFS ✅. Le filtre de normalisation de ffmpeg mesurait cette piste 1,2 LU plus bas que notre mesure de contrôle (sortie à -14.8) : le script réajuste la musique sur -16 et la remonte avec la vidéo.

## Points non résolus
- **Le son n'a été vérifié que par mesure.** Laisser le label « AI-generated content » activé.
- Les transitions entre bulles se chevauchent pendant environ 0,1 s (mouvement), jamais à l'arrêt.
