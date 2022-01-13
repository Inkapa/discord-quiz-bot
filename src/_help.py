# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 14:48:12 2021

@author: Liam
"""

from init import guild_ids
from discord_slash import cog_ext
from discord.ext import commands
import discord
import random
from datetime import datetime
from discord_slash.utils.manage_commands import create_choice, create_option


options = [create_option(name="aidesup", description="Si vous voulez plus d'info sur une commande en particulier", option_type=3, required=False, choices=[
            create_choice(name='createquiz', value='createquiz'),
            create_choice(name='addquestion', value='addquestion'),
            create_choice(name='getquizs', value='getquizs'),
            create_choice(name='recap', value='recap'),
            create_choice(name='launchquiz', value='launchquiz'),
            create_choice(name='getresults', value='getresults'),
            create_choice(name='viewresult', value='viewresult'),
            create_choice(name='leaderboard', value='leaderboard'), 
            create_choice(name='reset', value='reset')])]

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_slash(name="help", description="L'aide pour utiliser le super bot.", guild_ids = guild_ids, options=options)
    async def help(self, ctx, option = None):
        if option is None:
            embed = discord.Embed(title=":pencil: Voici la liste des commandes disponibles ! :pencil:", description="\u200b", colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/help", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":one: - /addquestion", value="Permet de rajouter une question à un quiz à l'aide de son identifiant ou de créer un nouveau quiz si aucun identifiant de quiz n'est spécifié.", inline=False)
            embed.add_field(name=":two: - /createquiz", value="Permet de créer un nouveau quiz.", inline=False)
            embed.add_field(name=":three: - /getquizs", value="Permet d'afficher les quiz créés par l'utilisateur ou de récupérer l'entièreté disponibles dans la bd.", inline=False)
            embed.add_field(name=":four: - /getresults", value="Permet d'afficher les résultats globaux d'une game de quiz.", inline=False)
            embed.add_field(name=":five: - /launchquiz", value="Permet de lancer une game de quiz.", inline=False)
            embed.add_field(name=":six: - /leaderboard", value="Permet d'afficher le classement des participants du serveur.", inline=False)
            embed.add_field(name=":seven: - /viewresult", value="Permet d'afficher les résultats personnels d'une game.", inline=False)
            embed.add_field(name=":eight: - /recap", value="Permet d'afficher un récapitulatif d'un quiz.", inline=False)
            embed.add_field(name=":nine: - /reset", value="Permet de reinitialiser les score et le classement des joueurs du serveur.", inline=False)

        elif option == "createquiz":
            embed = discord.Embed(title=":pencil: Comment créer un quiz :pencil:",colour=random.randint(0, 0xFFFFFF),description="```/createQuiz [titre] [points]```", timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/createquiz", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  Titre", value="Nom que l'on veut donner au quiz.", inline=False)
            embed.add_field(name=":arrow_right:  Points *[Facultatif] [Défaut = 10]*", value="Nombre de points que vaut le quiz (divisé par le nombre de question) (entre 1 et 100).", inline=False)
            embed.set_footer(text="⚠️ Nécessite le rôle de gestion de quiz!")

        elif option == "addquestion":
            embed = discord.Embed(title=":pencil: Comment ajouter une question à son quiz :pencil:",colour=random.randint(0, 0xFFFFFF),description="```/addQuestion [titre] [reponse1] [reponse2] [reponse3] [reponse4] [idquiz]```", timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/addquestion", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  Titre", value="Titre de la question.", inline=False) 
            embed.add_field(name=":arrow_right:  reponse1", value="Intitulé de la réponse 1.", inline=False)
            embed.add_field(name=":arrow_right:  reponse2", value="Intitulé de la réponse 2.", inline=False)
            embed.add_field(name=":arrow_right:  reponse3 *[Facultatif]*", value="Intitulé de la réponse 3.", inline=False)
            embed.add_field(name=":arrow_right:  reponse4 *[Facultatif]*", value="Intitulé de la réponse 4.", inline=False)
            embed.add_field(name=":arrow_right:  idquiz *[Facultatif]*", value="Identifiant du quiz auquel ajouter la question (si aucun identifiant n'est spécifié, un nouveau quiz sera créé).", inline=False)
            embed.set_footer(text="⚠️ Nécessite le rôle de gestion de quiz!")

        elif option == "launchquiz":
            embed = discord.Embed(title=":pencil: Lancer une game d'un quiz :pencil:",description="```/launchQuiz [idquiz] [Durée Attente] [Durée Réponse] [multiplicateur]```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/launchQuiz", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  idquiz", value="Identifiant du quiz dont on veut lancer une partie", inline=False)
            embed.add_field(name=":arrow_right:  durée_attente *[Facultatif] [Défaut = 30s]*", value="Durée d'attente pour s'inscrire au quiz avant le début de la partie (entre 30 et 36000 secondes).", inline=False)
            embed.add_field(name=":arrow_right:  durée_réponse *[Facultatif] [Défaut = 30s]*", value="durée disponible pour répondre à chaque question (entre 15 et 3600 secondes).", inline=False)
            embed.add_field(name=":arrow_right:  multiplicateur *[Facultatif] [Défaut = 1]*", value="Tel un coefficient permet de multiplier le nombre de points que rapporte le quiz.", inline=False)
            embed.set_footer(text="⚠️ Nécessite le rôle de gestion de quiz!")


        elif option == "getresults":
            embed = discord.Embed(title=":pencil: Récupérer les résultats globaux d'une game :pencil:",description="```/getresults [id_game]```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/getresults", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  id_game", value="Identifiant de la game dont on veut récupérer les résultats.", inline=False)

        elif option == "leaderboard":
            embed = discord.Embed(title=":pencil: Récupérer le classement des meilleurs joueurs du serveur :pencil:",description="```/leaderboard```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/leaderboard", icon_url=ctx.author.avatar_url)

        elif option == "viewresult":
            embed = discord.Embed(title=":pencil: Permet de votre résultat pour une game :pencil:",description="```/viewresult [id_game]```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/viewresult", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  id_game", value="Identifiant de la game sur laquelle on veut vérifier son résultat.", inline=False)

        elif option == "getquizs":
            embed = discord.Embed(title=":pencil: Récupérer une liste des quizs disponibles :pencil:",description="```/getquizs [personal]```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/getquizs", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  personal *[Facultatif] [Defaut = False]*", value="Déclare si l'on veut récupérer la liste des quiz créé par soi-même ou la liste des quiz disponibles dans la BD.", inline=False)
            embed.set_footer(text="⚠️ Nécessite le rôle de gestion de quiz!")

        elif option == "reset":
            embed = discord.Embed(title=":pencil: Reinitialise les scores et le classement du serveur :pencil:",description="```/reset```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/reset", icon_url=ctx.author.avatar_url)
            embed.set_footer(text="⚠️ Nécessite le rôle de gestion de quiz!")
            
        elif option == "recap":
            embed = discord.Embed(title=":pencil: Affiche un récapitulatif d'un quiz :pencil:",description="```/recap [idquiz]```",colour=random.randint(0, 0xFFFFFF), timestamp=datetime.today())
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/847085222365233182/847842597804441600/Quiz.png')
            embed.set_author(name="/recap", icon_url=ctx.author.avatar_url)
            embed.add_field(name=":arrow_right:  idquiz", value="Identifiant du quiz dont on veut afficher le récapitulatif.", inline=False)
            embed.set_footer(text="⚠️ Nécessite le rôle de gestion de quiz!")

        await ctx.send(embed=embed, hidden=True)
