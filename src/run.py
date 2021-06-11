# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 19:28:05 2021

@author: Liam
"""

from init import client, TOKEN
import events
from commandsSlash import Commandes
from _help import HelpCommand

if __name__ == "__main__":
    try:
        client.add_cog(Commandes(client))
        client.add_cog(HelpCommand(client))
        client.run(TOKEN)
    except Exception as e:
        print(f"[ ERROR ] Une erreur est survenue: {e}")