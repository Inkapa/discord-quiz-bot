# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 12:22:12 2021

@author: Liam
"""

from init import client, sourceDb
import asyncio
import aiosqlite
import sqlite3
from database import Utilisateur, Quiz, Question, Choix, Instance, Reponse

@client.command()
async def recupScore(ctx):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        user = await Utilisateur.get(ctx.author.id, ctx.guild.id, db)
        stats = await user.getStatistiques()
        await ctx.send(f"Bonjour {ctx.author.mention}, voici ton score total: " + str(await stats.getScoreTotal()))



@client.command()
async def recupNom(ctx):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        user = await Utilisateur.get(ctx.author.id, ctx.guild.id, db)
        await ctx.send(f"Bonjour {ctx.author.mention}, votre nom est: " + str(await user.getName()))

@client.command()
async def creerQuiz(ctx, points, titre):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        
        quiz = await Quiz.create(titre,points, ctx.author.id, db)
        if quiz:
            await ctx.send("Id du Quiz créée: " + str(await quiz.getIdQuiz()))
            
            nom = await quiz.getTitre()
            points = await quiz.getPoints()
            nbInstances = await quiz.getInstanceCount()
            await ctx.send(f"Nom du quiz: {nom}\nNbPoints: {points}\nNbInstances: {nbInstances}")
        else:
            await ctx.send("La création du quiz a échouée")

@client.command()
async def addQuestion(ctx, idQuiz, idQuestion, titre):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        
        question = await Question.create(idQuiz, idQuestion, titre, db)
        if question:
            await ctx.send("Id de la Question créée: " + str(await question.getIdQuestion()))
            
            nom = await question.getTitre()
            await ctx.send(f"La Question: {nom}")
        else:
            await ctx.send("La création de la question a échouée")

@client.command()
async def addChoix(ctx, idQuiz, idQuestion, idChoix, titre, estValide):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        
        choice = await Choix.create(idQuiz, idQuestion, idChoix, titre, estValide, db)
        if choice:
            await ctx.send("Id du Choix créée: " + str(await choice.getIdChoix()))
            
            nom = await choice.getTitre()
            valide = await choice.getEstValide()
            await ctx.send(f"Nom du choix: {nom}\nEst valide: {valide}")
        else:
            await ctx.send("La création du choix a échouée")
    
@client.command()
async def recapQuiz(ctx, idQuiz):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        
        quiz = await Quiz.get(idQuiz, db)
        text = "Nom: " + str(await quiz.getTitre()) + "\n"
        text += "Nb Points: " + str(await quiz.getPoints()) + "\n"
        text += "Instances: " + str(await quiz.getInstanceCount()) + "\n"
        creator = await quiz.getCreator(ctx.guild.id)
        text += "Créateur: " +str(await creator.getName()) + "\n\n"
        for question in await quiz.getQuestions():
            text += "   Question id: " + str(await question.getIdQuestion()) + "\n"
            text += "   Question title: " + str(await question.getTitre()) + "\n"
            for choix in await question.getChoix():
                text += "       Choix id: " + str(await choix.getIdChoix()) + "\n"
                text += "       Choix title: " + str(await choix.getTitre()) + "\n"
                text += "       Est correcte: " + ("Oui" if await choix.getEstValide() else "Non") + "\n\n"
        await ctx.send(text)
        
@client.command()
async def addInstance(ctx, idQuiz, multiplicateur = 1):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        
        instance = await Instance.create(idQuiz,db, ctx.guild.id, multiplicateur)
        if instance:
            await ctx.send("Id de l'Instance créée: " + str(await instance.getIdInst()))
            
            nom = await instance.getMultiplicateur()
            date = await instance.getDateDeb(formated=True)
            await ctx.send(f"Multiplicateur: {nom}\nDate de début: {date}")
        else:
            await ctx.send("La création de l'instance a échouée")
            
@client.command()
async def addReponse(ctx, idInst, idQuestion, idChoix, idDiscord: int = None):
    async with aiosqlite.connect(sourceDb) as db:
        db.row_factory = sqlite3.Row
        if idDiscord is None:
            idDiscord = ctx.author.id
            
        reponse = await Reponse.create(idInst, idQuestion, idChoix, idDiscord, db)
        if reponse:
            await ctx.send("id Réponse: " + str(await reponse.getIdRep()) + "\n" + "Est correcte: " + ("Oui" if await reponse.estCorrecte() else "Non"))
        else:
            await ctx.send("La création de la réponse a échouée")


@client.command()
async def testReactions(ctx):
    message = await ctx.send("Test")
    await message.add_reaction("🔥")
    await asyncio.sleep(5)
    
    message = await ctx.channel.fetch_message(message.id)
    reaction = [reaction for reaction in message.reactions if reaction.emoji == "🔥"][0]
    users = await reaction.users().flatten()
    for user in users:
        if not user.bot:
            print(user)