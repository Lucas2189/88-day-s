# Eazy88 TikTok — BeachSinkPOV (version A) · série « van »

Produit le 25 nov. 2026. **Statut : export final, non publié.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-25_beach-sink-pov.md`. Pourquoi la série : `analytics/2026-11-23_van-vs-autres.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_BeachSinkPOV_A.mp4` | 1080×1920, 30 fps, 8,6 s, H.264 + AAC stéréo, musique originale, **sans voix off** |
| `Eazy88_TikTok_BeachSinkPOV_Cover.png` | Cover (= première image) |
| `Eazy88_TikTok_BeachSinkPOV_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-25_BeachSinkPOV/render_beach_pov.py` (outils : `templates/tools/pov_kit.py`, `templates/tools/van_kit.py`).

## Concept
- **1re image :** « POV: YOU DROVE YOUR 2WD VAN ONTO THE BEACH FOR THE SUNSET. » + le van orange.
- **Idée unique :** Le van passe devant un panneau « 4WD ONLY », patine et s'enfonce dans le sable jusqu'à la planche de surf ; une mouette s'y pose.
- **Chute :** « THE SIGN DID SAY '4WD ONLY'. »
- **Objectif :** partages. **CTA unique :** « SEND THIS TO THE MATE WHO NEVER READS SIGNS ». Signature : « Eazy88 · free app to track your 88 days ».
- **Sans l'app.** Étiquette : « Illustration · not a real beach ».

## Déroulé
| Temps | Image | Son |
|---|---|---|
| 0 s | Coucher de soleil, panneau BEACH ACCESS · 4WD ONLY, le van roule sur le sable | Guitare insouciante |
| 0,9–3,6 s | Les roues patinent, le sable vole, le van s'enfonce par étapes | Moteur qui monte, « glouglou » qui descend |
| 3,7 s | Une mouette se pose sur la planche de surf | Cri de mouette |
| 4,3 s | Zoom arrière : le panneau et la planche qui dépasse du sable | Trombone triste |
| 4,8 s / 6,0 s / 6,6 s | Chute / CTA / signature | Guitare |

## Affirmations
Aucune règle citée : panneau humoristique, étiqueté « not a real beach ». Légende : lire le panneau avant de rouler sur le sable (conseil général). Signature : app gratuite qui suit les 88 jours (vérifié). À changer après le 1er mars 2027 (passage à 120 jours pour les nouvelles demandes).

## Contrôles (MP4 final)
- ffprobe : h264 1080x1920 30/1, aac 48000 Hz 2 ch, 8.6 s ✅
- Planche de 18 images : `drafts/2026-11-25_BeachSinkPOV/qc_contact_sheet.png` ✅
- Titre ≤ y 594 ; chute ≤ y 564 ; CTA ≤ y 782 ; signature y 1296–1360 ✅
- Son : -15.0 LUFS, pic -5.1 dBFS, 0.0 % sous 150 Hz, dernière demi-seconde à -29.4 dBFS ✅

## Points non résolus
- **La musique n'a été vérifiée que par mesure.** Laisser le label « AI-generated content » activé.
