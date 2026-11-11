# Brief — Hostel demo « 88 days. Lost count? » (deux backpackers + vraie démo de l'app)

> **Statut : préparé le 11 nov. 2026, en attente de deux éléments de Lucas** (enregistrement d'écran réel + scènes personnages générées). Travail en cours : `drafts/2026-11-11_HostelDemo/`. Rien n'est exporté, rien n'est publié, **0 crédit dépensé**.

| Champ | Valeur |
|---|---|
| Date | 11 nov. 2026 |
| Format | Vidéo verticale 9:16, 1080×1920, 30 fps, **30,0 s**, dialogue IA (deux voix distinctes), sous-titres incrustés. TikTok + Instagram Reels + YouTube Shorts |
| Pour qui | Titulaires d'un visa 417 ou 462 en train de faire leurs 88 jours, qui ont des fiches de paie éparpillées et ne savent plus où ils en sont |
| Problème (visible dès la 1re image) | Titre « 88 DAYS. LOST COUNT? » sur un backpacker qui fait défiler ses relevés de travail sur son téléphone |
| Idée principale | Ajouter ses fiches de paie dans Eazy88, vérifier les détails, et lire ses jours faits / restants sur l'écran d'accueil |
| Objectif principal | **Visites qualifiées sur l'App Store** (le seul objectif qui justifie de montrer l'app) |
| Pourquoi ça devrait marcher | La démo est l'événement principal : on voit ce qu'on entre (une fiche de paie), ce que l'app en lit (employeur, dates, heures, paie), l'étape de vérification, et où le résultat apparaît (accueil : jours faits / 88 et jours restants). Format « un voyageur aide un autre », sans présentateur |
| CTA (public, unique) | "Track your progress with Eazy88." + "Free on the App Store" |
| Lien produit | Oui. Fonctionnalités de la section 1 de `product/product-facts.md` : ajout de fiche de paie (photo / PDF), lecture par IA (employeur, dates, heures, revenu) avec vérification avant enregistrement, anneau de progression + jours restants sur l'accueil |
| Événement d'activation | `payslip_saved` (existence à confirmer auprès du développeur) |
| Thème de rotation | Relevés de travail / démo app (max. une fois toutes les deux semaines) |
| Dernière vidéo du même thème | Aucune démo app publiée. Cette vidéo **remplace** le Reel « Lost count? » prévu le mer. 18 nov. (même hook, même enregistrement requis). Les Stories « records » du ven. 13 sont du même thème : garder au moins un autre sujet entre les deux |
| Identité | Officielle (fond `#14110D`, Anton + Plus Jakarta Sans, orange `#F99660`, vert réservé à la progression, icône PNG officielle) |

## Recherche

Pas de nouvelle recherche d'angles : le concept est imposé par Lucas (brief du 11 nov.), et l'angle « lost count » a déjà été documenté le 7 nov. (`references/research/2026-11-07_research-angles.md`, besoin permanent de l'audience : 3 des 4 posts du compte portent sur le comptage des jours). Statut : *ongoing audience need*.

## Hooks (anglais, titre visible dès la 1re frame)

1. **(A, demandé par Lucas)** Titre « 88 DAYS. LOST COUNT? » · B1 : "How many days have I actually done?" · B2 : "Let's check in Eazy88."
2. **(B, ouverture alternative)** Titre « PAYSLIPS EVERYWHERE. HOW MANY DAYS? » · B1 : "Payslips everywhere. How many days is that?" · B2 : "Let's check in Eazy88." (seules les ~3 premières secondes et le titre changent ; déjà rendu en prévisualisation B)
3. (écarté) Titre « 88 DAYS: IS YOUR COUNT RIGHT? » · B1 : "Is my 88-day count even right?" → trop proche d'une promesse de précision du décompte (cf. avis App Store du 16 juin).

## Assets nécessaires

- [x] Dialogue, storyboard minuté, tableau des affirmations : `drafts/2026-11-11_HostelDemo/SCRIPT-STORYBOARD.md`
- [x] Voix de référence (Kokoro-82M, gratuit, deux voix distinctes) : `drafts/2026-11-11_HostelDemo/audio/`
- [x] Musique originale générée en code (libre par construction), carte de fin, sous-titres, pipeline d'assemblage
- [ ] **Enregistrement d'écran réel de l'app** (Lucas) → `drafts/2026-11-11_HostelDemo/footage/eazy88_demo.mp4`
- [ ] **3 clips de scènes personnages** (génération IA, outil à choisir, voir SCRIPT-STORYBOARD § 7) → `footage/scene1_problem.mp4`, `scene2_handover.mp4`, `scene3_reaction.mp4`

## Validation de Lucas

- [ ] Dialogue et storyboard validés (ou corrections)
- [ ] Choix de l'outil de génération des personnages et budget validés **avant toute dépense** (aucun outil gratuit disponible dans la session du 11 nov.)
- [ ] Enregistrement d'écran fourni
