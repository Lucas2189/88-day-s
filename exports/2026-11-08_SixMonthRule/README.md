# Eazy88 TikTok — SixMonthRule (version A) · prévu le 10 nov. 2026

**Statut : export final, non publié.** Coût : 0 crédit (rendu local).

| Fichier | Contenu |
|---|---|
| `Eazy88_TikTok_SixMonthRule_A.mp4` | 1080×1920, 30 fps, 36,0 s, H.264 + AAC stéréo, voix IA + musique originale, sous-titres incrustés |
| `Eazy88_TikTok_SixMonthRule.srt` | 12 sous-titres, identiques à la voix |
| `Eazy88_TikTok_SixMonthRule_Voiceover.wav` | Voix seule, −16 LUFS |
| `Eazy88_TikTok_SixMonthRule_Cover.png` | Cover 1080×1920 (= 1re image) |
| `Eazy88_TikTok_SixMonthRule_Caption.txt` | Légende (anglais) + titre YouTube Shorts |

- **Pour qui :** titulaires d'un visa 417 ou 462 qui approchent 6 mois chez le même employeur.
- **Problème, visible dès la 1re image :** « 6 MONTHS WITH ONE EMPLOYER? YOUR JOB MAY BE EXEMPT ».
- **Réponse :** la règle par défaut, les exemptions en vigueur, et que faire si on n'est pas exempté.
- **CTA unique :** "Save this before you sign your next job." (objectif : sauvegardes)

## Script (voix = sous-titres)
> Close to six months with one employer? On a working holiday visa, your job might be exempt. One. The default rule is six months' work with any one employer. It counts the months since you started, not your hours. Two. Some sectors are exempt right now, including tourism and hospitality, agriculture, health, aged care and childcare. Same employer, different locations? You can stay longer if each location is six months or less. Three. Not exempt? You'd need permission, and it's only given in limited cases. Save this before you sign your next job.

## Affirmations (toutes en vigueur, revérifiées le 8 nov. 2026)
| Affirmation | Source |
|---|---|
| 6 mois de travail maximum chez un même employeur (condition 8547) | Home Affairs, WHM latest news + page 8547 (mise à jour le 4 nov. 2026) |
| Compté en mois depuis le début du contrat, pas en heures | Page 8547 |
| Exemptés : tourisme et hôtellerie, agriculture, santé, soins aux personnes âgées, garde d'enfants ; plusieurs lieux (6 mois max chacun) | Page 8547, « until the Government makes further decisions » |
| Sinon, autorisation nécessaire, accordée dans des cas limités | Page 8547, section « Requesting permission » |

Citations : `references/official-sources/2026-11-08_home-affairs_8547-and-processing_notes.md`.
Volontairement non mentionnés dans la voix, mais cités en note et dans la légende : culture végétale et animale, reconstruction après catastrophe, certaines industries du nord de l'Australie.

## Contrôles effectués
- ffprobe : h264 + aac 48 kHz stéréo, 1080×1920, 30/1, 36,0 s ✅
- Volume : −16,2 LUFS ✅ · voix ≈ 20 dB au-dessus de la musique (musique très discrète) · voix bien présente dans le MP4 (enveloppe corrélée à 0,96) ✅
- Sous-titres : 12 repères, texte identique à la voix, aucun dépassant 4,5 s (max. 3,9 s) ✅
- Images du MP4 final (hook à 0,03 s, chaque repère, fin) : rien de coupé, rien sous les sous-titres (bas du contenu ≤ 1172 px, sous-titres à 1206 px) ✅
- Orthographe : tous les mots publics relus ✅

## Points non résolus
- **Audio vérifié par mesure uniquement** : personne ne l'a encore écouté. À écouter avant de publier, surtout « hospitality », « agriculture » et « childcare ».
- Voix IA américaine (pas de voix australienne gratuite) : activez le label « AI-generated content ».
- Règle temporaire (« until the Government makes further decisions ») : revérifiez la page 8547 le jour de la publication.
