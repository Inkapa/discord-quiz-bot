<div align="center">
  <img src="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp">
  <h1> Projet - Bot de Quiz </h1>
</div>

<div align="center">
  <a href="https://www.python.org/downloads/">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/Red-Discordbot">
  </a>
  <a href="https://github.com/Rapptz/discord.py/">
     <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
  </a>
  <a href="https://github.com/Inkapa/discord-quiz-bot/blob/master/LICENSE">
    <img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg">
  </a>
</div>
<br>
<div align="center">
  <a href="https://discord.com/oauth2/authorize?client_id=847830349060636682&permissions=8&scope=applications.commands%20bot"><img src="https://i.imgur.com/EiTBt5a.png"></a>
</div>

<div align="center">
  <a href="#presentation">Presentation</a>
  •
  <a href="#installation">Installation</a>
  •
  <a href="#utilisation">Utilisation</a>
  •
  <a href="#structure-bd">Structure BD</a>
  •
  <a href="#conception">Conception</a>
  •
  <a href="#conclusion">Conclusion</a>
  •
  <a href="#license">License</a>
</div>

# Presentation
Pour ce projet de fin d'année en Informatique à l'IUT de Reims, j'ai décidé de réaliser un bot discord capable 
de mettre en place et de gérer des quiz.

Le bot, surnommé "Projet?", est un bot autonome capable de créer, lancer et gérer des quiz à partir de commandes
Discord et de les lier à une base de données.

Vous pouvez télécharger le [Cahier Des Charges](https://github.com/Inkapa/discord-quiz-bot/blob/master/Files/CahierDesCharges.docx?raw=true)

# Installation

Pour utiliser ce bot il faut commencer par l'installation des dépendances 
```
pip install -r requirements.txt
```

Si vous n'avez jamais utilisé de bots auparavant, il vous faudra créer un bot via l'interface développeur de discord: https://discord.com/developers/applications

Assurez vous d'avoir activer les `Privileged Gateway Intents` sur l'onglet `Bot` du site ci-dessus. Ce a quoi cela doit ressembler:

![](https://cowboy.bebop.gg/i/4Ynv.png)

Il suffit ensuite de configurer le bot via le fichier de configuration `conf.json` dans le repertoire `Configuration`.

Voici un exemple:

```json
{
  "_instructions": "Pour récupérer votre token veuillez créer un bot via https://discord.com/developers/applications puis naviguez sur l'onglet 'Bot' et cliquez sur 'copiez le token'",
  "configuration": {
    "token": "token",
    "emplacement_bd": "../Database/DiscordBot.db",
    "prefix_bot": "-",
    "id_guilds": [
      783375356840640532
    ]
  }
}
```
`id_guilds` correspondent aux identifiant des serveurs dont votre bot fait partie.

**Si aucun `id_guilds` n'est spécifié les commandes seront activées en globale (encrâge des commandes pour tout les serveurs courants et future
du bot sans avoir besoin de spécifier d'identifiant de serveur). Néanmoins lors de la première execution du bot, les commandes globales pourront prendre jusqu'à 1 heure avant d'apparaître. Il est donc recommandé de spécifier un identifiant de serveur lors des tests et de passer en commandes globales lors de la mise en production.**

Une fois votre configuration terminé, vous pouvez executez le bot à l'aide du fichier `run.py`
```
python3 .\src\run.py
```

# Utilisation

Lors de l'invitation du bot sur un serveur, le bot s'occupera de créer un rôle `Projet Quiz Master` et de l'ajouter à l'utilisateur l'ayant invité.
Ce rôle peut être attribué à tout utilisateur pour lui donner la permission de créer et initialiser des quiz sur le serveur.

**ATTENTION: Le bot a besoin des privilèges administrateur pour fonctionner correctement**

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

**ATTENTION: Le bot utilise SQLite pour la base de données. Assurez-vous que SQLite (v.3.35 minimum) est installé sur votre machine**

Pour faire plaisir à Mme. Sandron, voici une représentation sous forme de MCD et MLD de la structure de ma base de données.

![](https://cowboy.bebop.gg/i/Bck2.png)

![](https://cowboy.bebop.gg/i/B7Xi.png)



A noter que la base de donnée du bot s'auto-génère, il n'est donc pas nécessaire d'executer le script SQL ou de créer de tables dans la BD.

**Pour re-initialiser la BD**, il suffit de supprimer le fichier `.bd` (par défaut `./Database/DiscordBot.db`). Une nouvelle BD vide sera générée lors de l'execution du bot.

# Conception

Représentation simpliste via des Use-Case UML:
![](https://cowboy.bebop.gg/i/Bhlo.png)

Représentation détaillée
![](https://media.discordapp.net/attachments/849645424167616532/850366679581982720/unknown.png?width=1367&height=676)

# Conclusion
J'ai trouvé ce projet très amusant, bien qu'il ai été plus difficile que premièrement imaginé.
J'ai dû changer la structure de la BD et mon organisation à multiples reprises lors du développement, et ce bien que j'ai réalisé la structure de la BD à l'avance en Merise. 
Mais j'ai au final sû rester organisé malgré tout, et ce jusqu'à la fin du projet à l'aide d'un planning prévisionnel solide *(merci Sufyan)*.

# License

Ce projet est sous license [MIT](LICENSE).