# Eazy88 TikTok — VisaBallot (version A)

Produit le 7 nov. 2026. Brief : `briefs/2026-11-07_visa-ballot-whats-confirmed.md`. **Non publié** : la publication revient à Lucas.

## Fichiers
| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_VisaBallot_A.mp4` | Vidéo 1080×1920, 30 fps, 34,0 s, H.264 + AAC stéréo, voix + musique originale |
| `Eazy88_TikTok_VisaBallot.srt` | Sous-titres (12 repères), identiques à la voix |
| `Eazy88_TikTok_VisaBallot_Voiceover.wav` | Voix seule, −16 LUFS |
| `Eazy88_TikTok_VisaBallot_Cover.png` | Cover 1080×1920 (= première image) |
| `Eazy88_TikTok_VisaBallot_Caption.txt` | Légende anglaise prête à coller + hashtags |

Sources éditables : `drafts/2026-11-07_VisaBallot/` (`spec.json`, `vo_lines.json`, clips audio) et `templates/tools/`.

## Concept
- **Pour qui :** titulaires d'un visa 417 ou 462 qui font leurs 88 jours et ont entendu parler du ballot.
- **Idée unique :** le ballot est annoncé, pas encore en vigueur. Voici ce qui est confirmé.
- **Objectif :** partages. **CTA :** "Send this to a mate doing their 88 days."
- **Sans l'app.** Seuls l'icône officielle et le nom apparaissent.

## Script final (voix off, anglais)
> Doing your 88 days and worried about the new visa ballot? Here's what's actually confirmed.
> One. It's announced, not in force. Reports say it should start by the end of 2026, but Home Affairs hasn't listed it on its Working Holiday news page yet.
> Two. Specified work is still required today. 88 days for a second visa, 179 days for a third.
> Three. UK passport holders already have different rules, so check what applies to your passport.
> Send this to a mate doing their 88 days.

## Tableau des affirmations
| Affirmation | Source | À qui | Statut |
|---|---|---|---|
| Ballot annoncé pour la 2e / 3e année | Time Out, 24 sept. 2026 (annonce de Tony Burke) | 417 / 462 visant une 2e ou 3e année | Annoncé |
| Démarrage annoncé « by the end of 2026 » | Time Out, 24 sept. 2026, citant Home Affairs | idem | Annoncé |
| Pas encore sur la page WHM latest news de Home Affairs | Lu directement le 7 nov. 2026 | — | Constat daté |
| 88 jours calendaires (2e visa), 179 (3e visa), week-ends et jours de repos inclus | Pages specified work 417 **et** 462, lues le 7 nov. 2026 | 417 / 462 | En vigueur |
| Passeport UK : pas de specified work pour un 2e visa (demande depuis le 1er juil. 2024) | Page Second Working Holiday 417, lue le 7 nov. 2026 | Passeports UK | En vigueur |
| Plafonds de 45 000 / 5 000 (légende uniquement) | Time Out, 24 sept. 2026 | 417 / 462 | Annoncé |

Copies des citations officielles : `references/official-sources/2026-11-07_home-affairs_specified-work-417_notes.md`.

## Storyboard (temps réels)
| Temps | Narration | Visuel / texte à l'écran |
|---|---|---|
| 0,00–5,8 s | Hook (b01–b02) | « 2ND-YEAR VISA BALLOT: WHAT'S ACTUALLY **CONFIRMED** », pastille 417 / 462, « Checked 7 Nov 2026 ». Visible dès la 1re image. |
| 5,8–15,9 s | Point 1 (b03–b06) | « 1 ANNOUNCED, **NOT IN FORCE** », pastille orange ANNOUNCED, 2 puces qui apparaissent avec la voix, sources |
| 15,9–23,9 s | Point 2 (b07–b09) | « 2 SPECIFIED WORK **STILL REQUIRED** », pastille verte IN FORCE TODAY, cartes **88** puis **179** au mot prononcé |
| 23,9–29,9 s | Point 3 (b10–b11) | « 3 UK PASSPORTS: **DIFFERENT RULES** », règle UK, « Check what applies to your passport » |
| 29,9–34,0 s | CTA (b12) | Flèche d'envoi, « SEND THIS TO A MATE DOING THEIR **88 DAYS** », icône + Eazy88, « General information, not migration advice » |

## Contrôle qualité effectué
- ffprobe : h264 + aac 48 kHz, 1080×1920, 30/1, 34,0 s ✅
- Planche d'images du MP4 final (hook à 0,03 s, chaque repère, fin) : texte non coupé, rien hors zone sûre, aucun chevauchement avec les sous-titres (contrôle automatique : bas du contenu ≤ 1179 px, sous-titres à 1206 px) ✅. Planche : `drafts/2026-11-07_VisaBallot/qc_contact_sheet.png`.
- Loudness : −16,2 LUFS intégré, pic −1,5 dBFS ✅. Voix ≈ 20 dB au-dessus de la musique seule (un peu plus que la cible de 12–17 dB : musique très discrète, voulue pour un sujet informatif).
- Voix : Kokoro af_heart (voix IA américaine, aucune voix australienne disponible). **Audio vérifié uniquement par mesure : personne ne l'a encore écouté.** Écoutez-la avant de publier, surtout « 2026 », « 179 » et « Home Affairs ».

## Avant de publier (Lucas)
- [ ] Écouter la vidéo en entier
- [ ] Revérifier la page Home Affairs le jour de la publication : si le ballot y apparaît, la vidéo est périmée
- [ ] Activer le label TikTok « AI-generated content »
- [ ] Coller la légende et choisir la cover
- [ ] Aucune promotion payante sans décision explicite

Hashtags : choisis pour leur pertinence. **Aucune preuve qu'ils soient en croissance.**

## Évaluation (organique)
Comparer à 72 h et 7 jours avec les 4 posts existants (`analytics/2026-11-07_baseline.md`) : comptes atteints, partages (objectif principal), saves, commentaires utiles, durée moyenne, complétion. Avec ce volume, on obtient une tendance, pas une preuve.

## Pas produit
Ouverture B : non produite (vous avez choisi le hook A). Elle peut être faite plus tard pour un test A/B payant, avec votre accord.
