<h1 align="center">
  <img src="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp">
  <br>
  Projet - Bot de Quiz
  <br>
</h1>
<hr>
<p align="center">
  <a href="https://www.python.org/downloads/">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/Red-Discordbot">
  </a>
  <a href="https://github.com/Rapptz/discord.py/">
     <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
  </a>
  <a href="https://iut-info.univ-reims.fr/gitlab/corn0050/projet-s2/LICENSE">
    <img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg">
  </a>
</p>

# Presentation
Pour notre projet de fin d'année en Informatique à l'IUT de Reims, nous avons décidé de réaliser un bot discord capable 
de mettre en place et de gérer des quiz.

Le bot, surnommé "Projet?", est un bot autonome capable de créer, lancer et gérer des quiz à partir de commandes
Discord et de les lier à une base de données.

Vous pouvez télécharger notre [Cahier Des Charges]()

Ainsi que notre [Plan de Projet]() 

(malheureusement, dû aux limitations du logiciel que l'on nous a forcé à apprendre et à utiliser en cours, l'exportation du Diagramme de Gantt pose certains problèmes de qualité visuelle)

# Installation

Pour utiliser ce bot il faut commencer par l'installation des dépendances 
```
pip install -r requirements.txt
```

Si vous n'avez jamais utilisé de bots auparavant, il vous faudra créer un bot via l'interface développeur de discord: https://discord.com/developers/applications

Il suffit ensuite de configurer le bot via le fichier de configuration `conf.json`

Voici un exemple:

```json
{
  "_instructions": "Pour récupérer votre token veuillez créer un bot via https://discord.com/developers/applications puis naviguez sur l'onglet 'Bot' et cliquez sur 'copiez le token'",
  "configuration": {
    "token": "token",
    "emplacement_bd": "../Database/DiscordBot.db",
    "prefix_bot": "-",
    "id_guilds": {
      "846487696573464616": "",
      "783759963981742100": "",
      "783375356840640532": "",
      "851375104168165417": "",
      "852687717128208426": "852689039088943114"
    }
  }
}
```
`id_guilds` correspondent aux identifiant des serveurs dont votre bot va faire partie.

A chaque identifiant de serveur est lié un identifiant de rôle qui représente l'identifiant du rôle d'administrateur de quiz.

Si aucun identifiant de rôle n'est spécifié, tout les utilisateurs du serveurs auront accès à toutes les commandes

Une fois votre configuration terminé, vous pouvez executez le bot à l'aide du fichier `run.py`
```
python3 .\src\run.py
```

# Utilisation

Le bot vient pre-configuré avec différentes commandes documentées. Les commandes, sous format de commandes slash `/command`, bénéficient
de l'autocomplétion Discord. Tapez `/` dans votre barre de message pour avoir une vue globale des fonctionnalités.

![](https://cowboy.bebop.gg/i/BHi7.png)

Voici un récapitulatif des commandes disponibles :

- **/help**

Permet d'avoir plus d'informations sur le fonctionnement d'une commande

- **/createquiz**
  
Permet de créer un nouveau quiz.

- **/addquestion** 
  
Permet de rajouter une question à un quiz à l'aide de son identifiant ou de créer un nouveau quiz si aucun identifiant de quiz n'est spécifié.

- **/getquizs** 

Permet d'afficher les quiz créés par l'utilisateur ou de récupérer l'entièreté disponibles dans la bd.

- **/getresults** 


  Permet d'afficher les résultats globaux d'une game de quiz.

- **/launchquiz** 
  

  Permet de lancer une game de quiz.

- **/leaderboard** 
  

  Permet d'afficher le classement des participants du serveur.

- **/viewresult** 
  

  Permet d'afficher les résultats personnels d'une game.

- **/recap** 
  

  Permet d'afficher un récapitulatif d'un quiz.

- **/reset** 
  

  Permet de reinitialiser les score et le classement des joueurs du serveur.
  
# Structure BD

Pour faire plaisir à Mme. Sandron, voici une représentation sous forme de MCD et MLD de la structure de notre base de données.

![](https://cowboy.bebop.gg/i/Bck2.png)

![](https://cowboy.bebop.gg/i/B7Xi.png)

A noter que la base de donnée du bot s'auto-génère, il n'est donc pas nécessaire d'executer le script SQL.

# Conception - interactions

Représentation simpliste:
![](https://cowboy.bebop.gg/i/Bhlo.png)

Représentation détaillée
![](https://media.discordapp.net/attachments/849645424167616532/850366679581982720/unknown.png?width=1367&height=676)

# Conlusion
Nous avons trouver ce projet très amusant, bien qu'il ai été plus difficile que premièrement imaginé.
Nous avons dû changer de structure de BD et d'organisation à multiples reprises mais nous avons au final sû rester 
organisé malgré tout, et ce jusqu'à la fin du projet.