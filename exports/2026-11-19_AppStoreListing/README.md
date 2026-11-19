# Fiche App Store Eazy88 — nouvelle version (brouillon du 19 nov. 2026)

**Statut : brouillon à valider par Lucas, rien n'est modifié sur l'App Store.** Texte à copier-coller : `Eazy88_AppStore_Listing_v2.txt` (anglais, nombre de caractères vérifié pour chaque champ).
Fiche actuelle relue le 19 nov. 2026 (identique au 7 nov.) : version 1.1, note 2,0/5 sur 4 notes, langue anglais uniquement.

## Pourquoi la changer
1. **Elle promet ce qui n'existe pas encore.** 6 rubriques sur 8 (Jobs, Housing, Cars, Road trips, Insurance, Map) n'ont pas de vraies annonces : les gens installent pour ça, ne trouvent rien, et partent déçus.
2. **Elle contient des affirmations d'éligibilité** (« validated visa days », « visa-eligible jobs ») : risque pour la marque, et le décompte est justement critiqué dans le seul avis écrit.
3. **Elle ne contient pas les mots que les backpackers cherchent** (« 88 days » n'est que dans le sous-titre ; « payslip », « farm work », « second year visa », « WHV » sont absents du nom et du sous-titre).

## Ce qui change
| Champ | Aujourd'hui | Proposé |
|---|---|---|
| Nom | Eazy88 | **Eazy88: 88 Days Tracker** (option A) — ou inchangé (option B) |
| Sous-titre | Your 88 days companion | **Working holiday payslips** (A) — ou **Track 88 days & payslips** (B) |
| Mots-clés | (invisibles) | 100 caractères, sans répéter le nom ni le sous-titre : backpacker, farm, work, second, year, visa, WHV, 417, 462… |
| Texte promotionnel | (aucun visible) | Photo, PDF ou galerie · 88 jours · gratuit |
| Description | 8 rubriques, dont 6 vides ; « validated visa days », « visa-eligible jobs » | 3 fonctions réelles (88 jours, fiches de paie, documents de travail) + « Free » + « Coming soon » honnête + rappel « Home Affairs décide, pas l'app » |
| Captures | (à voir dans App Store Connect) | 5 captures, une idée chacune, dans l'ordre : 88 jours → ajout d'une fiche de paie → vérification → documents → gratuit |

Toutes les affirmations viennent de `product/product-facts.md` (fonctions vérifiées) : app gratuite sans abonnement, suivi des 88 jours (anneau et calendrier), ajout par photo / PDF / galerie, lecture de l'employeur, des dates, des heures et de la paie avec vérification avant l'enregistrement, espace Work (fiches de paie, CV, certifications).
Volontairement absents : sécurité (AES, AWS), mode hors ligne, connexion Google, « 7 eligible sectors », « thousands of backpackers » (non vérifiés), Google Play (introuvable).

## Comment l'appliquer (App Store Connect)
- **Tout de suite, sans nouvelle version :** le **texte promotionnel**. Apple indique qu'il se modifie à tout moment.
- **Avec la prochaine version de l'app :** nom, sous-titre, description, captures, « What's New ». Pour les mots-clés, la documentation d'Apple n'est pas claire : prévoir de les changer avec la nouvelle version.
- Remplir **[SUPPORT EMAIL]** et le modèle **What's New** avec ce qui est réellement dans la version (ne rien annoncer qui ne soit pas livré).
- **Captures :** vrais écrans de l'app avec des données de démo (fiche de paie « EXAMPLE », pas de vraie personne). La fiche de paie d'exemple existe : `drafts/2026-11-07_LostCount/props/Eazy88_EXAMPLE_payslip_for-demo-recording.pdf`.

## La note de 2,0/5
- **D'abord corriger le décompte** dans le cas signalé (semaine de 48 h dont le lundi, le mardi, le samedi et le dimanche ne sont pas comptés), en le comparant à la règle de Home Affairs.
- **Remise à zéro de la note** : possible au moment où une nouvelle version sort. C'est irréversible, cela vaut pour tous les pays, et les avis écrits restent affichés. Apple conseille de l'utiliser rarement. Mon avis : à faire seulement avec la version qui corrige le décompte, puisque les 4 notes actuelles portent sur un problème réglé.
- **Demander des notes** dans l'app après un bon moment (par exemple après l'enregistrement d'une fiche de paie), pas au premier lancement.

### Réponse proposée à l'avis de corentin.20 (16 juin)
L'avis est en français. Notre règle est « contenu public en anglais », mais répondre en français à un avis écrit en français est plus naturel : **à vous de choisir** (version anglaise en dessous).

> Bonjour, merci d'avoir pris le temps d'écrire, et désolés pour cette mauvaise expérience. Nous regardons de près le cas d'une semaine de 48 heures dont certains jours ne sont pas comptés. [À ajouter seulement si c'est vrai : « C'est corrigé dans la version X.X. »] Si vous voulez nous aider à vérifier, écrivez-nous à [SUPPORT EMAIL] (sans données personnelles). L'équipe Eazy88

> Hi, thanks for taking the time to write, and sorry for the experience. We're looking closely at the case of a 48-hour week where some days aren't counted. [Only if true: "This is fixed in version X.X."] If you'd like to help us check, write to us at [SUPPORT EMAIL] (no personal details needed). The Eazy88 team

## Plus tard
- **Pages produit personnalisées** (« custom product pages ») : une version de la fiche par source (par exemple, les gens qui viennent de TikTok voient d'abord les 88 jours). Utile quand il y aura du trafic à mesurer.
- **Liens de campagne** App Store Connect pour chaque canal (TikTok, auberges, groupes), pour savoir d'où viennent les installations.

## Sources
- Limites et règles des champs : [Creating your product page](https://developer.apple.com/app-store/product-page/), [Platform version information](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information/), [App Store search](https://developer.apple.com/app-store/search/)
- Remise à zéro de la note : [Reset an app overview rating](https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/reset-an-app-overview-rating/), [Ratings, reviews, and responses](https://developer.apple.com/app-store/ratings-and-reviews/)
- Liens de campagne : [Campaign links](https://developer.apple.com/help/app-store-connect-analytics/acquisition/campaign-links/)
- Fiche actuelle : https://apps.apple.com/au/app/eazy88/id6759782986 (relue le 19 nov. 2026)
