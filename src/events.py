# -*- coding: utf-8 -*-
"""
Created on Thu Jun  10 17:15:48 2021

@author: Liam
"""

from init import client
import discord
from discord.ext import tasks
import asyncio
from datetime import datetime

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

@tasks.loop(seconds=10.0)
async def game():
    await client.change_presence(activity=discord.Streaming(name="/help", game="Utilisez /help", platform="Twitch", url="https://www.twitch.tv/sardoche"))
    await asyncio.sleep(10)
    await client.change_presence(activity=discord.Streaming(name=f"{len(client.guilds)} {'serveur' if len(client.guilds) == 1 else 'serveurs'}", game="Utilisez /help", platform="Twitch", url="https://www.twitch.tv/sardoche"))
    await asyncio.sleep(10)
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

@client.event
async def on_ready():
    print("[ START ] Le bot est en ligne")
    print(f"[ START ] Les bot est actif sur {len(client.guilds)} serveurs")
    game.start()
    
@client.event
async def on_command(ctx):
    print(f"[ COMMAND ] {ctx.author} a utilisé la commande {ctx.message.content}")

@client.event
async def on_slash_command(ctx):
    print(f"[ COMMAND ] {ctx.author} a utilisé la commande /{ctx.name}")
    
@client.event
async def on_guild_join(guild):
    
    try:    
        role = discord.utils.find(lambda r: r.name == "Projet Quiz Master", guild.roles)
        if not role:
            role = await guild.create_role(name="Projet Quiz Master", colour=0x1ABC9C, reason="Nécessaire à la gestion de permission du bot de quiz")    
        
        
        async for log in guild.audit_logs(limit=20, before = datetime.today(), action=discord.AuditLogAction.bot_add):
            if log.target == guild.me:
                try:
                    if role not in log.user.roles:
                        await log.user.add_roles(role)
                    embed = discord.Embed(title="Quiz Bot a rejoint votre serveur!", colour=discord.Colour(0x1ABC9C), description="Bonjour! Un nouveau role a été ajouté à votre serveur: ```json\n\"\n@Projet Quiz Master\n\"```Le rôle vous a automatiquement été ajouté. Ajoutez ce rôle à un utilisateur pour lui donner la permission de créer et initialiser des quiz.\n\nPour vous lancer dans l'utilisation du bot, n'hesitez pas à regarder notre README sur gitlab ou a utiliser la commande: ```/help```", timestamp=datetime.today())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                    embed.set_author(name="Introduction", icon_url=log.user.avatar_url)
                    await log.user.send(log.user.mention, embed=embed)
                except Exception as e:
                    print(f"[ ERROR ] On join {e}")
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            embed = discord.Embed(title="Quiz Bot a rejoint votre serveur!", colour=discord.Colour(0x1ABC9C), description="Bonjour! Je n'ai pas réussi à vous contacter par MP le message est par conséquent envoyé ici.\nUn nouveau role a été ajouté à votre serveur: ```json\n\"\n@Projet Quiz Master\n\"```Ajoutez ce rôle à un utilisateur pour lui donner la permission de créer et initialiser des quiz.\n\nPour vous lancer dans l'utilisation du bot, n'hesitez pas à regarder notre README sur gitlab ou a utiliser la commande: ```/help```", timestamp=datetime.today())
                            embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                            embed.set_author(name="Introduction", icon_url=log.user.avatar_url)
                            await channel.send(log.user.mention, embed=embed)
                            break
                    pass
                break
    except Exception:
        print("[ ERROR ] Le bot n'as pas eu les permissions d'accès au logs")
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:        
                embed = discord.Embed(title="", colour=discord.Colour(0xFF001C), description="```diff\n- Le bot n'a pas reçu les permissions nécessaires pour fonctionner. Veuillez re-inviter le bot avec les permissions adéquates.```", timestamp=datetime.today())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/846496626558500864/847844887847370752/Quiz.png?width=1145&height=670")
                embed.set_author(name="Une erreure est survenue", icon_url="https://cdn.discordapp.com/avatars/847830349060636682/c82344f7811d55d4d8fe67dc2680c88b.webp")
                await channel.send('@here',embed=embed)
                break
                            
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

    