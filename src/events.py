# -*- coding: utf-8 -*-
"""
Created on Thu Jun  10 17:15:48 2021

@author: Liam
"""

from init import client
import discord
from discord.ext import tasks
import asyncio

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

@tasks.loop(seconds=10.0)
async def game():
    await client.change_presence(activity=discord.Streaming(name="/help", game="Utilisez la commande /help", platform="Twitch", url="https://www.twitch.tv/sardoche"))
    await asyncio.sleep(10)
    await client.change_presence(activity=discord.Streaming(name=f"{len(client.guilds)} {'serveur' if len(client.guilds) == 1 else 'serveurs'}", game="Utilisez la commande /help", platform="Twitch", url="https://www.twitch.tv/sardoche"))
    await asyncio.sleep(10)
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

@client.event
async def on_ready():
    print("[ START ] Le bot est en ligne")
    print(f"[ START ] Le bot est actif sur {len(client.guilds)} serveurs")
    game.start()
    
@client.event
async def on_command(ctx):
    print(f"[ COMMAND ] {ctx.author} a utilisé la commande {ctx.message.content}")

@client.event
async def on_slash_command(ctx):
    print(f"[ COMMAND ] {ctx.author} a utilisé la commande /{ctx.name}")
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

    