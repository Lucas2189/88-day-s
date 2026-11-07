# Eazy88 — « 88 DAYS. LOST COUNT? » · livrables du 7 nov. 2026

Brief : `briefs/2026-11-07_lost-count-work-records.md`. **Rien n'est publié.** Coût : **0 crédit**, tout est rendu en local.

## État des livrables

| Livrable | Statut | Fichiers |
|---|---|---|
| Carrousel Instagram, 5 visuels 1080×1350 PNG | ✅ **exporté** | `carousel/Eazy88_Carousel_RecordsChecklist_01…05.png` |
| Stories, 3 images 1080×1920 PNG | ✅ **exportées** (+ 2 guides pour placer les stickers) | `stories/…_01/_02/_03.png`, `stories/sticker-guides/` |
| Légendes, un seul fichier texte | ✅ | `Eazy88_LostCount_Captions.txt` |
| Sources éditables | ✅ | `source/` (descriptions JSON, voix, clips audio, accessoires, scripts) |
| **Reel 1080×1920 MP4 avec voix et sous-titres** | ❌ **NON EXPORTÉ : bloqué** | — (voir ci-dessous) |

## ❌ Blocage exact du Reel

Le Reel approuvé doit **montrer le vrai parcours dans l'app** : Add › Read › Check › Save › Track. **Aucun enregistrement d'écran réel de l'app n'existe** dans le dossier, dans les fichiers envoyés ni sur la machine (vérifié le 7 nov. 2026).

- Les écrans officiels du site (accueil, Work, Admin, Travel, Map) ne montrent **ni la lecture d'une fiche de paie, ni l'écran de vérification, ni « Confirm & Save »**. Les utiliser pour ces étapes reviendrait à inventer la démo, ce qui est interdit.
- Aucun outil disponible ne peut produire ces images. Canva vidéo est bloqué par votre offre, et une IA générative inventerait de toute façon l'interface.
- Il n'existe qu'un **aperçu de travail** avec des zones « PLACEHOLDER » : `drafts/2026-11-07_LostCount/reel/Eazy88_Reel_LostCount_DRAFT-preview.mp4`. **Ce n'est pas une vidéo finie** et il ne doit pas être publié.

**Pour débloquer :** enregistrez l'écran de l'iPhone sur un compte de démo, en important `source/props/Eazy88_EXAMPLE_payslip_for-demo-recording.pdf`. Le parcours : Add a payslip → PDF → lecture → vérification → Confirm & Save → accueil. Comptez 15 à 25 s, gestes lents. Déposez le fichier sous `drafts/2026-11-07_LostCount/reel/footage/eazy88_add-payslip_demo.mp4`. Le rendu final prend environ une minute. Je vérifierai ensuite que chaque étape annoncée par la voix correspond bien à ce que montre l'enregistrement.

## Contrôles effectués

| Contrôle | Résultat |
|---|---|
| Dimensions | Carrousel 5 × 1080×1350 · Stories 3 × 1080×1920, RVB ✅ |
| Orthographe | Les 76 textes publics ont été relus, mot par mot. Aucune faute ; orthographe australienne et britannique (« organised ») ✅ |
| Lisibilité | Corps de texte ≥ 36 px (sauf notes de source à 25 px), contraste crème ou orange sur fond sombre. Planches et visuels pleine taille inspectés ✅ |
| Cadrage | Contrôle automatique de zone sûre : carrousel ≤ 1290 px (contenu jusqu'à 1120 px), Stories entre 250 et 1580 px (contenu jusqu'à 1546 px). Rien de coupé, rien sous les barres d'Instagram ✅ |
| Affirmations | Chaque fait indique sa source officielle (Home Affairs 417, Fair Work) et la date de vérification ✅ |
| Démo de l'app | **Story 3** : écran officiel de l'accueil, reproduit tel quel (aucune valeur modifiée), étiqueté « Real app screen · eazy88.com ». ⚠️ Vous n'avez pas confirmé qu'il montre des données de démo : la mention « demo data » a donc été retirée. **Reel** : pas de démo, voir le blocage. |
| Sous-titres et audio | Sans objet tant que le Reel n'est pas exporté |

## Points à connaître avant publication

- L'écran d'accueil (Story 3) affiche « 7 validated · 2 pending ». C'est la vraie interface, mais le mot « validated » peut laisser croire à une validation officielle. Si ça vous gêne, remplacez-le par votre propre capture.
- Le carrousel cite la page du visa 417. Pour le 462, il renvoie le lecteur vers la page de son visa.
- Publiez le carrousel séparément des vidéos TikTok sur les relevés de travail (règle de rotation des thèmes).
- Stickers à ajouter dans Instagram : un **sondage** (Story 1) et un **lien App Store** (Story 3). Les guides montrent où les placer.

## Sources éditables (`source/`)

- `carousel_spec.json`, `stories_spec.json`, `reel/spec.json` : tous les textes et la mise en page, modifiables.
- `reel/vo_lines.json` + `reel/audio/` : la voix off, phrase par phrase.
- `props/` : la fiche de paie EXAMPLE pour l'enregistrement, et l'écran officiel de l'accueil.
- `tools/` : copies des scripts. Pour relancer un rendu, utilisez ceux de `templates/tools/` dans le dépôt, qui ont accès aux polices et au logo de `brand/`.
- Pas de fichier Canva : les outils de design Canva ne sont pas disponibles dans cette session.
