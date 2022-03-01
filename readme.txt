+-------------------------------------------------------+
+							+
+			MATCHA				+
+							+
+-------------------------------------------------------+

+----------------------TEMPLATE-------------------------+
##
  -
    =>
    a)
    1)
+-------------------------------------------------------+
+			GENERAL				+
+-------------------------------------------------------+

#MATCHA-Application de rencontre

##Description
- Proposer un site de rencontre
- L'utilisateur peut s'inscrire et renseigner ses détails personnels et ses préférences dans l’autre
- Pouvoir matcher un autre utilisateur ayant un profil plus ou moins correspondant, parmi une selection de profils d’autres utilisateurs que votre site proposera.
- Une fois qu’ils se sont réciproquement matchés, ces deux profils devront pouvoir s’échanger des mots doux et plus si affinités via un chat privé que vous aurez conçu.

##General
- Rendre auteur
- erreurs relatives à l’absence d’HTTPS sur la console web seront tolérées
- Laguage libre
- MicroFramework autorisé
=>Flask en Python
- Coté client, HTML, CSS et JavaScript, librairies front autorisé
=>React, Vue, Bootstrap, Semantic
- Pas de faille sécu
- Serveur libre
=>Apache/Nginx?
- Compatible Firefox (>= 41) et Chrome (>= 46)
- BDD libre
=>MySQL
/!\ INTERDIT /!\
+-------------------------------------------------------+
##Interdit d'utiliser des Librairie externe proposant
- Un ORM ou un ODM
- Un validateur de donnée
- Une gestion des comptes utilisateurs
- Une gestion de BDD
+-------------------------------------------------------+
- Présentable sur mobile, gerer la résolution sur des petites résolutions
- Formulaires avec validation correcte, client et serveur
- Pas de mdr en clair en vdd
- Protection injection XSS html et js
- Protection XSS upload
- Protection Injection sql

+-------------------------------------------------------+
+			MANDATORY PART			+
+-------------------------------------------------------+

+-----------------INSCRIPTION ET CONNEXION--------------+

#Description

##Inscription
- Le Formulaire Demande au minimum
=>Email
=>Nom d'utilisateur
=>Nom
=>Prenom
=>Mot de passe minimum sécurisé
- Email de confirmation

##Connexion
- Avec Nom d'utilisateur/Mot de passe
- Mot de passe oublié, lien de réinitatiolasion de mot de passe
- Deconnexion depuis n'importe quel page du site

#INSCRIPTION ET CONNEXION

##Front
-Page inscription
a)formulaire inscription
=>validation input
=>error
-Page connexion
a)formulaire connexion
=>validation input
=>error
b)link forgot password
-boutons déconnexion

##Back
-inscription request
a)input validation
b)validate email
-resend password request
-logout request

+-----------------PROFIL DE L'UTILISATEUR--------------+

#PROFIL DE L'UTILISATEUR

##Complétion de profil (public info)
- Genre
- Orientation sexuelle
- Une bio courte
- Liste d'intérêt #ex réutilisable.
- Des images maximum 5 dont 1 qui sert de photo de profil
##User panel
-A tout moment il peut éditer toutes ses informations (private and public)
-pouvoir changer de mot de passe ou le réinitialiser
-pouvoir consulter les personnes ayant consulté son profil et ses 'likes'
-score de popularité public
-géolocalisation, à l'arrondissement près
=>Si il refuse, trouver un moyen de le localiser maigres lui
=>l'utilisateur peut modifier sa localisation sur son profil

+-----------------MATCH ME IF YOU CAN------------------+

#Description

L’utilisateur doit pouvoir avoir accès à une liste de suggestions qui lui correspondent, du match total au match plus ou moins partiel.
Cette sélection ne sera pas possible tant que le profil étendu de l’utilisateur n’est pas renseigné. Dans ce cas là, vous devez l’inviter à le remplir.

#MATCH ME IF YOU CAN

