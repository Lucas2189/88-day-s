# Eazy88 TikTok — PieceRates (version A)

Produit le 17 nov. 2026, exporté le 19 nov. **Statut : export final, non publié, date à décider.** Coût : 0 crédit (rendu local).
Brief : `briefs/2026-11-17_piece-rates.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_PieceRates_A.mp4` | 1080×1920, 30 fps, 36,0 s, H.264 + AAC stéréo, voix IA + musique originale, sous-titres incrustés |
| `Eazy88_TikTok_PieceRates.srt` | 12 sous-titres, identiques à la voix |
| `Eazy88_TikTok_PieceRates_Voiceover.wav` | Voix seule |
| `Eazy88_TikTok_PieceRates_Cover.png` | Cover 1080×1920 (= 1re image) |
| `Eazy88_TikTok_PieceRates_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-17_PieceRates/spec.json` + `vo_lines.json` (rendu avec `templates/tools/render_reel.py`, voix à vitesse 1,0 pour rester sous 40 s).

## Concept
- **Pour qui :** backpackers qui cueillent des fruits payés à la pièce (au seau, au bac, au kilo) cet été.
- **Problème, 1re image :** « PAID PER BUCKET? YOU STILL GET A MINIMUM ».
- **Réponse :** un minimum par jour travaillé · on touche le montant le plus élevé · un relevé écrit avant de commencer.
- **Objectif :** partages. **CTA unique :** « Send this to the mate you're picking with. »
- **Sans l'app.**

## Script (voix = sous-titres, 107 mots)
> Picking fruit on piece rates this summer? You're still guaranteed a minimum. One. Under the Horticulture Award, pieceworkers get a daily minimum: at least the hourly rate for your level, times the hours you worked. For an adult level one casual, that's thirty-two dollars eighteen an hour. Two. Pick fast and your piece rate pays more? You get the higher amount. And a good day can't be used to cover a slow one. Three. Before you start, your employer must give you a written piecework record, with the task and the piece rate. These rules apply whatever your visa. Send this to the mate you're picking with.

## Affirmations
| Affirmation | Source | Statut |
|---|---|---|
| Les travailleurs à la pièce ont un minimum garanti pour chaque jour travaillé : au moins le taux horaire de leur niveau × les heures du jour | Fair Work Ombudsman, horticulture.fairwork.gov.au (« Pay and piece rates », « How to use piece rates ») | En vigueur depuis le 28 avril 2022 |
| Casual niveau 1, adulte (20 ans et +) : 32,18 $/h ; 19 ans : 28,96 $ ; 18 ans : 25,74 $ | Pay guide Horticulture Award MA000028, publié le 24 juin 2026 (copie : `references/official-sources/2026-11-17_fairwork_horticulture-award-MA000028_pay-guide.pdf`) | En vigueur depuis la 1re période de paie complète à partir du 1er juillet 2026 |
| Le taux casual inclut la majoration de 25 % (non dit dans la vidéo) | FWO | En vigueur |
| Si la paie à la pièce du jour est plus élevée, on touche ce montant | FWO | En vigueur |
| Un bon jour ne peut pas compenser un jour faible | FWO | En vigueur |
| L'employeur remet un relevé écrit (piecework record) avant le début du travail, avec la tâche et le taux à la pièce | FWO | En vigueur |
| Mêmes droits quel que soit le visa | FWO, « Visa holders and migrants » | En vigueur |

Limite d'application, à l'écran et dans la légende : « For employees under the Horticulture Award. General information, not legal advice. »
Citations et limites d'accès : `references/official-sources/2026-11-17_piece-rates_and_rental-scams_notes.md`.

## Contrôles effectués (sur le MP4 final)
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 35,97 s ✅
- Planche de 14 images (`drafts/2026-11-17_PieceRates/qc_contact_sheet.png`) : hook lisible dès la 1re image, chaque section et le CTA corrects, contenu au-dessus des sous-titres (bas du contenu à y = 1142, limite 1190) ✅
- Sous-titres : 12, texte identique à la voix, 4,5 s maximum à l'écran ✅
- Son : −16,1 LUFS (cible −16), pic −4,4 dBFS ; voix 19,4 dB au-dessus de la musique ; enveloppe du MP4 corrélée à 0,97 avec la voix (la voix est bien dans le fichier) ✅
- Orthographe de tous les textes ✅

## Points non résolus
- **Le son n'a été vérifié que par mesure** : personne ne l'a écouté.
- fairwork.gov.au bloque la lecture directe depuis cet environnement : les règles viennent d'extraits concordants de pages officielles renvoyés par la recherche ; les taux viennent du PDF officiel, lu en entier.
- Les taux changent en général chaque 1er juillet : vidéo valable jusqu'à fin juin 2027.
- Voix entièrement générée par IA : laisser le label « AI-generated content » activé.
