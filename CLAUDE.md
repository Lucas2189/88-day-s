# Eazy88 — Marketing workspace

Espace de travail marketing d'Eazy88 (Lucas, fondateur, Adelaide).
Ce fichier contient les instructions **permanentes**. Elles s'appliquent à chaque session.

## Langues

- Explications, rapports et échanges avec Lucas : **français**.
- Tout contenu public (voix off, texte à l'écran, sous-titres, légende, cover, hashtags) : **anglais naturel**.

## Instructions permanentes

1. **Audience.** Eazy88 cible les backpackers et les voyageurs en Working Holiday (visas 417 et 462) en Australie. Ne pas confondre avec les randonneurs ni avec les voyageurs internationaux en général.
2. **Identité de marque.** Préserver l'identité réelle de la marque (voir `brand/brand-identity.md`). Ne jamais inventer de logo, de couleur ni de police. Si deux sources se contredisent, demander à Lucas au lieu de choisir à sa place.
3. **Fonctionnalités vérifiées uniquement.** Avant toute affirmation sur le produit, vérifier `product/product-facts.md`, puis revérifier sur https://eazy88.com/en et https://apps.apple.com/au/app/eazy88/id6759782986. Une fonctionnalité *listée* n'est pas forcément *active* : confirmer qu'elle contient du vrai contenu avant de la promouvoir.
4. **Problème ou bénéfice immédiat.** Chaque contenu rend le problème ou le résultat utile évident tout de suite.
5. **Reels compréhensibles sans le son, dès la première image.** Le titre du hook est visible sur la toute première frame ; les sous-titres sont incrustés et reprennent la voix mot pour mot.
6. **Une idée principale et un seul CTA principal** par contenu.
7. **Voix off IA en anglais naturel.** Lucas n'enregistre ni son visage ni sa voix. Pas de présentateur artificiel (avatar) non plus. Rappeler d'activer le label TikTok « AI-generated content ».
8. **Ne jamais inventer** de statistiques, témoignages, commentaires, écrans d'application ou affirmations d'éligibilité au visa.
9. **Livrables finaux dans `exports/`**, avec des noms de fichiers clairs (convention dans `exports/README.md`).
10. **Rien sans l'accord explicite de Lucas :** publier, programmer, envoyer des messages, acheter un abonnement ou des crédits, dépenser des crédits de génération (Canva, invideo, etc.), lancer une campagne payante.

## Règles marketing (résumé des instructions fournies)

Source complète : `references/marketing-instructions/eazy88-tiktok-trend-video_SKILL_2026-11-07.md` et `references/marketing-rules.md`.

**Objectif.** Un seul objectif par vidéo, choisi avant d'écrire : *saves*, *shares*, commentaires utiles, *follows* ou visites qualifiées sur l'App Store. Seul le dernier exige de montrer l'app. Les vues seules ne sont pas un objectif. Ne jamais promettre viralité, ROI ou téléchargements.

**Protection de la marque**
- Pas d'affirmation de visa ou d'éligibilité : ne jamais laisser entendre qu'Eazy88 valide un travail éligible, garantit un emploi, un logement ou un visa, ou remplace Home Affairs ou Fair Work. Ne pas montrer l'écran « 88 Days Eligible » comme une certification.
- Attention : le site officiel lui-même contient des formulations d'éligibilité (« checks whether the job counts », « eligible jobs », « guides you through your Second Year Visa application »). **Ne pas les reprendre** dans nos contenus.
- Faits visa, salaire, impôts ou emploi : vérifier sur les sources officielles (immi.homeaffairs.gov.au, fairwork.gov.au, horticulture.fairwork.gov.au, ato.gov.au, abs.gov.au). Préciser à qui la règle s'applique, et distinguer *annoncé/proposé* de *en vigueur*. Tenir un tableau des affirmations (`templates/claims-table.md`).
- Écrans : uniquement de vrais écrans ou enregistrements de l'app avec des données de démo, étiquetés « Real app screens · demo data ». Ne jamais modifier une valeur ni inventer un tap. Graphismes originaux uniquement (illustrations, carte Natural Earth, fiche de paie marquée « EXAMPLE » sans vrais chiffres).
- Musique : originale ou licenciée pour l'usage prévu. Ne jamais supposer qu'un son tendance est libre de droits.
- App Store seulement : la fiche Google Play est introuvable (404 au 7 nov. 2026), ne pas mentionner Android.

**Recherche avant tout choix d'angle.** Priorité aux 30 derniers jours (7 jours pour les tendances rapides). Tableau de 5 angles : angle · source (URL, date, lieu) · signal observable · problème de l'audience · lien avec une fonctionnalité confirmée · statut (*verified emerging trend* / *ongoing audience need* / *creative hypothesis*). Ne pas forcer les 88 jours ni le produit : une vidéo utile sans l'app vaut mieux qu'un pont forcé. Faire tourner les thèmes ; jamais deux vidéos fiches de paie / relevés de travail d'affilée ; démo app au maximum une fois toutes les deux semaines.

**Format reel (30–40 s, 9:16, 1080×1920, 30 fps)**
- Hook 0–4 s qui nomme l'audience et le problème, puis 2–3 points concrets, un pont produit (~9 s, seulement pour l'objectif App Store) et un CTA unique adapté à l'objectif.
- Environ 95–105 mots de voix off. Pas d'intro générique, pas de peur, pas de fausse urgence, de la valeur avant le CTA.
- Trois hooks écrits ; le second sert d'ouverture alternative B (seuls les ~4 premières secondes et le titre changent).
- Zone sûre TikTok : éléments essentiels dans x 80–940, y 220–1380. Sous-titres incrustés (max. 2 lignes de ~42 caractères).
- Son : voix + éventuel fond musical original ; normalisation à −16 LUFS, TP −1,5.

