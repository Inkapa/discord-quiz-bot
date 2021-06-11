# -*- coding: utf-8 -*-
"""
Created on Thu Jun  10 17:15:48 2021

@author: Liam
"""
import pathlib
import sqlite3

def checkDB(path: pathlib.Path):
    if not path.is_file():
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        sql_file = open("../Database/createDB.sql")
        
        sql_as_string = sql_file.read()
        
        cursor.executescript(sql_as_string)
        connection.commit()
        connection.close()