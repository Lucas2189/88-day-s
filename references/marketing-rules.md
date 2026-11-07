# Règles marketing — version détaillée

Résumé structuré des instructions fournies (`marketing-instructions/eazy88-tiktok-trend-video_SKILL_2026-11-07.md`). Le résumé court est dans `CLAUDE.md`. En cas de doute, l'original fait foi, sauf pour les points marqués « mis à jour ».

## 1. Objectif et ton
- Une vidéo utile et crédible par demande. Un seul objectif principal : saves, shares, commentaires utiles, follows, ou visites qualifiées sur l'App Store.
- Lucas n'apparaît pas à l'écran et n'enregistre pas sa voix. Voix IA naturelle en anglais acceptée. Il n'aime pas le contenu IA « bon marché ».
- Ne jamais promettre viralité, ROI ou téléchargements. Ne jamais inventer de chiffres d'engagement, de croissance de recherche, de commentaires ou de conversion.

## 2. Protection de la marque
- Fonctionnalités vérifiées uniquement → `product/product-facts.md`.
- **Mis à jour le 7 nov. 2026 :** Google Play toujours introuvable → App Store uniquement.
- Aucune affirmation d'éligibilité ou de visa ; ne pas présenter l'écran « 88 Days Eligible » comme une certification.
- Faits officiels uniquement : immi.homeaffairs.gov.au, fairwork.gov.au, horticulture.fairwork.gov.au, ato.gov.au, abs.gov.au. Préciser à qui la règle s'applique (ex. titulaires 417/462 visant une 2e ou 3e année ; ressortissants britanniques exemptés du travail spécifié ; salariés et non contractants ABN ; travailleurs relevant du Horticulture Award). Séparer *annoncé/proposé* et *en vigueur*.
- Pas de faux : présentateurs artificiels, témoignages, commentaires, fausses actus, logos de médias, écrans inventés.
- Graphismes originaux : illustrations, carte Natural Earth (domaine public), fiche de paie « EXAMPLE » sans vrais chiffres.
- Musique originale ou licenciée.

## 3. Assets
- Chercher d'abord dans ce dossier (`brand/`, `references/`, `drafts/`).
- S'il manque un asset essentiel : terminer tout le reste, puis demander **une seule fois**, dans un message en français regroupé. La demande habituelle : un enregistrement d'écran iPhone de la fonctionnalité avec des données de démo, et éventuellement des images australiennes appartenant à Eazy88.
- Ne jamais présenter un placeholder comme une démo produit finie.

## 4. Recherche
- Date du jour d'abord. Priorité aux 30 derniers jours, 7 jours pour les tendances rapides.
- Thèmes : erreurs d'arrivée et de première semaine ; coûts réels, logement, économies ; trouver du travail, récoltes saisonnières, changement de région ; vie en hostel et voyage solo ; road trips, transports, achat de véhicule ; fiches de paie, relevés de travail, travail spécifié ; actualité australienne qui touche les WHM.
- Sources : ABC, SBS, The Guardian AU, presse régionale, Time Out ; Home Affairs, Fair Work, ABS ; Reddit et communautés si accessibles. TikTok Creative Center est souvent bloqué : essayer une fois, noter la limite, continuer. Les vues cumulées d'un hashtag ne prouvent pas une croissance actuelle en Australie.
- Tableau de 5 angles, puis notation : pertinence pour l'audience, utilité pratique, adéquation à l'objectif, effort de production (+ lien produit seulement si objectif App Store).
- Rotation des thèmes : trouver et préparer un job · vie de backpacker et hostel · logement et déménagement · budget et décisions de voyage · actualité australienne vérifiée · relevés de travail et démos app (max. une toutes les deux semaines). Jamais deux vidéos fiches de paie d'affilée.

## 5. Concept et script
- Nommer : pour qui (une situation précise), la promesse unique, l'objectif, pourquoi la vidéo devrait l'atteindre. Pour l'objectif App Store : l'événement d'activation (ex. première fiche de paie enregistrée), montré avec de vrais écrans.
- Trois hooks ; garder celui qui nomme l'audience et le problème en 0–2 s. Promettre la réponse dans le titre d'ouverture. Pas de question vague, de peur ou de clickbait. Le deuxième hook devient l'ouverture B.
- Structure 30–40 s : hook (0–4 s) → 2–3 points concrets avec un visuel simple chacun → pont produit (~9 s, objectif App Store uniquement) → un CTA (save, send, question facile, follow avec promesse de contenu, ou download). Jamais plusieurs CTA.
- ~95–105 mots ≈ 35–39 s (Kokoro, vitesse 1.0).
- Tableau des affirmations : affirmation · source officielle · à qui elle s'applique · en vigueur ou proposée.
- Voix off découpée en un clip par sous-titre (1,5–4,5 s).

