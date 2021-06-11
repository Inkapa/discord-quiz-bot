# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 15:46:29 2021

@author: Liam
"""

import re
import discord
from discord_slash import SlashContext
from datetime import datetime
from database import Quiz, Question, Choix, Utilisateur
import aiosqlite 

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
async def createEmbed(desc: str, ctx: SlashContext = None, quiz: Quiz = None, question: Question = None, bonneRéponse: Choix = None) -> discord.Embed:
    """Fonction qui permet la création d'embed Discord pour un Question d'un quiz
    
    Args:
        desc (str): Identifiant du type d'embed que l'on veut sous forme de str
        ctx (SlashContext): Contexte de la commande
        (default None)
        quiz (Quiz): Instance de Quiz
        (default None)
        question (Question): Instance de question
        (default None)
        bonneRéponse (Choix): Instance de Choix représentant la bonne réponse de Question
        (default None)
        
    Returns:
        discord.Embed: Embed Discord contenant les informations voulues
        
    """
    if desc in ["success", "createQuiz"]:
        if question:
            descriptions = {
            "success":'```json\n"\nLa question a été créée avec succès.\nId du Quiz: ' + str(await quiz.getIdQuiz()) + '\nTitre de la question: ' + re.sub("```", "'''",str(await question.getTitre())) + '\nBonne réponse: ' + re.sub("```", "'''",str(await bonneRéponse.getTitre())) + '\n"```',
            }
        else:
            descriptions = {
            "createQuiz":'```json\n"\nLe quiz a été créé avec succès.\nId du Quiz: '  + str(await quiz.getIdQuiz()) + '\nTitre du Quiz: ' + re.sub("```", "'''",str(await quiz.getTitre())) + '\nPoints: ' + str(await quiz.getPoints())+ '\n"```'
            }
        embed = discord.Embed(title=":pencil: Récapitulatif de la question :pencil:", colour=discord.Colour(0x42a010), description=descriptions[desc], timestamp=datetime.today())
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
        embed.set_author(name="Id du Quiz: " + str(await quiz.getIdQuiz()), icon_url=ctx.author.avatar_url)
    
        
    else:
        descriptions = {
        "annulé":"```diff\n- Question annulée```​",
        "incorrecte":"```diff\n- L'id du quiz est incorrecte.```​",
        "maxQuestions":"```diff\n- Il ne peut pas y avoir plus de 4 questions dans un quiz.```​",
        "creator":"```diff\n- Seul le créateur du quiz peut ajouter des questions à son quiz.```​",
        }
        embed = discord.Embed(title=":pencil: Récapitulatif de la question :pencil:", colour=discord.Colour(0xFF001C), description=descriptions[desc], timestamp=datetime.today())
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
        embed.set_author(name="Question annulée", icon_url=ctx.author.avatar_url)
    return embed

async def quizEmbed(ctx: SlashContext, personal: bool, quizCount: int, user: Utilisateur, db: aiosqlite.core.Connection, page: int, pages: int, offset: int = 0) -> discord.Embed:
    """ Fonction qui créer un embed listant les quizs disponibles
    
    Args:
        ctx (SlashContext): Contexte de la commande
        personal (bool): Si l'on récupère les quizs de l'utilisateur qui a initié la commande ou globale
        quizCount (int): Nombre de quizs créés par l'auteur de la commande
        user (Utilisateur): Instance d'Utilisateur correspondant à l'auteur de la commande
        db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        page (int): Page courante
        pages (int): Nombre de pages au total
        offset (int): Offset de récupération des quizs
    
    Returns:
        discord.Embed: Embed listant les quizs du bot
    """

    if personal:
        quizs = await user.getQuizs(10, offset)            
        embed = discord.Embed(title=":books: Liste de vos quizs :books:", colour=discord.Colour(0x42a010), description="*Classé du plus récent au plus vieux. (PS: Si un quiz n'a pas au moins 1 question il n'apparaitera pas)*​")
        embed.set_author(name="Votre avez créé: " + str(quizCount) + (' quiz' if quizCount == 1 else ' quizs'), icon_url=ctx.author.avatar_url)

    else:
        quizs = await Quiz.getAll(db, limit=10, offset=offset)
        embed = discord.Embed(title=":books: Liste des quizs disponibles :books:", colour=discord.Colour(0x42a010), description="*Classé par popularité à travers tout les serveurs du bot.*​")
        embed.set_author(name="Il y a " + str(quizCount) + ' quizs disponibles', icon_url=ctx.author.avatar_url)

    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
    embed.set_footer(text=f"Utilisez ◀ et ▶ pour naviguer | Page {page}/{pages}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
    embed.add_field(name=":arrow_right: __[Id du Quiz] - Titre du quiz__", value="\u200b", inline=False)
    for quiz in quizs:
        idQuiz = await quiz.getIdQuiz()
        quizTitle = await quiz.getTitre()
        if not personal:
            creator = await quiz.getCreator(ctx.guild.id)
            embed.add_field(name=f"**[ {idQuiz} ]** - {quizTitle}", value="Créé par " + str(await creator.getName()) + " | Nombre de points: " + str(await quiz.getPoints()), inline=False)            
        else:
            embed.add_field(name=f"**[ {idQuiz} ]** - {quizTitle}", value="Nombre de points: " + str(await quiz.getPoints()), inline=False)       
    embed.add_field(name="\u200b", value="Vous pouvez utiliser `/addQuestion` pour ajouter des questions à votre quiz ou `/launchQuiz` pour lancer une game d'un quiz")
    return embed

async def recapEmbed(ctx: SlashContext, quiz: Quiz, idQuestion: int, nbQuestions: int, db: aiosqlite.core.Connection) -> discord.Embed:
    """Fonction qui permet de créer un embed récapitulatif d'une question
    
    Args:
        ctx (SlashContext): context de la commande
        quiz (Quiz): Instance de quiz dont on veut le récapitulatif
        idQuestion (int): Numéro de la question dont on veut le récapitulatif
        nbQuestions (int): Nombre de questions pour l'instance de quiz
        db (aiosqlite.core.Connection): Connection à la bd via aiosqlite

    Returns:
        discord.Embed: Embed faisant un récapitulatif d'une question        
    """
    
    reactions = ["1️⃣","2️⃣","3️⃣","4️⃣"]
    author = await quiz.getCreator(ctx.guild.id)
    points = await quiz.getPoints()
    idQuiz = await quiz.getIdQuiz()
    question = await Question.get(idQuiz, idQuestion, db)
    nbChoix = await question.getNbChoix()
    recapChoix = "⠀⠀⠀\n"
    for i, choix in enumerate(await question.getChoix()):
        estCorrecte = await choix.getEstValide()
        recapChoix += "⠀⠀⠀" + ("‎:white_check_mark: " if estCorrecte else ":negative_squared_cross_mark: ") + str(await choix.getTitre()) + ("\n\n" if i < nbChoix-1 else "")
    
    embed = discord.Embed(title=f":book: Récapitulatif du Quiz {idQuiz} : " + await quiz.getTitre(), colour=discord.Colour(0x42a010), description=f"Le quiz possède **{nbQuestions}** questions pour un total de **{points}** points\n⠀⠀⠀​", timestamp=datetime.today())
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
    embed.set_author(name="Quiz créé par: " + str(await author.getName()), icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f"Utilisez ◀ et ▶ pour naviguer | Page {idQuestion}/{nbQuestions}", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")         
    embed.add_field(name=f"{reactions[idQuestion-1]} - " + str(await question.getTitre()), value=recapChoix, inline=False)
    
    return embed