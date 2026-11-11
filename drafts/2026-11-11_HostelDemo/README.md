# HostelDemo — « 88 days. Lost count? » (11 nov. 2026)

**Statut : BLOQUÉ sur deux assets, tout le reste est prêt.** Rien d'exporté, rien de publié, 0 crédit dépensé.
Brief : `briefs/2026-11-11_hostel-demo-lost-count.md`. Dialogue, storyboard, affirmations, guides et besoins : `SCRIPT-STORYBOARD.md`.

| Fichier | Rôle |
|---|---|
| `dialogue.json` | Les 11 répliques (10 + ouverture B), voix par personnage |
| `audio/*.wav`, `audio/vo_timings.json` | Voix Kokoro (B1 `bf_emma`, B2 `am_michael`), durées, phonèmes |
| `spec.json` | Fenêtres de scènes, étapes de la démo (`clip_in` et `focus` **à calibrer** sur l'enregistrement), carte CTA |
| `tools/make_dialogue.py` | Synthèse des voix (misaki + Kokoro ONNX, gratuit) |
| `tools/assemble_reel.py` | Assemblage final : clips personnages + enregistrement réel + CTA, sous-titres, zooms, musique, −16 LUFS |
| `footage/` | **À déposer** : `eazy88_demo.mp4`, `scene1_problem.mp4`, `scene2_handover.mp4`, `scene3_reaction.mp4` |
| `previz/*_PREVIZ-not-for-posting.mp4` | Prévisualisation A et B avec cartes « placeholder » : minutage, voix, sous-titres, carte CTA. **Pas une vidéo finie.** |
| `character-prompts.txt`, `captions.txt` | Prompts des scènes personnages ; légendes TikTok / Reels / Shorts |

## Pour terminer (une fois les 4 fichiers dans `footage/`)
```
python3 tools/assemble_reel.py spec.json audio out --music            # version A
python3 tools/assemble_reel.py spec.json audio out --music --hook B   # ouverture B
```
Le script refuse de produire un fichier d'apparence finie tant qu'un clip manque. Avant l'export : calibrer `clip_in` / `focus` de chaque étape sur l'enregistrement, relire l'affirmation 4, puis contrôle qualité complet (ffprobe, planche, loudness, lip-sync, cohérence des personnages) et copie dans `exports/2026-11-11_HostelDemo/`.