**Contrôle qualité avant de dire « terminé ».** ffprobe (h264 + aac, 1080×1920, 30 fps, durée), planches de frames extraites du MP4 final (hook à 0,03 s, chaque scène, la fin), mesure de loudness, relecture de chaque affirmation contre le tableau. Préciser que l'audio n'a été vérifié que par mesure. Un export muet n'est jamais une « vidéo voix off terminée ».

**Mesure.** Publier seulement la version A en organique ; le test A/B propre se fait dans TikTok Ads Manager (avec l'accord de Lucas et un budget validé). Comparer à 72 h et 7 jours avec les posts de même format. Pour l'objectif App Store : vues 2 s / 6 s → clics → installations attribuables → activation (ex. `payslip_saved`). Eazy88 est gratuit : on évalue l'efficacité d'acquisition et d'activation, pas un ROI financier.

## Organisation du dossier

| Dossier | Contenu |
|---|---|
| `brand/` | Identité de marque, logos officiels (originaux en lecture seule). |
| `product/` | `product-facts.md` : fonctionnalités vérifiées, infos non confirmées, assets manquants. |
| `references/` | Instructions marketing fournies, captures textuelles et écrans du site et de l'App Store, sources officielles. |
| `briefs/` | Un brief par contenu, à partir de `templates/content-brief.md`. |
| `templates/` | Modèles (brief, tableau des affirmations, storyboard, checklist) et outils (voix off). |
| `drafts/` | Travail en cours : scripts, rendus intermédiaires, un sous-dossier par contenu. |
| `exports/` | Livrables finaux uniquement, noms de fichiers clairs. |
| `analytics/` | Suivi des performances (chiffres réels de la plateforme uniquement). |

## Règles de fichiers

- **Ne jamais écraser ni modifier un original.** Les fichiers dans `brand/logos/`, `references/marketing-instructions/` et `references/official-sources/` sont en lecture seule. Pour retoucher, copier dans `drafts/` puis travailler sur la copie.
- Nouvelles sources : les dater dans le nom (`AAAA-MM-JJ_...`).
- Les fichiers lourds téléchargés (modèle de voix, polices, carte) restent hors Git (voir `.gitignore`).
- Mettre à jour `product/product-facts.md` dès qu'une fonctionnalité est vérifiée ou contredite.
