# -*- coding: utf-8 -*-
"""
Created on Thu Jun  10 17:15:48 2021

@author: Liam
"""

import discord
from discord.ext import commands
from pathlib import Path
from discord_slash import SlashCommand
from createDB import checkDB
import json

try:
    # Ouvre le fichier de configuration
    with open('../Configuration/conf.json', mode='r') as confFile:
        configuration = json.load(confFile)
    
    # Récupère le chemin du fichier de base de donnée
    sourceDb = Path(str(configuration['configuration']['emplacement_bd']))
    # Récupère les ids des serveurs
    guild_ids = configuration["configuration"]["id_guilds"]
    if not guild_ids:
        print("[ WARNING ] Vous n'avez pas spécifié de guilds, si ceci est votre premier lancement du bot, les commandes pourront prendre jusqu'à 1 heure avant d'apparaître.")
    # Vient vérifier la présence du fichier de BD. Si il est absent, il l'auto-génère 
    checkDB(sourceDb)
    # Récupère le token Discord
    TOKEN = configuration['configuration']['token']
    # Configure le client
    client = commands.Bot(command_prefix = configuration['configuration']['prefix_bot'], intents=discord.Intents.all())
    client.remove_command('help')
    slash = SlashCommand(client, sync_commands=True)
except Exception as e:
    print(f"[ ERROR ] Une erreure est survenue: {e}")
    print("[ INFO ] Assurez-vous d'avoir complété le fichier de configuration: ./Configuration/conf.json")
    print(f"[ INFO ] Assurez-vous que votre Token Discord est valide: {configuration['_instructions']}")
    print("[ INFO ] Assurez-vous que votre bot possède les 'Privileged Gateway Intents'. (Sur la page où vous récupérez le token du bot, Activez `Presence Intent` et `Server Members Intent`)")
    print(f"[ INFO ] Assurez-vous que `{configuration['configuration']['emplacement_bd']}` est accessible par le bot et mène bien au .db de la base de données")