##Condition matching
- profil étendu remplis sinon inviter l'user à le faire
- liste de suggestion possible que si profil étendu remplis
- matcher si au moins 1 critère correspond
- Bisexualité par défaut
##Critère matching
- Pondérer les critères
- Ordre de priorités
1)Orientation sexuelle définie
2)Proximité géographique
3)Centre d'intérêts
3)Score de popularité
-résultats triable par
=>âge
=>localisation
=>popularité
=>tags en communs
- liste de selection possible que si profil étendu renseigné
-résultat filtrable par
=>intervalle d'âge
=>localisation
=>intervalle de popularité
=>tags

+-----------------RECHERCHE----------------------------+

#Description

L’utilisateur doit pouvoir effectuer une recherche avancée en sélectionnant un ou plusieurs critères

#RECHERCHE (liste de sélection)

##Critères
- intervalle d'âge
- intervalle de score de popularité
- localisation
- un ou plusieurs tags d'intérêt
##Actions supplémentaire
- résultat triable
- résultat filtrable

+-----------------PROFIL DES AUTRES UTILISATEURS-------+

#Description

Un utilisateur doit pouvoir consulter le profil des autres utilisateurs, qui doit contenir toutes les informations disponibles sur ce dernier, excepté l’adresse email et le mot de passe.

#PROFIL DES AUTRES UTILISATEURS

##Informations à afficher
- Tous sauf
=>email
=>mot de passe
##Action
- historique des visites 'vus'
- "liker" ou "unlinked" un utilisateur si le visiteur possède au moins une photo
- voir que le profil visité à déjà liker l'utilisateur et peut liker en retour
- consulter le score de popularité
- voir si l'user est en ligne sinon dernière date de connexion
- reporter l'user comme "faux compte"
- bloquer l'user
a) l'user bloqué ne doit plus apparaitre dans les recherches
b) ne doit plus générer de notification

+-----------------CHAT---------------------------------+

#Description

Lorsque deux utilisteurs se sont “likés” mutuellement, on dira qu’ils ont “matchés” et de ce fait, ils doivent pouvoir “chatter” tous les deux en temps réel

##CHAT
- Implémentation libre
- l'user doit pouvoir voir depuis n'importe quel page qu'il à reçu un message
- seuls les 2 users peuvent interagir dans la room

+-----------------NOTIFICATIONS-------------------------+

#Description

Un utilisateur doit être notifié, en temps réel5, 10 sec accepté

#NOTIFICATIONS

- Reçu un "like" 
- Reçu une visite
- reçu un message
- un user "like" à "liker" en retour
- un user matcher ne vous "like" plus
- l'user doit pouvoir voir depuis n'importe quel page qu'une notification n'as pas été lue

+-----------------CONTRAINTES ET OBLIGATIONS------------+

#En résumé

##Technologies
- Language autorisés :
=>[SERVER] Libre
=>[CLIENT] HTML (template ou non) - CSS - JavaScript
- Framework
=>[SERVER] Micro Framework
=>[BDD] Base de données relationnelles ou orienté graphe
=>[CLIENT] Tous
##Librairies
- Librairie ok SAUF :
a)un ORM ou un ODM
b)un validateur de données
c)une gestion de comptes utilisateur
d)une gestion de base de données
##Seed
- fournir un seed au rendu
=>hydrate la vdd avec un ensemble de faux profil, correctement renseignés
=>entre 500 et 1000 profils différents - qui testera l'optimisation du site
=>s'aider de librairies qui fake les profil pour nous
=>seed utilisé pendant la correction

+-------------------------------------------------------+
+			BONUS PART			+
+-------------------------------------------------------+

+-----------------IDEES DE BONUS--------------+

##Exemples
- Gérer les genres et orientations sexuelle non binaires de manière plus précise
- Ajouter des stratégie OAuth pour la connexion au site en plus de la notre
- Charger des images depuis un réseau social
- Faire une messagerie intégrée accessible à tout moment en footer de l'app (cf: Facebook)
- Faire une carte interactive des utilisateurs (géolocalisation plus précise)




