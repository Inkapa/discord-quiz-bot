# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 11:59:04 2021

@author: Liam
"""
from discord.ext import commands
import aiosqlite
import sqlite3
from database import Utilisateur, Quiz

class TestUtilisateur(commands.Cog):
    def __init__(self, client, sourceDb):
        self.client = client
        self.source = sourceDb
    
    @commands.command()
    async def initUser(self, ctx):
        async with aiosqlite.connect(self.source) as db:
            db.row_factory = sqlite3.Row
            
            user = await Utilisateur.get(ctx.author.id, db)
            name = await user.getName()
            idD = await user.getIdDiscord()
            score = await user.getScoreTotal()
            rep = len(await user.getReponses())
            quizs = len(await user.getQuizs())
            nbInst = await user.getNbParticipations()
            text = f"""
Hey there {name}, your id is {idD}
Your total score is {score} points
You have {rep} responses and you have created {quizs} quizs
You have participated to {nbInst} games
            """
            await ctx.send(text)
        
    @commands.command()
    async def leaderboard(self, ctx):
        async with aiosqlite.connect(self.source) as db:
            db.row_factory = sqlite3.Row
            text = ""
            leader = await Utilisateur.getLeaderboard(db)
            for user in leader:
                text += await user.getName() + " : " + str(await user.getScoreTotal()) + " points\n"
            await ctx.send(text)
            
    @commands.command()
    async def addPoints(self, ctx):
        async with aiosqlite.connect(self.source) as db:
            db.row_factory = sqlite3.Row
            
            user = await Utilisateur.get(ctx.author.id, db)
            await user.addPoints(10)
            
            await ctx.send(str(await user.getScoreTotal()) + " points")


class TestQuiz(commands.Cog):
    def __init__(self, client, sourceDb):
        self.client = client
        self.source = sourceDb
    
    @commands.command()
    async def createQuiz(self, ctx, titre, points):
        async with aiosqlite.connect(self.source) as db:
            db.row_factory = sqlite3.Row
            
            quiz = await Quiz.create(titre, points, ctx.author.id, db)
            titre = await quiz.getTitre()
            quizId = await quiz.getIdQuiz()
            instanceCount = await quiz.getInstanceCount()
            points = await quiz.getPoints()
            text = f"""
Quiz id: {quizId}
Title: {titre}
Number of instances: {instanceCount}
Points: {points}
            """
            await ctx.send(text)
            user = await quiz.getCreator()
            name = await user.getName()
            idD = await user.getIdDiscord()
            score = await user.getScoreTotal()
            rep = len(await user.getReponses(ctx.author.id))
            quizs = len(await user.getQuizs())
            nbInst = await user.getNbParticipations()

            text = f"""
Quiz creator: {name}, his id is {idD}
His total score is {score} points
He has {rep} responses and has created {quizs} quizs
You have participated to {nbInst} games
            """
            await ctx.send(text)
        