## 6. Production (pipeline testé, entièrement gratuit)
- Voix : Kokoro-82M ONNX (Apache-2.0), voix `af_heart`, phonèmes écrits à la main (pas d'espeak). Prononciations fixes : Eazy88 = `ˈizi ˈAɾi ˈAt`, etc. Aucune voix australienne disponible : le dire. Script : `templates/tools/make_voiceover.py`.
- Vérifier chaque clip (pics de syllabes, pauses internes ≥ 90 ms).
- Timeline construite à partir des vraies durées WAV : premier clip à 0,15 s ; 0,17–0,22 s entre clips ; ~0,4 s entre sections ; ~1,5 s après le CTA.
- Image : frames Pillow → ffmpeg, 1080×1920, 30 fps. En-tête « EAZY88 · BACKPACKER TIPS » + wordmark ; chiffres de section, cartes, puces pour la règle clé ; notes de source ~27 px.
- Zone sûre : x 80–940, y 220–1380. Sous-titres incrustés à partir de y≈1206, 46 px, blanc sur boîte sombre translucide, max. 2 lignes ; SRT généré à partir des mêmes repères.
- Écrans réels : masque arrondi, ombre douce, fondus, contour sur la zone décrite, ligne d'étapes « Add › Read › Check › Save ».
- Encodage : libx264 crf 18, yuv420p, high 4.2 ; AAC 192k ; `+faststart`.
- Musique : fond original généré en numpy, ou rien. Mixage sous la voix, fondu final 1,2 s, loudnorm deux passes −16 LUFS / TP −1,5. Exporter aussi une piste voix seule.
- **Note :** couleurs et polices de cette section dépendent de la décision d'identité (`brand/brand-identity.md`).

## 7. Contrôle qualité
- ffprobe : h264 + aac, 1080×1920, 30/1, durée dans la plage.
- Frames extraites du MP4 final : hook (0,03 s), chaque scène, chaque surlignage, fin. Vérifier : texte coupé ou superposé, éléments hors zone sûre, sous-titres ≠ voix, CTA lisible, interface inventée.
- Loudness ≈ −16 LUFS intégrés ; voix 12–17 dB au-dessus de la musique seule.
- Relecture de chaque affirmation. Dire que l'audio n'a été vérifié que par mesure.

## 8. Livrables
- Dossier de production (artifact Docs) : résumé ; A recherche + limites ; B concept + objectif ; trois hooks ; C script final + tableau des affirmations ; D storyboard minuté ; E cover, légende (anglais, prête à coller) et 3–5 hashtags (sans preuve de croissance) ; F ouverture alternative ; plan d'évaluation ; assets manquants + checklist avant publication ; sources.
- Fichiers dans `exports/` : `Eazy88_TikTok_<Topic>_A.mp4` / `_B.mp4`, `.srt`, `_Voiceover.wav`, `_Cover.png` (1080×1920), dossier source éditable, ZIP `Eazy88_TikTok_<Topic>.zip`.

## 9. Évaluation
- Organique : version A seulement. A/B propre dans TikTok Ads Manager (créa comme seule variable ; vérifier le budget minimum ; **accord de Lucas obligatoire**).
- Objectifs save/share/comment/follow : comparer aux posts du même format au même âge (72 h, 7 j), dénominateur = comptes atteints.
- Objectif App Store : vues 2 s / 6 s, durée moyenne, complétion → CTR, clics App Store → installations attribuables, coût par installation → activation (taux, coût) → temps de production + dépenses.
- Suivi nécessaire : événement in-app d'activation, SDK TikTok ou outil d'attribution (AppsFlyer, Adjust, Branch), limites SKAdNetwork, lien de campagne App Store Connect en bio (utilisateurs consentants seulement).
- Décision : coût par activation, puis rétention précoce. Pas de seuils universels ; faible volume = tendance, pas preuve. Pas de ROI financier (app gratuite).
