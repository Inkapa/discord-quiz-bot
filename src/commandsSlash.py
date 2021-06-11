# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 15:45:21 2021

@author: Liam
"""

import aiosqlite
import discord
from datetime import datetime
import sqlite3
import math
from init import sourceDb, guild_ids, permission
from database import Utilisateur, Quiz, Instance, Reponse, Statistiques
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
import asyncio
import time
from utils import createEmbed, quizEmbed, recapEmbed


class Commandes(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        

    @cog_ext.cog_slash(name="addquestion",
                 guild_ids=guild_ids,
                 description="Ajoute une question à un quiz existant si spécifié ou créé un nouveau quiz pour la question.",
                 permissions=permission,
                 options=[
                   create_option(
                     name="titre",
                     description="Titre de la question",
                     option_type=3,
                     required=True
                   ),
                   create_option(
                     name="reponse1",
                     description="Première reponse possible",
                     option_type=3,
                     required=True
                   ),
                   create_option(
                     name="reponse2",
                     description="Deuxième reponse possible",
                     option_type=3,
                     required=True
                   ),
                   create_option(
                     name="reponse3",
                     description="Troisième reponse possible",
                     option_type=3,
                     required=False
                   ),
                   create_option(
                     name="reponse4",
                     description="Quatrième reponse possible",
                     option_type=3,
                     required=False
                   ),
                   create_option(
                     name="idquiz",
                     description="Identifiant du quiz auquel on rajoute la question",
                     option_type=4,
                     required=False
                   )
                 ])
    async def addquestion(self, ctx, titre: str, reponse1: str, reponse2: str, reponse3: str = None, reponse4: str = None, idquiz: int = None):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            
            reponses = [reponse for reponse in [reponse1, reponse2, reponse3, reponse4] if reponse is not None and type(reponse) == str]
            keycaps = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                
                
            embed = discord.Embed(title=":pencil: Récapitulatif de la question :pencil:", colour=discord.Colour(0x42a010), description="\u200b​", timestamp=datetime.today())
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
            embed.set_author(name="En cours de création", icon_url=ctx.author.avatar_url)
            embed.set_footer(text="Appuyer sur ❌ pour annuler la question", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
            embed.add_field(name=":book: __La Question__:", value=f"**“ {titre} ”**", inline=False)
            embed.add_field(name=":white_check_mark: __Les reponses possibles__:", value="\u200b​", inline=False)
             
    
            for i, reponse in enumerate(reponses):
                embed.add_field(name=keycaps[i] + " - " + str(reponse), value="\u200b", inline=False)
            message = await ctx.send(embed=embed)
            for i, reponse in enumerate(reponses):
                await message.add_reaction(keycaps[i])
            await message.add_reaction('❌')
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout = 15.0, check = lambda reaction, user: user.id == ctx.author.id and reaction.message.id == message.id and (str(reaction.emoji) in keycaps or str(reaction.emoji) == '❌'))
                
                await message.clear_reactions()
    
                if str(reaction.emoji) == '❌':
                    await message.edit(embed=await createEmbed("annulé", ctx))
                    
                elif str(reaction.emoji) in keycaps:
                    estValide = [1 if keycaps[i] == reaction.emoji else 0 for i, reponse in enumerate(reponses)]
                    
                    
                    if idquiz is None:
                        quiz = await Quiz.create(titre, 10, ctx.author.id, db)
                        question = await quiz.addQuestion(titre)
                        for i, reponse in enumerate(reponses):
                            
                            await question.addChoix(reponse, estValide[i])
                        bonneRéponse = await question.getBonneReponse()
                        
                        await message.edit(embed=await createEmbed("success",ctx, quiz,question,bonneRéponse))
                        
                    else:
                        
                        
                        quiz = await Quiz.get(idquiz, db)
                        if quiz:
                            creator = await quiz.getCreator(ctx.guild.id)
                            if await creator.getIdDiscord() != ctx.author.id:
                                await message.edit(embed=await createEmbed("creator", ctx))       
                            else:
                                if await quiz.getNbQuestions() >= 4:
                                    await message.edit(embed=await createEmbed("maxQuestions", ctx))    
                                else:
                                    question = await quiz.addQuestion(titre)
                                    for i, reponse in enumerate(reponses):
                                        
                                        await question.addChoix(reponse, estValide[i])
                                    bonneRéponse = await question.getBonneReponse()
                                    
                                    await message.edit(embed=await createEmbed("success", ctx, quiz,question,bonneRéponse))
                        else:
                            await message.edit(embed=await createEmbed("incorrecte", ctx))                        
                    
            except Exception as e:
                print(e)
                await ctx.send("<a:error:804691277010567189> Tu n'as pas spécifié la bonne reponse, la question a été annulée")
                await message.edit(embed=await createEmbed("annulé", ctx), hidden = True)   
            
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------            
                    
    @cog_ext.cog_slash(name="createquiz",
                 guild_ids=guild_ids,
                 description="Permet de créer un nouveau quiz. N'oubliez pas d'ajouter des questions avec /addQuestion",
                 permissions=permission,
                 options=[
                   create_option(
                     name="titre",
                     description="Titre du quiz",
                     option_type=3,
                     required=True
                   ),
                   create_option(
                     name="points",
                     description="Nombre de points que vaut le quiz",
                     option_type=4,
                     required=False
                   )
                 ])        
    async def createquiz(self, ctx, titre: str, points: int = 10):
                
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            points = max(min(points, 100),1)
            quiz = await Quiz.create(titre, points, ctx.author.id, db)
            await ctx.send(embed= await createEmbed("createQuiz", ctx, quiz), hidden=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
            
    @cog_ext.cog_slash(name="leaderboard",
                 guild_ids=guild_ids,
                 description="Permet d'afficher le classement des meilleurs joueurs en termes de points.")     
    async def leaderboard(self, ctx):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            
            keycaps = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
            user = await Utilisateur.get(ctx.author.id, ctx.guild.id, db)
            stats = await user.getStatistiques()
            position = await user.getCurrentPosition()
            points = round(await stats.getScoreTotal(), 2)
            embed = discord.Embed(title=":trophy: Voici le top 10 des meilleurs joueurs :trophy:", colour=discord.Colour(0x42a010), description="*Classé en termes de points totaux sur le serveur*​", timestamp=datetime.today())
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
            embed.set_author(name="Votre place: " + (str(position) + 'er' if position == 1 else str(position) +'ème'), icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f"Vous avez {points} points", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
    
            
            leaderboard = await Statistiques.getLeaderboard(ctx.guild.id, db)
            for i, ranker in enumerate(leaderboard):
                embed.add_field(name=keycaps[i] + " - " + str(await ranker[0].getName()), value=str(round(await ranker[1].getScoreTotal(), 2)) + " points", inline=False)
            await ctx.send(embed = embed, hidden=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

    @cog_ext.cog_slash(name="getquizs",
                 guild_ids=guild_ids,
                 description="Permet de récupérers tout les quizs disponibles sur la base de données.",
                 permissions=permission,
                 options=[
                   create_option(
                     name="personal",
                     description="Limiter la recherche des quizs à ceux que vous avez créés.",
                     option_type=5,
                     required=False
                   )])   
    async def getquizs(self, ctx, personal: bool = True):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row    
            utilisateur = await Utilisateur.get(ctx.author.id, ctx.guild.id, db)
            if personal:
                quizCount = await Quiz.getCount(db, ctx.author.id)   
            else:
                quizCount = await Quiz.getCount(db)
                
            pages = math.ceil(quizCount/10)
            page = 1
            offset = 0
            reaction = None
            embed = await quizEmbed(ctx, personal, quizCount, utilisateur, db, 1, pages)
            message = await ctx.send(embed=embed)
            if page < pages:
                await message.add_reaction('▶')
            
                while True:
                    if str(reaction) == '◀' and page > 1:
                        page -= 1
                        offset -= 10
                        if page == 1:
                            await message.remove_reaction('◀', self.client.user)
                        if page == pages-1:
                            await message.add_reaction('▶')
                        embed = await quizEmbed(ctx, personal, quizCount, utilisateur, db, page, pages, offset)
                        await message.edit(embed=embed)
                        
                    elif str(reaction) == '▶' and page < pages:
                        page += 1
                        offset += 10
                        if page == pages:
                            await message.remove_reaction('▶', self.client.user)
                        if page == 2:
                            await message.remove_reaction('▶', self.client.user)
                            await message.add_reaction('◀')
                            await message.add_reaction('▶')
                        embed = await quizEmbed(ctx, personal, quizCount, utilisateur, db, page, pages, offset)
                        await message.edit(embed=embed)
                                    
                    try:
                        reaction, discordUser = await self.client.wait_for('reaction_add', timeout = 10.0, check = lambda reaction, discordUser: discordUser.id == ctx.author.id and reaction.message.id == message.id and str(reaction.emoji) in ['◀', '▶'])
                        await message.remove_reaction(reaction, discordUser)
                    except:
                        await message.clear_reactions()
                        break
                
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                        
                
    @cog_ext.cog_slash(name="getresults",
         guild_ids=guild_ids,
         description="Permet de récuperer la moyenne et le classement d'une game.",
         options=[
           create_option(
             name="id_game",
             description="L'identifiant unique de la game.",
             option_type=4,
             required=True
           )])   
    async def getresults(self, ctx, id_game: int):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row    
            
            game = await Instance.get(id_game, db)
            if game:
                if await game.getDateFin():
                    keycaps = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
                    moyenne, nbPoints = await game.getMoyenne(False, True)
                    quiz = await game.getQuiz()
                    nbQuestions = await quiz.getNbQuestions()
                    pointsParQ = await quiz.getPoints()*await game.getMultiplicateur()/nbQuestions
                    classement = await game.getClassement()
                    reponseTrie = await game.getReponsesTrie()
                    dateDébut = await game.getDateDeb(True)
                    DateFin = await game.getDateFin(True)
                    
                    embed = discord.Embed(title=f":chart_with_upwards_trend: Instance {id_game} du Quiz: " + await quiz.getTitre() , colour=discord.Colour(0x42a010), description=f"La moyenne pour cette instance de quiz est de: **{round(moyenne,2)}/{nbPoints}**​", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Nombre de participants: " + str(await game.getNbParticipants()), icon_url=ctx.author.avatar_url)
                    embed.set_footer(text=f"Vous pouvez utilisez /viewResult {id_game} pour voir votre résultat", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
                    if len(reponseTrie) > 1:
                        mieuxReussi = reponseTrie[0]
                        moinsReussi = reponseTrie[-1]
                        embed.add_field(name=":white_check_mark: Question la mieux réussi:", value='**' + await mieuxReussi[0].getTitre() + "** avec " + str(mieuxReussi[1]) + " bonnes réponses", inline=False)  
                        embed.add_field(name=":negative_squared_cross_mark: Question la moins réussi:", value='**' + await moinsReussi[0].getTitre() + "** avec " + str(moinsReussi[1]) + " bonnes réponses", inline=False)  
                    embed.add_field(name=":calendar: Date de la game", value=f"Début : {dateDébut}\nFin: " + DateFin if DateFin else "Le quiz n'est pas terminé", inline=False)  
                    embed.add_field(name=":trophy: Classement des 10 meilleurs participants", value="\u200b", inline=False)
                    for i, (ranker, nbBnReponse) in enumerate(classement):
                        points = nbBnReponse*pointsParQ
                        embed.add_field(name=keycaps[i] + " - " + str(await ranker.getName()), value=f"{nbBnReponse}/{nbQuestions} bonnes réponses. Soit {round(points,2)} points.", inline=False)
                    await ctx.send(embed = embed, hidden = True)
                else:
                    embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Veuillez attendre la fin de la partie d'id {id_game}```", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed, hidden = True)                       
            else:
                embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Aucun résultat n'a été trouvé pour une instance d'id {id_game}```", timestamp=datetime.today())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed, hidden=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

    @cog_ext.cog_slash(name="viewresult",
         guild_ids=guild_ids,
         description="Permet de récuperer votre résultat pour une game.",
         options=[
           create_option(
             name="id_game",
             description="L'identifiant unique de la game.",
             option_type=4,
             required=True
           )])       
    async def viewresult(self, ctx, id_game: int):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row 
            
            user = await Utilisateur.get(ctx.author.id, ctx.guild.id, db)
            resultats = await user.getResultats(id_game)
            instance = await Instance.get(id_game, db)
            keycaps = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
            
            if resultats and instance:
                if await instance.getDateFin():
                    quiz = await instance.getQuiz()
                    nbQuestions = await quiz.getNbQuestions()
                    pointsParQ = await quiz.getPoints()*await instance.getMultiplicateur()/nbQuestions
                    nbBnReponse = await instance.getNbCorrectes(ctx.author.id)
                    points = nbBnReponse*pointsParQ
                    moyenne, nbPoints = await instance.getMoyenne(False, True)
                    classement = await user.getCurrentPosition(id_game)
                    embed = discord.Embed(title=f":chart_with_upwards_trend: Instance {id_game} du Quiz: " + await quiz.getTitre() , colour=discord.Colour(0x42a010), description=f"Vous avez eu **{nbBnReponse}/{nbQuestions}** bonnes réponses​", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Nombre de participants: " + str(await instance.getNbParticipants()), icon_url=ctx.author.avatar_url)
                    embed.set_footer(text=f"La moyenne est de {round(moyenne,2)}/{nbPoints}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")         
                    embed.add_field(name=":trophy: Classement:", value=f"Vous êtes **{classement}" + ("er" if classement == 1 else "ème") + f"** du classement avec un total de **{round(points, 2)} points** *(sur {nbPoints})*\n", inline=False)  
                    embed.add_field(name=":pencil: Récapitulatif des questions:", value="\u200b", inline=False)  
                    
                    for i, (question, estCorrecte, choix) in enumerate(resultats):       
                        bonneReponse = await question.getBonneReponse()
                        titre = await bonneReponse.getTitre()
                        if choix:
                            titreChoix = await choix.getTitre()
                        else:
                            titreChoix = "Vous n'avez pas répondu à cette question"
                        embed.add_field(name=keycaps[i] + " - " + await question.getTitre(), value=f"⠀⠀⠀‎:ballot_box_with_check: **Réponse attendue:** {titre}\n⠀⠀⠀‎" + (":white_check_mark:" if estCorrecte else (":negative_squared_cross_mark:" if choix else ":x:")) + f" **Votre réponse: ** {titreChoix}", inline=False)
                    await ctx.send(embed=embed, hidden=True)
                else:
                    embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Veuillez attendre la fin de la partie d'id {id_game}```", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed, hidden=True)                    
            else:
                embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Aucun résultat n'a été trouvé pour votre compte sur l'instance d'id {id_game}```", timestamp=datetime.today())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed, hidden=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
                
    @cog_ext.cog_slash(name="launchquiz", 
        description="Commande pour lancer une game d'un quiz !",
        permissions=permission,
        options=[
            create_option(
              name="idquiz",
              description="L'identifiant du quiz a lancer. Utilisez la commande /getquizs pour retrouver les identifiants.",
              option_type=4,
              required=True
            ),
            create_option(
              name="durée_attente",
              description="La durée (en secondes) que le bot attendera pour des réactions avant de lancer la game.",
              option_type=4,
              required=False
            ),
            create_option(
              name="durée_réponse",
              description="La durée (en secondes) que possédera un participant pour chaque question.",
              option_type=4,
              required=False
            ),
            create_option(
              name="multiplicateur",
              description="Tel un coefficient, vient multiplier le nombre de points d'un quiz par le multiplicateur.",
              option_type=4,
              required=False
            )], 
        guild_ids=guild_ids)
    async def launchquiz(self, ctx, idquiz: int, durée_attente: int = 30, durée_réponse: int = 30, multiplicateur: int = 1):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            
            
            durée_attente = max(min(durée_attente, 36000), 30)
            durée_réponse = max(min(durée_réponse, 3600), 15)
            multiplicateur = max(min(multiplicateur, 100), 1)
            quiz = await Quiz.get(idquiz, db)
            if quiz:
                quizQuestions = await quiz.getNbQuestions()
                
                if quizQuestions > 0:

                    createur = await quiz.getCreator(ctx.guild.id)
                    createurId = await createur.getIdDiscord()
                    creatorNom = await createur.getName()
                    creator = discord.utils.get(self.client.get_all_members(), id=createurId)
                    quizName = await quiz.getTitre()
                    
                    quizPoints = await quiz.getPoints()*multiplicateur
                    embed = discord.Embed(title=f":books: Participation au quiz : {quizName}", description=f"Une game du quiz **{quizName}** va bientôt commencer.", color=0x50E3C2, timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name=f"Game lancée par {ctx.author.name}#{ctx.author.discriminator}", icon_url= ctx.author.avatar_url)
                    embed.add_field(name=":information_source: - Informations", value=f'Le quiz contient **{quizQuestions}** question(s) pour un total de **{quizPoints}** point(s).', inline=False)
                    embed.add_field(name=":ballot_box: - Comment participer", value="Appuyer sur la réaction :ballot_box: pour participer, une fois le temps d'attente écoulé un channel privé vous sera généré")
                    embed.add_field(name=":alarm_clock: - Temps", value=f'Vous avez **{time.strftime("%H heures %M minutes et %S secondes" if durée_attente >= 3600 else ("%M minutes et %S secondes" if durée_attente >= 120 else ("%M minute et %S secondes" if durée_attente >= 60 else "%S secondes")), time.gmtime(durée_attente))}** avant le lancement du test.', inline=False)
                    embed.set_footer(text=f"Quiz créé par {creatorNom}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")         
    
                    message = await ctx.send(embed=embed)
                    await message.add_reaction(emoji="🗳️")
                    await asyncio.sleep(durée_attente)
                    message = await ctx.channel.fetch_message(message.id)
                    reaction = [reaction for reaction in message.reactions if reaction.emoji == "🗳️"][0]
                    users = await reaction.users().flatten()
                    await message.clear_reactions()
                    if len(users) > 1:
                        instance = await Instance.create(idquiz, db, ctx.guild.id, multiplicateur)
                        if not instance:
                            embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description="```diff\n- La création de l'instance a échoué```", timestamp=datetime.today())
                            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                            embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                            await ctx.send(embed=embed)
                        else:
                            idInst = await instance.getIdInst()

                            embed = discord.Embed(title=f":books: Participation au quiz : {quizName}", description="", color=0xff4c5b, timestamp=datetime.today())
                            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")

                            embed.set_author(name=f"Game lancée par {ctx.author.name}#{ctx.author.discriminator}", icon_url= ctx.author.avatar_url)
                            embed.add_field(name=":lock: - Le quiz est maintenant fermé", value="Le temps d'attente est écoulé. Le quiz est maintenant lancé.\nCherchez un channel à votre nom dans les channels du serveur et répondez aux questions à l'aide des reactions à l'intérieur de celui-ci.")
                            embed.set_footer(text=f"Quiz créé par {creatorNom}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")         
            
                            await message.edit(embed=embed)
                            newCat = await ctx.guild.create_category(name=quizName)
                            
                            embed = discord.Embed(title="Le quiz va bientôt commencer!", colour=discord.Colour(0x4A90E2), description="Encore quelques instants. Le bot ouvre les channels aux participants...", timestamp=datetime.today())
                            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                            embed.set_footer(text=f"Quiz créé par {creatorNom}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
                            tasks = []
                            
                            for user in users:
                                if not user.bot:
                                    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                                                user: discord.PermissionOverwrite(read_messages = True)}
                                    channel = await newCat.create_text_channel(name=f"{user.name}-{user.discriminator}", overwrites=overwrites)
                                    answerMessage = await channel.send(user.mention, embed=embed)
                                    tasks.append(self.envoyerQuestion(channel, instance, quiz, creator, user, answerMessage, durée_réponse)) 
            
                            await asyncio.gather(*tasks)
                            
                            await instance.setDateFin()
                        
                            keycaps = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
                            moyenne, nbPoints = await instance.getMoyenne(False, True)
                            pointsParQ = quizPoints/quizQuestions
                            classement = await instance.getClassement()
                            reponseTrie = await instance.getReponsesTrie()
                            dateDébut = await instance.getDateDeb(True)
                            dateFin = await instance.getDateFin(True)
                            
                            embed = discord.Embed(title=f":chart_with_upwards_trend: Instance {idInst} du Quiz: {quizName}", description=f"La moyenne pour cette instance de quiz est de: **{round(moyenne,2)}/{nbPoints}**​", colour=discord.Colour(0x42a010), timestamp=datetime.today())
                            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                            embed.set_author(name="Nombre de participants: " + str(await instance.getNbParticipants()), icon_url=ctx.author.avatar_url)
                            embed.set_footer(text=f"Vous pouvez utilisez /viewResult {idInst} pour voir votre résultat", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
                            if len(reponseTrie) > 1:
                                mieuxReussi = reponseTrie[0]
                                moinsReussi = reponseTrie[-1]
                                embed.add_field(name=":white_check_mark: Question la mieux réussi:", value='**' + await mieuxReussi[0].getTitre() + "** avec " + str(mieuxReussi[1]) + " bonnes réponses", inline=False)  
                                embed.add_field(name=":negative_squared_cross_mark: Question la moins réussi:", value='**' + await moinsReussi[0].getTitre() + "** avec " + str(moinsReussi[1]) + " bonnes réponses", inline=False)  
                            embed.add_field(name=":calendar: Date de la game", value=f"Début : {dateDébut}\nFin: " + dateFin if dateFin else "Le quiz n'est pas terminé", inline=False)  
                            embed.add_field(name=":trophy: Classement des 10 meilleurs participants", value="\u200b", inline=False)
                            for i, (ranker, nbBnReponse) in enumerate(classement):
                                points = nbBnReponse*pointsParQ
                                embed.add_field(name=keycaps[i] + " - " + str(await ranker.getName()), value=f"{nbBnReponse}/{quizQuestions} bonnes réponses. Soit {round(points,2)} points.", inline=False)
                            
                            await message.edit(embed=embed)
                            await asyncio.sleep(3)
                            await newCat.delete()
                    else:
                        embed = discord.Embed(title=f":books: Participation au quiz : {quizName}", description="", color=0xc20010, timestamp=datetime.today())
                        embed.set_author(name=f"Game lancée par {ctx.author.name}#{ctx.author.discriminator}", icon_url= ctx.author.avatar_url)
                        embed.add_field(name=":x: Game annulé", value="La game n'a pas reçu de participations dans le temps impartie. La game a été annulée")
                        embed.set_footer(text=f"Quiz créé par {creatorNom}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")          
                        await message.edit(embed=embed)

                else:
                    embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description="```diff\n- Vous ne pouvez pas lancer un quiz qui n'a pas de questions.\n\n- Faites /addQuestion pour ajouter au moins 1 question à ce quiz ou utiliser /getQuizs pour avoir une liste des quizs disponibles.```", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed, hidden=True)
            else:
                embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Aucun Quiz d'id {idquiz} n'a été trouvé```", timestamp=datetime.today())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed, hidden=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

    async def envoyerQuestion(self, channel, instance, quiz, creator, user, message, durée_réponse):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            
            reactions = ["1️⃣","2️⃣","3️⃣","4️⃣"]
            await Utilisateur.get(user.id, channel.guild.id, db)

            for question in await quiz.getQuestions():
                choix = await question.getChoix()
                nbChoix = len(choix)
                embed = discord.Embed(title=":pencil: "+ str(await quiz.getTitre()), description=f'''Vous avez **{time.strftime("%H heures %M minutes et %S secondes" if durée_réponse >= 3600 else ("%M minutes et %S secondes" if durée_réponse >= 120 else ("%M minute et %S secondes" if durée_réponse >= 60 else "%S secondes")), time.gmtime(durée_réponse))}** pour répondre à chaque question à l'aide des réactions sous ce message.''', color=0x0011ff, timestamp=datetime.today())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar_url)
                embed.set_footer(text=f"Utilisez les réactions de 1️⃣ à {reactions[nbChoix-1]} pour choisir votre réponse", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
                embed.add_field(name=":book: "+ await question.getTitre()+ " :book:", value = "\u200b")

                for i,choix in enumerate(choix):
                    titreChoix = await choix.getTitre()
                    embed.add_field(name=f"{reactions[i]} - {titreChoix}", value="\u200b", inline=False)
                
                await message.edit(embed=embed)

                reactPossible = []
                for i in range(nbChoix):
                    await message.add_reaction(emoji=reactions[i])
                    reactPossible.append(reactions[i])

                try:
                    reaction, u = await self.client.wait_for('reaction_add', timeout=durée_réponse, check=lambda reaction, discordUser: discordUser.id == user.id and reaction.message.id == message.id and str(reaction.emoji) in reactPossible)
                    if reaction.emoji == "1️⃣":
                        await Reponse.create(await instance.getIdInst(), await question.getIdQuestion(), 1, user.id, db)
                    if reaction.emoji == "2️⃣":
                        await Reponse.create(await instance.getIdInst(), await question.getIdQuestion(), 2, user.id, db)
                    if reaction.emoji == "3️⃣":
                        await Reponse.create(await instance.getIdInst(), await question.getIdQuestion(), 3, user.id, db)
                    if reaction.emoji == "4️⃣":
                        await Reponse.create(await instance.getIdInst(), await question.getIdQuestion(), 4, user.id, db)

                except asyncio.TimeoutError:
                    await Reponse.create(await instance.getIdInst(), await question.getIdQuestion(), 0, user.id, db)
                await message.clear_reactions()

        embed = discord.Embed(title="Quiz terminé!", colour=discord.Colour(0xF5A623), description="Le quiz est maintenant terminé. Ce channel sera supprimé dans quelques instants", timestamp=datetime.today())
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
        embed.set_footer(text=f"Quiz créé par {creator.name}#{creator.discriminator}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
        await message.edit(embed=embed)
        await asyncio.sleep(5)
        await channel.delete()
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

    @cog_ext.cog_slash(name="reset",
         guild_ids=guild_ids,
         description="Permet de reinitialiser les scores et le leaderboard du serveur.",
         permissions=permission)
    async def reset(self, ctx):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            
            await Statistiques.clearLeaderboard(ctx.guild.id, db)
            await ctx.send(":white_check_mark:", hidden=True)
            
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
            
    @cog_ext.cog_slash(name="recap",
                 guild_ids=guild_ids,
                 description="Permet de faire un récapitulatif d'un quiz.",
                 permissions=permission,
                 options=[
                   create_option(
                     name="idquiz",
                     description="Id du quiz dont on veut faire le récapitulatif.",
                     option_type=4,
                     required=True
                   )])   
    async def recap(self, ctx, idQuiz: int):
        async with aiosqlite.connect(sourceDb) as db:
            db.row_factory = sqlite3.Row
            
            quiz = await Quiz.get(idQuiz, db)
            
            if quiz:
                
                pages = await quiz.getNbQuestions()
                
                if pages > 0:
                    page = 1
                    
                    reaction = None
                    
                    embed = await recapEmbed(ctx, quiz, page, pages, db)
                    message = await ctx.send(embed=embed)
                    
                    if page < pages:
                        await message.add_reaction('▶')
                    
                        while True:
                            if str(reaction) == '◀' and page > 1:
                                page -= 1
                                if page == 1:
                                    await message.remove_reaction('◀', self.client.user)
                                if page == pages-1:
                                    await message.add_reaction('▶')
                                embed = await recapEmbed(ctx, quiz, page, pages, db)
                                await message.edit(embed=embed)
                                
                            elif str(reaction) == '▶' and page < pages:
                                page += 1
                                if page == pages:
                                    await message.remove_reaction('▶', self.client.user)
                                if page == 2:
                                    await message.remove_reaction('▶', self.client.user)
                                    await message.add_reaction('◀')
                                    await message.add_reaction('▶')
                                    
                                embed = await recapEmbed(ctx, quiz, page, pages, db)
                                await message.edit(embed=embed)
                                            
                            try:
                                reaction, discordUser = await self.client.wait_for('reaction_add', timeout = 20.0, check = lambda reaction, discordUser: discordUser.id == ctx.author.id and reaction.message.id == message.id and str(reaction.emoji) in ['◀', '▶'])
                                await message.remove_reaction(reaction, discordUser)
                            except:
                                await message.clear_reactions()
                                break
                else:
                    embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Le quiz d'id {idQuiz} n'a aucune question```", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed, hidden=True)                        
            else:
                embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description=f"```diff\n- Aucun Quiz d'id {idQuiz} n'a été trouvé```", timestamp=datetime.today())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                embed.set_author(name="Une erreure est survenue", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed, hidden=True)