# Eazy88 TikTok — RulesChange120 (version A)

Produit le 25 nov. 2026. **Statut : export final, non publié.** Coût : 0 crédit (rendu local). Sujet urgent : les inscriptions ouvrent le 1er déc. 2026.
Brief : `briefs/2026-11-25_rules-change-120.md`. Sources : `references/official-sources/2026-11-24_whm-120-days-and-invitations_notes.md`.

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_RulesChange120_A.mp4` | 1080×1920, 30 fps, 39,75 s, H.264 + AAC stéréo, voix IA + musique originale, sous-titres incrustés |
| `Eazy88_TikTok_RulesChange120.srt` | 14 sous-titres, identiques à la voix |
| `Eazy88_TikTok_RulesChange120_Voiceover.wav` | Voix seule |
| `Eazy88_TikTok_RulesChange120_Cover.png` | Cover (= 1re image) |
| `Eazy88_TikTok_RulesChange120_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

Source éditable : `drafts/2026-11-25_RulesChange120/spec.json` + `vo_lines.json` (rendu avec `templates/tools/render_reel.py`, voix à vitesse 1,0).
Suite de « Ballot update » (16 nov.), qui disait « Follow Eazy88. We'll post when it's decided ».

## Concept
- **Pour qui :** backpackers en 417 / 462 qui font (ou vont faire) leur travail spécifié pour un 2e visa.
- **1re image :** « IT'S OFFICIAL: 88 DAYS BECOMES 120 DAYS » + « 2ND WHV · 417 / 462 · FROM 1 MARCH 2027 ».
- **3 points :** 120 jours à partir du 1er mars 2027 · invitation obligatoire, inscriptions dès le 1er déc. · encore 88 jours si dossier déposé avant le 28 févr. 2027.
- **Objectif :** enregistrements. **CTA unique :** « Save this so you don't miss the dates. »
- **Sans l'app.**

## Script (voix = sous-titres)
> It's official: the second-year visa rules are changing. Doing your 88 days? Here's what Home Affairs announced. One. From 1 March 2027, a second visa needs 120 days of specified work, not 88. Work you've already done still counts. Two. From March, you'll also need an invitation to apply. Registrations open on 1 December, and you can register before you finish your days. Three. Finish your 88 days and lodge your application by 28 February? You can still use the current process. The third visa stays at six months. Save this so you don't miss the dates.

## Affirmations
| Affirmation | Source officielle | Statut |
|---|---|---|
| 2e visa : 120 jours de travail spécifié à partir du 1er mars 2027 (88 aujourd'hui) | Home Affairs (article + infographie, 17 nov. 2026) ; ministre (« three months to four months ») | Annoncé, en vigueur le 1er mars 2027 |
| Le travail déjà fait compte | Communiqué du ministre, 17 nov. 2026 | Annoncé |
| Invitation obligatoire à partir du 1er mars 2027 ; inscriptions dès le 1er déc. 2026 ; inscription possible avant d'avoir fini | Infographie et page WHM latest news (17 nov. 2026) | Annoncé |
| L'inscription ne garantit pas d'invitation | Article Home Affairs, 17 nov. 2026 | Annoncé |
| Exemption : titulaires d'un passeport britannique | Infographie (« except UK passport holders ») | Annoncé |
| 88 jours + demande valide déposée au plus tard le 28 févr. 2027 = processus actuel, sans invitation | Infographie ; page WHM latest news | Transitoire, annoncé |
| 3e visa : toujours 179 jours (6 mois) | Infographie ; ministre | Inchangé |

Non dit volontairement : le nombre de places (45 000 / 25 000), les frais et le lien d'inscription (pas encore publiés), le détail des tirages mensuels.

## Contrôles (MP4 final)
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 39,75 s ✅
- 14 sous-titres, texte identique à la voix, 3,7 s maximum à l'écran ✅
- Planche de 16 images : `drafts/2026-11-25_RulesChange120/qc_contact_sheet.png` ; contenu au-dessus des sous-titres (bas à y = 1170, limite 1190) ✅
- Son : −16,1 LUFS, pic −4,5 dBFS ✅
- Orthographe et dates relues contre les sources ✅

## Points non résolus
- **Le son n'a été vérifié que par mesure.**
- Revérifier immi.homeaffairs.gov.au le jour de la publication (les modalités d'inscription doivent paraître avant le 1er déc.).
- Voix générée par IA : laisser le label « AI-generated content » activé.
