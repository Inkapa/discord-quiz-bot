# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 18:05:37 2021

@author: Liam
"""
import discord.utils
from init import client
import time
import aiosqlite

# La docstring a été écrite en suivant les normes Google https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings

# On aurait pu séparer chaque classe dans son propre fichier. Mais pour des raisons de simplification d'importation
# et pour éviter des problèmes d'import circulaires, j'ai décidé de tout mettre dans un même fichier


class Utilisateur(object):
    """Classe d'instance de la table Utilisateur
    
    Permet l'instanciation d'objets correspondant à une ligne de la table utilisateur
    permet la récupération des données correspondant dans la base de donnée.
    """
    
    @staticmethod
    async def __insertUser(user: discord.User, db: aiosqlite.core.Connection) -> None:
        """Insère un nouvel utilisateur dans la BD
        
        Args:
            user (discord.User): Utilisateur discord à ajouter
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        """
        
        await db.execute("""INSERT INTO Utilisateur (idDiscord, name) VALUES(?, ?)""",(user.id, user.name + "#" + user.discriminator,))
        await db.commit()
    
    @staticmethod
    async def __updateUserName(user: discord.User, db: aiosqlite.core.Connection) -> None:
        """Met à jour le pseudonyme d'un utilisateur dans la BD
        
        Si un utilisateur déjà existant dans la BD change de pseudonyme ou de discriminator Discord,
        on vient le mettre à jour dans la BDs
        
        Args:
            user (discord.User): Utilisateur discord à ajouter
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        """
        
        await db.execute("""UPDATE Utilisateur SET name = (?) WHERE idDiscord = (?)""", (user.name + "#" + user.discriminator, user.id,))
        await db.commit()

    
    @staticmethod
    async def checkUser(snowflake: int, idServer: int, db: aiosqlite.core.Connection) -> None:
        """Vérifie la présence d'un utilisateur dans la BD
        
        Vérifie si l'identifiant Discord (aka "snowflake") est présent dans la BD,
        Si oui:
            Vérifier que le pseudonyme correspond
        
        Si non:
            Insert l'utilisateur dans la BD
        
        Vient aussi assurer la création d'une ligne de statistiques pour l'utilisateur dans le serveur courant
        
        Args:
            snowflake (int): Identifiant Discord d'un utilisateur
            idServer (int): Identifiant du serveur Discord
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        """
        
        user = discord.utils.get(client.get_all_members(), id=snowflake)
        if user is not None:
            async with db.execute("SELECT name FROM Utilisateur WHERE idDiscord = (?)", (user.id,)) as cursor:
                name = await cursor.fetchone()
                stats = await Statistiques.get(idServer, snowflake, db)
                if not stats:
                    await Statistiques.create(idServer, snowflake, db)
                if not name:
                    await Utilisateur.__insertUser(user, db)
                else:
                    if not name[0] == user.name + "#" + user.discriminator:
                        await Utilisateur.__updateUserName(user, db)
        else:
            print("Utilisateur n'est pas dans la liste du bot")
            
            
    @classmethod
    async def get(cls, snowflake: int, idServer: int, db: aiosqlite.core.Connection) -> object:
        """Récupère une instance d'Utilisateur
        
        Vient récupérer les informations relatives à un utilisateur dans la BD puis retourne une instance
        de Utilisateur correspondant
        
        
        Args:
            snowflake (int): Identifiant Discord d'un utilisateur
            idServer (int): Identifiant du serveur Discord
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        
        Returns:
            self: Instance d'Utilisateur
        """
        
        self = Utilisateur()
        await Utilisateur.checkUser(snowflake, idServer, db)
        async with db.execute("SELECT * FROM Utilisateur WHERE idDiscord = (?)", (snowflake,)) as cursor:
            user = await cursor.fetchone()
            idDiscord, name = user['idDiscord'], user['name']
        self.__db = db
        self.__idDiscord = idDiscord
        self.__name = name
        self.__idServer = idServer
        return self   
    

    async def getName(self) -> str:
        """Accésseur qui retourne le nom de l'utilisateur
        
        Le nom de l'utilisateur est formé de son pseudonyme et de son descriminator Discord
        sous le format Nom#Discriminator
        
        Returns:
            str: Nom de l'utilisateur
        """
        return self.__name
    
    async def getIdDiscord(self) -> int:
        """Accésseur qui retourne l'identifiant Discord de l'utilisateur
        
        Returns:
            int: Identifiant Discord unique (aka "snowflake") de l'utilisateur
        """
        return self.__idDiscord
    
    async def getIdServer(self) -> int:
        """Accésseur qui retourne l'identifiant Discord du serveur
        
        Returns:
            int: Identifiant Discord unique du serveur
        """
        return self.__idServer
    
    async def addPoints(self, points: float, idServer: int) -> None:
        """Méthode d'instance qui permet d'ajouter des points au score de l'Utilisateur
        
        Args:
            points (int): Nombre de points à ajouter
            idServer (int): Identifiant du serveur Discord
        """
        await self.__db.execute("""UPDATE Statistiques SET scoreTotal = scoreTotal + (?) WHERE idDiscord = (?) AND idServer = (?)""", (points, self.__idDiscord, idServer,))
        await self.__db.commit()
    
    async def getQuizs(self, limit: int = None, offset: int = None) -> list:
        """Accésseur qui retourne une liste d'instances de quizs créé par l'utilisateur (trié par date de création)

        Args:
            limit (int): Spécifie une limite dans le nombre d'instance à retourner
            (default None)
            offset (int): Spécifie un point de départ
            (default None)
        
        Returns:
            list: Liste d'instances de Quiz créés par l'utilisateur
        """
        return await Quiz.getAll(self.__db, self.__idDiscord, limit, offset)
        
    async def getReponses(self, idInst: int = None) -> list:
        """Accésseur qui retourne une liste de réponses de l'utilisateur pour une instance 

        Args:
            idInst (int): Identifiant de l'instance sur laquelle on veut récupérer les réponses de l'utilisateur
        
        Returns:
            list: Liste d'instances de Réponse liant l'utilisateur à l'instance d'identifiant idInst
        """
        return await Reponse.getAll(self.__db, idInst, self.__idDiscord)
    
    async def getStatistiques(self) -> object:
        """Accésseur qui retourne une instance de Statistiques correspondant à l'utilisateur

        Returns:
            object: Instance de Statistiques correspondant à l'utilisateur pour le serveur courant
        """
        return await Statistiques.get(self.__idServer, self.__idDiscord, self.__db)
    
    async def getCurrentPosition(self, idInst: int = None) -> int:
        """Accéseur qui retourne la position de l'utilisateur dans un classement
        
        Si un identifiant d'Instance est passé en paramètre, la position de l'utilisateur dans le classement
        de cette instance sera retourné
        Sinon, la position de l'utilisateur dans le classement global du serveur sera retourné
        
        Args:
            idInst (int): Identifiant de l'instance dont ont veut le classement
            (default None)
        
        Returns:
            int: Place de l'utilisateur dans le classement
        """
        
        if idInst:
            async with self.__db.execute("""SELECT row FROM (SELECT ROW_NUMBER() OVER (ORDER BY nbCorrectes DESC, idDiscord) AS row, idDiscord, nbCorrectes FROM (SELECT idDiscord, SUM(estCorrecte) "nbCorrectes" FROM Instance i, Reponse r WHERE i.idInst = r.idInst AND i.idInst = (?) GROUP BY idDiscord)) WHERE idDiscord = (?)""", (idInst, self.__idDiscord,)) as cursor:
                res = await cursor.fetchone()            
        else:
            async with self.__db.execute("""SELECT row FROM (SELECT ROW_NUMBER() OVER (ORDER BY scoreTotal DESC, idDiscord) AS row, idDiscord FROM (SELECT idDiscord, scoreTotal FROM Statistiques WHERE idServer = (?))) WHERE idDiscord = (?)""", (self.__idServer, self.__idDiscord,)) as cursor:
                res = await cursor.fetchone()
        return res[0]

    async def getResultats(self, idInst: int) -> list:
        """Accéseur qui retourne les résultats d'un utilisateur pour une instance
        
        Args:
            idInst (int): Identifiant de l'instance dont ont veut le classement
        
        Returns:
            list: Listes de tuples contenant pour chaque question d'une instance : l'instance de Question correspondant, si la réponse de l'utilisateur est correcte et une instance du choix de l'utilisateur pour cette question
        """        
        async with self.__db.execute("SELECT i.idQuiz, r.idQuestion, r.estCorrecte, r.idChoix FROM Reponse r, Instance i WHERE r.idInst = i.idInst and r.idDiscord = (?) AND i.idInst = (?) GROUP BY r.idQuestion",(self.__idDiscord, idInst,)) as cursor:
            resultats = []
            async for row in cursor:
                idQuiz, idQuestion, estCorrecte, idChoix = row[0], row[1], row[2], row[3]
                resultats.append((await Question.get(idQuiz, idQuestion, self.__db), estCorrecte, await Choix.get(idQuiz, idQuestion, idChoix, self.__db) if idChoix else None))
            return resultats
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                
        
class Quiz(object):
    """Classe d'instance de la table Quiz
    
    Permet l'instanciation d'objets correspondant à une ligne de la table Quiz
    permet la récupération des données correspondant dans la base de donnée.
    """
    
    @staticmethod
    async def create(titre: str, points: float, snowflake: int, db: aiosqlite.core.Connection) -> object:
        """Méthode de classe (dites "Usine") qui vient générer une instance de Quiz en ajoutant un quiz dans la BD
        
        Args:
            titre (str): Titre du quiz
            points (float): Nombre de points que vaut le quiz
            snowflake (int): Identifiant Discord unique du créateur du quiz
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        
        Returns:
            object: Instance du Quiz créé
        """
        try:
            async with db.execute("INSERT INTO Quiz (titre, idDiscord, points) VALUES(?,?,?) RETURNING idQuiz", (titre, snowflake, points,)) as cursor:
                res = await cursor.fetchone()
                idQuiz = res['idQuiz']
            await db.commit()
            instance = await Quiz.get(idQuiz, db)
        except Exception as e:
            print("[ ERROR ] On Quiz.create() " + str(e))
            instance = False
        return instance
    
    
    @staticmethod
    async def getAll(db: aiosqlite.core.Connection, snowflake: int = None, limit: int = None, offset: int = None):
        """Accésseur de classe qui retourne une liste d'instances de quizs disponibles dans la BD
        
        Si un identifiant Discord d'un utilisateur est spécifié, seul les instances des quizs créés par
        cet utilisateur seront retournés
        
        Sinon, une instance de chaque quiz dans la BD sera retourné (selon les limites et offset passés en paramètre)

        Args:
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            snowflake (int): Identifiant unique d'un utilisateur Discord
            (default None)
            limit (int): Spécifie une limite dans le nombre d'instance à retourner
            (default None)
            offset (int): Spécifie un point de départ
            (default None)
        
        Returns:
            list: Liste d'instances de Quiz
        """
        
        if limit is None:
            sqlLimit = ""
        else:
            offset = 0 if offset is None else offset
            sqlLimit = f" LIMIT {limit} OFFSET {offset}"
        if snowflake is None:
            async with db.execute("""SELECT DISTINCT qz.* FROM Quiz qz, Question qe WHERE qz.idQuiz = qe.idQuiz ORDER BY instanceCount""" + sqlLimit) as cursor:
                allQuizs = []
                async for row in cursor:
                    allQuizs.append(await Quiz.get(row['idQuiz'], db))
                    
        else:
            async with db.execute("""SELECT DISTINCT qz.* FROM Quiz qz, Question qe WHERE qz.idQuiz = qe.idQuiz AND idDiscord = (?) ORDER BY idQuiz DESC""" + sqlLimit,(snowflake,)) as cursor:
                allQuizs = []
                async for row in cursor:
                    allQuizs.append(await Quiz.get(row['idQuiz'], db))
        return allQuizs
    
    @classmethod
    async def get(cls, idQuiz: int, db: aiosqlite.core.Connection) -> object:
        """Accésseur qui retourne une instance de Quiz à partir de son identifiant

        Args:
            idQuiz (int): Identifiant unique du Quiz à récupérer
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        
        Returns:
            object: Instance de quiz correspondant
        """        
        async with db.execute("SELECT * FROM Quiz WHERE idQuiz = (?)", (idQuiz,)) as cursor:
            quiz = await cursor.fetchone()
            if not quiz:
                self = False
            else:
                self = Quiz()
                idQuiz, instanceCount, points, titre, idDiscord = quiz['idQuiz'], quiz['instanceCount'], quiz['points'], quiz['titre'], quiz['idDiscord']
                self.__idQuiz = idQuiz
                self.__titre = titre
                self.__idDiscord = idDiscord
                self.__instanceCount = instanceCount
                self.__points = points
                self.__db = db
        return self
    
    async def getIdQuiz(self) -> int:
        """Accésseur qui retourne l'identifiant du Quiz

        Returns:
            int: Identifiant du quiz courant
        """     
        return self.__idQuiz
    
    async def getTitre(self) -> str:
        """Accésseur qui retourne le titre du Quiz

        Returns:
            str: Titre du quiz courant
        """     
        return self.__titre
    
    async def getInstanceCount(self) -> int:
        """Accésseur qui retourne le nombre d'instances d'un Quiz

        Returns:
            int: Nombre d'instances du quiz courant
        """    
        return self.__instanceCount
    
    async def getPoints(self) -> int:
        """Accésseur qui retourne le nombre de points du quiz

        Returns:
            int: Nombre de points du quiz courant
        """    
        return self.__points
    
    @staticmethod
    async def getCount(db, snowflake: int = None) -> int:
        """Accésseur qui retourne le nombre de quizs dans la BD
        
        Un quiz n'est comptabilisé uniquement si il possède au moins une question
        
        Un identifiant Discord (aka "snowflake") peut être passé en paramètre, si
        c'est le cas le nombre de quizs (d'au moins une question) créés par l'utilisateur sera retourné 

        Returns:
            int: Nombre de quizs
        """    
        if snowflake is None:
            async with db.execute("""SELECT COUNT(DISTINCT qz.idQuiz) FROM Quiz qz, Question qe WHERE qz.idQuiz = qe.idQuiz""") as cursor:
                res = await cursor.fetchone()
        else:
            async with db.execute("""SELECT COUNT(DISTINCT qz.idQuiz) FROM Quiz qz, Question qe WHERE qz.idQuiz = qe.idQuiz AND idDiscord = (?)""",(snowflake,)) as cursor:
                res = await cursor.fetchone()
        return res[0]
         
    async def getNbQuestions(self) -> int:
        """Accésseur qui retourne le nombre de questions du Quiz courant

        Returns:
            int: Nombre de questions du quiz courant
        """    
        async with self.__db.execute("SELECT COUNT(DISTINCT idQuestion) FROM Question WHERE idQuiz = (?)", (self.__idQuiz,)) as cursor:
            res = await cursor.fetchone()
            nb = False
            if res:
                nb = res[0]
            return nb
                       
    async def getCreator(self, idServer: int) -> object:
        """Accéseur qui retourne une instance d'Utilisateur correspondant au créateur du Quiz
        
        Args:
            idServer (int): Identifiant unique du Serveur
        
        Returns:
            object: Instance d'Utilisateur correspondant au créateur du quiz

        """
        return await Utilisateur.get(self.__idDiscord, idServer, self.__db)
    
    async def getQuestions(self) -> list:
        """Accéseur qui retourne une liste d'instances des questions du Quiz
        
        
        Returns:
            list: Liste d'instances des questions du Quiz

        """
        return await Question.getAll(self.__db, self.__idQuiz)
    
    async def getInstances(self, idServer: int, active: bool) -> list:
        """Accéseur qui retourne une liste d'objet ""d'instances" (Table Instance ou "game") du Quiz pour un serveur
        
        Args:
            idServer (int): Identifiant du serveur dont on veut récupérer les instances du quiz
            active (bool): Si l'on veut récupérer les instances actives (sans date de fin définie) ou terminées (avec une date de fin définie)
        
        Returns:
            list: Liste des instances de la table Instance correspondant au quiz dans un serveur d'identifiant idServer

        """
        return await Instance.getAll(self.__db, self.__idQuiz, idServer, active)

    async def addQuestion(self, titre: str) -> object:
        """Méthode d'instance qui permet l'ajout d'une question à un Quiz
        
        Args:
            titre (str): Titre de la question
        
        Returns:
            object: Instance de la question que l'on vient d'ajouter au quiz

        """
        return await Question.create(self.__idQuiz, titre, self.__db)
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

class Question(object):
    """Classe d'instance de la table Question
    
    Permet l'instanciation d'objets correspondant à une ligne de la table Question
    permet la récupération des données correspondant dans la base de donnée.
    """

    @staticmethod
    async def __getIdQuestion(idQuiz: int, db: aiosqlite.core.Connection) -> int:
        """Accesseur privé qui permet de récupérer l'identifiant incrémental future de la prochaine question ajoutée au Quiz
        
        Args:
            idQuiz (int): Identifiant du Quiz auquel on veut récupérer l'identifiant de la prochaine question
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            int: Identifiant de la prochaine question du Quiz d'identifiant idQuiz
        
        """
        async with db.execute("SELECT COUNT(DISTINCT idQuestion) FROM Question WHERE idQuiz = (?)", (idQuiz,)) as cursor:
            res = await cursor.fetchone()
            idQuestion = res[0]+1
            return idQuestion        
    
    @staticmethod
    async def create(idQuiz: int, titre: str, db: aiosqlite.core.Connection) -> object:
        """Méthode de classe (dit "Usine") qui permet l'ajout d'une Question dans la BD et la création de son instance correspondant
        
        Args:
            idQuiz (int): Identifiant du Quiz auquel on veut ajouter une question
            titre (str): Titre de la question
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance de la question créée
        
        """
        try:
            idQuestion = await Question.__getIdQuestion(idQuiz, db)
            await db.execute("INSERT INTO Question (titre, idQuestion, idQuiz) VALUES(?,?,?)", (titre, idQuestion, idQuiz,))
            await db.commit()
            instance = await Question.get(idQuiz, idQuestion, db)
        except Exception as e:
            print("[ ERROR ] On Question.create() " + str(e))
            instance = False
        return instance
    
    @staticmethod
    async def getAll(db: aiosqlite.core.Connection, idQuiz: int) -> list:
        """Accésseur de classe qui retourne une liste d'instances de questions correspondant à un quiz disponibles dans la BD
        
    
        Args:
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            idQuiz (int): Identifiant unique du quiz dont on veut récupérer les questions

        Returns:
            list: Liste d'instances des questions du quiz d'identifiant idQuiz
        """
        async with db.execute("""SELECT DISTINCT * FROM Question WHERE idQuiz = (?)""",(idQuiz,)) as cursor:
            allQuestions = []
            async for row in cursor:
                allQuestions.append(await Question.get(row['idQuiz'], row['idQuestion'], db))
        return allQuestions

    
    @classmethod
    async def get(cls, idQuiz: int, idQuestion: int, db: aiosqlite.core.Connection) -> object:
        """Accésseur de classe qui retourne une instance de Question selon l'identifiant du Quiz et de la Question passé en paramètre
        
    
        Args:
            idQuiz (int): Identifiant unique du quiz dont on veut récupérer les questions
            idQuestion (int): Numéro de la question pour le quiz d'identifiant idQuiz (Lien-Identifiant)
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite

        Returns:
            object: Instance de la question n°idQuestion du quiz d'identifiant idQuiz
        """
        
        async with db.execute("SELECT * FROM Question WHERE idQuiz = (?) AND idQuestion = (?)", (idQuiz, idQuestion,)) as cursor:
            question = await cursor.fetchone()
            if not question:
                self = False
            else:
                self = Question()
                idQuiz, idQuestion, titre = question['idQuiz'], question['idQuestion'], question['titre']
                self.__idQuiz = idQuiz
                self.__idQuestion = idQuestion
                self.__titre = titre
                self.__db = db
                
        return self
    
    async def getQuiz(self) -> object:
        """Accésseur qui retourne une instance du Quiz dont la question courante fait partie
        
        Returns:
            object: Instance du Quiz dont la question courante fait partie
        """
        return await Quiz.get(self.__idQuiz, self.__db)
    
    async def getTitre(self) -> str:
        """Accésseur qui retourne le titre de la question courante
        
        Returns:
            str: Titre de la question courante
        """
        return self.__titre
    
    async def getIdQuestion(self) -> int:
        """Accésseur qui retourne le n° de la question courante
        
        Returns:
            int: N° (ou identifiant) de la question courante par rapport à son quiz
        """
        return self.__idQuestion
    
    async def getNbChoix(self) -> int:
        """Accésseur qui retourne le nombre de choix lié à la question courante
        
        Returns:
            int: Le nombre de choix que possède la question courante
        """
        async with self.__db.execute("SELECT COUNT(DISTINCT idChoix) FROM Choix WHERE idQuiz = (?) AND idQuestion=(?)", (self.__idQuiz,self.__idQuestion,)) as cursor:
            res = await cursor.fetchone()
            nb = False
            if res:
                nb = res[0]
            return nb
    
    async def getChoix(self) -> list:
        """Accésseur qui retourne une liste des instances de Choix correspondante à la question courante
        
        Returns:
            list: Liste des instances de Choix appartenant à la question courante
        """
        return await Choix.getAll(self.__db, self.__idQuiz, self.__idQuestion)
    
    async def getBonneReponse(self) -> object:
        """Accésseur qui retourne une instance de Choix correspondante à la bonne réponse de la question courante
        
        Returns:
            object: Instance de Choix correspondante à la bonne réponse de la question courante
        """
        async with self.__db.execute("SELECT idChoix FROM Choix WHERE idQuiz = (?) AND idQuestion= (?) AND estValide = 1", (self.__idQuiz,self.__idQuestion,)) as cursor:
            res = await cursor.fetchone()
            return await Choix.get(self.__idQuiz, self.__idQuestion, res[0], self.__db)
    
    async def addChoix(self, titre, estValide) -> object:
        """Méthode d'instance qui permet d'ajouter un choix à la question courante et de retourner son instance
        
        Returns:
            object: Instance du choix créé pour la question courante
        """
        return await Choix.create(self.__idQuiz, self.__idQuestion, titre, estValide, self.__db)
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

class Choix(object):
    """Classe d'instance de la table Choix
    
    Permet l'instanciation d'objets correspondant à une ligne de la table Choix
    permet la récupération des données correspondant dans la base de donnée.
    
    """
    
    @staticmethod
    async def __getIdChoix(idQuiz: int, idQuestion: int,  db: aiosqlite.core.Connection) -> int:
        """Accesseur privé qui permet de récupérer l'identifiant incrémental future du prochain Choix ajouté à une question d'un Quiz
        
        Args:
            idQuiz (int): Identifiant du Quiz auquel est lié la question
            idQuestion (int): Identifiant de la question du quiz idQuiz auquel on veut récupérer l'identifiant du prochain Choix
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            int: Identifiant du prochaine Choix de la question d'identifiant idQuestion du Quiz d'identifiant idQuiz
        
        """
        async with db.execute("SELECT COUNT(DISTINCT idChoix) FROM Choix WHERE idQuiz = (?) AND idQuestion=(?)", (idQuiz, idQuestion,)) as cursor:
            res = await cursor.fetchone()
            idChoix = res[0]+1
            return idChoix
    
    @staticmethod
    async def create(idQuiz: int, idQuestion: int, titre: str, estValide: int, db: aiosqlite.core.Connection) -> object:
        """Méthode de classe (Dites "Usine") qui pemet de rajouter une Choix d'une Question d'un Quiz dans la BD et de retourner son instance
        
        Args:
            idQuiz (int): Identifiant du Quiz auquel la question est lié
            idQuestion (int): Identifiant (ou numéro) de la question pour le quiz d'identifiant idQuiz auquel au vont ajouter un choix
            titre (int): Titre du choix
            estValide (int): Si le choix est valide ou non (0 ou 1)
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance du choix que l'on vient de créer
        
        """
        try:
            idChoix = await Choix.__getIdChoix(idQuiz, idQuestion, db)
            await db.execute("INSERT INTO Choix (idQuiz, idQuestion, idChoix, titre, estValide) VALUES(?,?,?,?,?)", (idQuiz, idQuestion, idChoix, titre, estValide,))
            await db.commit()
            instance = await Choix.get(idQuiz, idQuestion, idChoix, db)
        except Exception as e:
            print("[ ERROR ] On Choix.create() " + str(e))
            instance = False
        return instance
    
    @staticmethod
    async def getAll(db: aiosqlite.core.Connection, idQuiz: int, idQuestion: int) -> list:
        """Accesseur de classe qui retourne une liste des instances de Choix disponnibles dans la BD pour une question d'un quiz
        
        Args:
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            idQuiz (int): Identifiant du Quiz auquel la question est lié
            idQuestion (int): Identifiant (ou numéro) de la question pour le quiz d'identifiant idQuiz a partir duquel on veut récupérer les instances de choix
            
        Returns:
            list: Liste d'instances des choix de la question d'identifiant idQuestion pour le quiz d'identifiant idQuiz
        """
        async with db.execute("""SELECT DISTINCT * FROM Choix WHERE idQuiz = (?) AND idQuestion = (?)""",(idQuiz, idQuestion,)) as cursor:
            allChoices = []
            async for row in cursor:
                allChoices.append(await Choix.get(row['idQuiz'], row['idQuestion'], row['idChoix'], db))
        return allChoices
    
    @classmethod
    async def get(cls, idQuiz: int, idQuestion: int, idChoix: int, db: aiosqlite.core.Connection) -> object:
        """Accesseur de classe qui retourne une instance de choix à l'aide de son identifiant, celui de sa question et celui de son quiz
        
        Args:
            idQuiz: Identifiant du Quiz auquel la question est lié
            idQuestion: Identifiant (ou numéro) de la question pour le quiz d'identifiant idQuiz a partir duquel on veut récupérer une instance de Choix
            idChoix: Identifiant (ou numéro) du choix de la question dont on veut récupérer l'instance
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance de choix correspondant au choix N°idChoix de la question N°idQuestion du quiz idQuiz
        """
        async with db.execute("SELECT * FROM Choix WHERE idChoix = (?) AND idQuestion = (?) AND idQuiz = (?)", (idChoix, idQuestion,idQuiz,)) as cursor:
            choix = await cursor.fetchone()
            if not choix:
                self = False
            else:
                self = Choix()
                idQuiz, idQuestion, idChoix, titre, estValide = choix['idQuiz'], choix['idQuestion'], choix['idChoix'], choix['titre'], choix['estValide']
                self.__idChoix = idChoix
                self.__idQuiz = idQuiz
                self.__idQuestion = idQuestion
                self.__titre = titre
                self.__estValide = estValide
                self.__db = db
                
        return self

    async def getIdChoix(self) -> int:
        """Accésseur qui retourne l'identifiant (ou Numéro) du Choix courant
        
        Returns:
            int: Identifiant (ou numéro) du Choix courant
        """
        return self.__idChoix
    
    async def getQuiz(self) -> object:
        """Accesseur qui retourne une instance de Quiz correspondant au quiz dont le choix fait partie
        
        Returns:
            object: Instance du quiz dont le choix fait partie
        """
        return await Quiz.get(self.__idQuiz, self.__db)
    
    async def getTitre(self) -> str:
        """Accésseur qui retourne le titre du choix courant
        
        Returns:
            str: Titre du choix courant
        """
        return self.__titre
    
    async def getQuestion(self) -> object:
        """Accésseur qui retourne l'instance de la question correspondant au choix courant
        
        Returns:
            object: Instance de la Question dont le choix fait partie
        """
        return await Question.get(self.__idQuiz,self.__idQuestion, self.__db)
    
    async def getEstValide(self) -> int:
        """Accésseur qui retourne si le choix courant est la bonne réponse
        
        Returns:
            int: Si le choix courant est la bonne réponse (0 ou 1) de sa question et de son quiz correspondant
        """
        return self.__estValide
    

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

class Instance(object):
    """Classe d'instance de la table Instance (ou "Game" de Quiz)
    
    Permet l'instanciation d'objets correspondant à une ligne de la table Instance
    permet la récupération des données correspondant dans la base de donnée.
    """    

    @staticmethod
    async def __increaseInstanceCount(idQuiz: int, db: aiosqlite.core.Connection) -> None:
        """Méthode de classe privée qui permet d'accroître de 1 le nombre d'instance d'un Quiz
        
        Args:
            idQuiz (int): Identifiant du Quiz dont on veut accroître de 1 l'attribut `instanceCount` (le nombre d'instanczs global du Quiz)
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        """
        await db.execute("""UPDATE Quiz SET instanceCount = instanceCount+1 WHERE idQuiz = (?)""", (idQuiz,))
        await db.commit()
    
    @staticmethod
    async def getAll(db: aiosqlite.core.Connection, idQuiz: int, idServer: int, active: bool = True) -> list:
        """Accésseur de classe qui permet de retourner une liste des instances d'Instance (ou "game" de Quiz) d'un serveur
        
        Si le paramètre `active` est True, alors seront uniquement retourné les Instances (ou "games") de quiz encore en activité dans le serveur, qui ne sont pas finies
        Sinon sera retourné une liste des Instances qui sont terminé dans le serveur d'identifiant idServer
        
        Args:
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            idQuiz (int): Identifiant du Quiz dont on veut récupérer la liste d'Instances (ou "games")
            idServer (int): Identifiant du Serveur dont ont veut récupérer les Instances
            active (bool): Si l'on veut récupérer une liste d'Instance encore actifs ou non
            
        Returns:
            list: Liste des instances d'Instance (ou "game"), actives ou non, pour un Quiz et un Serveur
        """
        if active:
            async with db.execute("""SELECT DISTINCT * FROM Instance WHERE idQuiz = (?) AND idServer = (?) AND dateFin IS NULL ORDER BY dateDeb""",(idQuiz, idServer,)) as cursor:
                allInstances = []
                async for row in cursor:
                    allInstances.append(await Instance.get(row['idInst'], db))
        else:
            async with db.execute("""SELECT DISTINCT * FROM Instance WHERE idQuiz = (?) AND idServer = (?) AND dateFin IS NOT NULL ORDER BY dateDeb""",(idQuiz, idServer,)) as cursor:
                allInstances = []
                async for row in cursor:
                    allInstances.append(await Instance.get(row['idInst'], db))
        return allInstances
    
    @staticmethod
    async def create(idQuiz: int, db: aiosqlite.core.Connection, idServer: int, multiplicateur: float = 1) -> object:
        """Méthode de classe (dites "Usine") qui permet la création d'une Instance (ou "game" de Quiz) dans la BD et retourne son instance (objet)
        
        Args:
            idQuiz (int): Identifiant du Quiz dont on veut récupérer une Instance (ou "game")
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            idServer (int): Identifiant du Serveur sur laquel on créer une Instance
            multiplicateur (float): Tel un coefficient vient multiplier le nombre de points du quiz d'identifiant idQuiz pour cette Instance
            (default 1)
        
        Returns:
            object: Instance (objet) de l'Instance (ou "game" de quiz) que l'on vient de créer
        """
        try:
            quiz = await Quiz.get(idQuiz, db)
            if not len(await quiz.getQuestions()):
                raise Exception("Le quiz n'a pas de questions")
            dateDeb = int(time.time())
            async with db.execute("INSERT INTO Instance (idQuiz, idServer, dateDeb, multiplicateur) VALUES(?,?,?,?) RETURNING idInst", (idQuiz, idServer, dateDeb, multiplicateur,)) as cursor:
                res = await cursor.fetchone()
                instId = res['idInst']
            await db.commit()
            instance = await Instance.get(instId, db)
            await Instance.__increaseInstanceCount(idQuiz, db)
        except Exception as e:
            print("[ ERROR ] On Instance.create() " + str(e))
            instance = False
        return instance
    
    @classmethod
    async def get(cls, idInst: int, db: aiosqlite.core.Connection) -> object:
        """Accésseur de classe qui permet de récupérer une instance (objet) d'Instance (ou "game" de Quiz) à l'aide de son identifiant
        
        Args:
            idInst (int): Identifiant unique de l'Instance (ou "game" de quiz) dont on veut récupérer l'instance (objet)
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance (objet) de l'Instance (ou "game" de quiz) d'identifiant idInst
        """
        async with db.execute("SELECT * FROM Instance WHERE idInst = (?)", (idInst,)) as cursor:
            instance = await cursor.fetchone()
            if not instance:
                self = False
            else:
                self = Instance()
                idInst, idQuiz, idServer, dateDeb, dateFin, multiplicateur = instance['idInst'], instance['idQuiz'], instance['idServer'], instance['dateDeb'], instance['dateFin'], instance['multiplicateur']
                self.__idQuiz = idQuiz
                self.__idInst = idInst
                self.__dateDeb = dateDeb
                self.__idServer = idServer
                self.__dateFin = dateFin
                self.__multiplicateur = multiplicateur
                self.__db = db
        return self
    
    async def getIdInst(self) -> int:
        """Accésseur qui retourne l'identifiant de l'Instance
        
        Returns:
            int: Identifiant unique de l'instance courant
        """
        return self.__idInst
    
    async def getQuiz(self) -> object:
        """Accésseur qui retourne une instace de Quiz correspondant à l'Instance (ou "game" de quiz) courant
        
        Returns:
            object: Instance du Quiz dont l'Instance (game) courante fait partie
        """
        return await Quiz.get(self.__idQuiz, self.__db)
    
    async def getIdServer(self) -> int:
        """Accésseur qui retourne l'identifiant du Serveur de l'Instance courante
        
        Returns:
            int: identifiant du Serveur de l'Instance courante
        """
        return self.__idServer
    
    async def getDateDeb(self, formated: bool = False) -> int or str:
        """Accésseur qui retourne la date de début de l'Instance courante
        
        Si le paramètre `formated` est False, alors la date de début sera retourné sous
        forme d'un integer représentant le temps Unix (ou "Epoch") de la création de l'Instance
        
        Si il est vrai, alors la date de début sera retourné sous forme de chaîne de caractères
        dans le format Jour/Mois/Année Heure:Minute:Seconde
        
        Args:
            formated (bool): Si l'on veut récupérer la date de départ en chaîne de caractères ou en integer
            (default False)
            
        Returns:
            int: La date de départ de l'Instance (game) sous forme d'integer représentant les secondes en temps Unix
            str: La date de départ de l'Instance (game) sous forme de chaîne de caractères au format Jour/Mois/Année Heure:Minute:Seconde
        """
        if formated and self.__dateDeb:
            date = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(self.__dateDeb))
        else:
            date = self.__dateDeb
        return date
    
    async def getDateFin(self, formated = False) -> int or str or None:
        """Accésseur qui retourne la date de fin de l'Instance courante
        
        Si le paramètre `formated` est False, alors la date de fin sera retourné sous
        forme d'un integer représentant le temps Unix (ou "Epoch") de la fin de l'Instance
        
        Si il est vrai, alors la date de fin sera retourné sous forme de chaîne de caractères
        dans le format Jour/Mois/Année Heure:Minute:Seconde
        
        Args:
            formated (bool): Si l'on veut récupérer la date de fin en chaîne de caractères ou en integer
            (default False)
        
        Returns:
            int: La date de fin de l'Instance (game) sous forme d'integer représentant les secondes en temps Unix
            str: La date de fin de l'Instance (game) sous forme de chaîne de caractères au format Jour/Mois/Année Heure:Minute:Seconde
            None: L'Instance (game) n'est pas terminé donc la date de fin est Null
        """
        if formated and self.__dateFin:
            date = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(self.__dateFin))
        else:
            date = self.__dateFin
        return date
    
    async def getMultiplicateur(self) -> float:
        """Accésseur qui retourne le multiplicateur de l'Instance courante
        
        Returns:
            float: Multiplicateur de l'Instance courante
        """
        return self.__multiplicateur
    
    async def setDateFin(self, dateFin: int = None) -> None:
        """Modificateur qui permet de mettre en place la date de fin de l'Instance courante
        
        Si le paramètre `dateFin` est Null, alors la date de fin sera mis à la date courante lors de l'appel de la fonction
        
        Args:
            dateFin (int): Date de fin en secondes UNIX (Epoch) à affecter à l'Instance courante  
        """
        
        if not dateFin:
            dateFin = int(time.time())
        await self.__db.execute("""UPDATE Instance SET dateFin = (?) WHERE idInst = (?)""", (dateFin,self.__idInst,))
        await self.__db.commit()   
        self.__dateFin = dateFin

    async def getReponses(self, snowflake: int) -> list:
        """Accésseur qui retourne une liste d'instances de Réponse d'un utilisateur correspondant aux réponses de l'Instance (game) courante
        
        Args:
            snowflake (int): Identifiant discord Unique d'un utilisateur dont on veut récupérer les réponses à l'Instance (game) courante
        
        Returns:
            list: Liste des instances de Réponse de l'utilisateur d'identifiant snowflake pour l'Instance (game) courante
        
        """
        return await Reponse.getAll(self.__idInst, snowflake)
    
    async def getMoyenne(self, echelle: float = None, avecPoints: bool = False) -> float or tuple:
        """Accesseur qui récupère la moyenne de l'Instance (game) courante
        
        Args:
            echelle (float): Si une echelle est passé la moyenne sera retourné sur cette échelle (ex: 5/10 avec une échelle de 20 -> 10/20)
            (default None)
            avecPoints (bool): Définie si la function doit retourner le nombre de points (sur combien la moyenne est basé, n'est pris en compte que si echelle est None)
            (default False)
        
        Returns:
            float: Moyenne de l'Instance (game courante)
            tuple: Moyenne de l'Instance (game courante) avec le nombre de points
        """
        quiz = await self.getQuiz()
        nbPoints = await quiz.getPoints()
        async with self.__db.execute("SELECT SUM(r.estCorrecte), COUNT(r.estCorrecte) FROM Reponse r, Instance i WHERE r.idInst = i.idInst and i.idInst = (?)", (self.__idInst,)) as cursor:
            res = await cursor.fetchone()
            nbCorrectes, nbNotes = res[0], res[1]
            if echelle:
                moyenne = (nbCorrectes*nbPoints*self.__multiplicateur / nbNotes)/nbPoints*echelle
            else:
                if avecPoints:
                    moyenne = (nbCorrectes*nbPoints*self.__multiplicateur / nbNotes, nbPoints*self.__multiplicateur)
                else:
                    moyenne = nbCorrectes*nbPoints*self.__multiplicateur /nbNotes
        return moyenne
    
    async def getClassement(self) -> list:
        """Accésseur qui retourne le classement des utilisateurs ayant participer à l'Instance courante
        
        L'accésseur retourne une liste de tuples pour chaque participant. Un tuple (representant une ligne de la BD) est composé
        d'une instance de l'Utilisateur (participant)et de son nombre de réponses correctes dans l'Instance courante (trié par nombre de réponses correctes décroissant)
        
        Returns:
            list: Liste des tuples correspondant au classement des participants de l'Instance courante
        """
        async with self.__db.execute("SELECT idDiscord, SUM(estCorrecte) FROM Instance i, Reponse r WHERE i.idInst = r.idInst AND i.idInst = (?) GROUP BY idDiscord ORDER BY 2 DESC, 1 LIMIT 10",(self.__idInst,)) as cursor:
            classement = []
            async for row in cursor:
                idDiscord, nbCorrect = row[0], row[1]
                classement.append((await Utilisateur.get(idDiscord,self.__idServer,self.__db), nbCorrect))
            return classement
        
    async def getReponsesTrie(self) -> list:
        """Accésseur qui retourne une liste des questions triées par nombre de réponses correctes (décroissant)
        
        La liste est composé de tuples, chaque tuple représente une ligne et est composé de: l'instance de Question correspondant et le nombre de réponses de correctes cette
        question a reçu dans l'Instance courante à travers tout les participants. Le premier tuple représentant donc la question ayant reçu le plus de réponses correctes,
        le dernier élément étant son inverse.
        
        Returns:
            list: Liste des tuples correspondant au classement des questions lieux mieux réussies
        """
        async with self.__db.execute("SELECT idQuestion, SUM(estCorrecte) FROM Instance i, REPONSE r WHERE i.idInst = r.idInst AND i.idInst = (?) GROUP BY idQuestion ORDER BY 2 DESC, 1",(self.__idInst,)) as cursor:
            reponses = []
            async for row in cursor:
                idQuestion, nbCorrect = row[0], row[1]
                reponses.append((await Question.get(self.__idQuiz, idQuestion, self.__db), nbCorrect))
            return reponses
    
    async def getNbParticipants(self) -> int:
        """Accésseur au nombre de participants de l'Instance courante  ("game" de Quiz)
        
        Returns:
            int: Le nombre d'utilisateurs ayant participé à la "game"/Instance courante
        """
        async with self.__db.execute("SELECT COUNT(DISTINCT idDiscord) FROM Instance i, REPONSE r WHERE i.idInst = r.idInst AND i.idInst = (?) GROUP BY i.idInst",(self.__idInst,)) as cursor:
            res = await cursor.fetchone()
        return res[0]

    async def getNbCorrectes(self, snowflake: int) -> int:
        """Accésseur qui retourne le nombre de réponses correctes qu'un utilisateur (participant) areçu pour l'Instance courante
        
        Args:
            snowflake (int): Identifiant discord unique d'un participant à l'Instance courante
            
        Returns:
            int: Nombre de réponses correctes qu'a reçu le participant d'identifiant `snowflake` pour l'Instance courante
        """
        async with self.__db.execute("SELECT SUM(estCorrecte) FROM Instance i, REPONSE r WHERE i.idInst = r.idInst AND i.idInst = (?) AND idDiscord = (?)",(self.__idInst, snowflake)) as cursor:
            res = await cursor.fetchone()
        return res[0]
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

class Reponse(object):
    """Classe d'instance de la table Reponse
    
    Permet l'instanciation d'objets correspondant à une ligne de la table Reponse
    permet la récupération des données correspondant dans la base de donnée.
    """    
    
    @staticmethod
    async def __addGrade(snowflake: int, idInst: int, idServer: int, quiz: Quiz, db: aiosqlite.core.Connection) -> None:
        """Méthode de classe privée qui vient ajouter une note au score d'un utilisateur
        
        La méthode vient prendre en compte le nombre de points du Quiz correspondant et du multiplicateur de l'Instance
        pour ajouter une note au participant d'une Instance ("game" d'un Quiz)
                
        Args:
            snowflake (int): Identifiant discord unique d'un participant auquel on veut ajouter des points
            idInst (int): Identifiant de l'Instance auquel participe l'utilisateur auqel on veut ajouter des points
            idServer (int): Serveur sur lequel a lieu l'Instance
            quiz (Quiz): Instance de Quiz correspondant
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        
        """
        
        user = await Utilisateur.get(snowflake, idServer, db)
        quizInstance = await Instance.get(idInst, db)
        points = await quiz.getPoints()*await quizInstance.getMultiplicateur()/await quiz.getNbQuestions()
        await user.addPoints(points, idServer)        
    
    @staticmethod
    async def __estValide(idQuiz: int, idQuestion: int, idChoix: int, db: aiosqlite.core.Connection) -> int:
        """Méthode de classe privée qui permet de vérifier si un choix est correcte ou non
        
        Args:
            idQuiz (int): Identifiant du quiz auquel est lié la question
            idQuestion (int): Identifiant (ou Numéro) de la question dont on veut vérifier un choix
            idChoix (int): Identifiant (ou Numéro) du choix dont on veut vérifier la validité
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            int: Si le choix passé est la bonne réponse de la question (1) ou non (0)
            
        """
        
        choix = await Choix.get(idQuiz, idQuestion, idChoix, db) # Si aucun choix n'est émis (idChoix = 0), alors choix = False
        valide = 0
        if choix and await choix.getEstValide():
            valide = 1
        return valide
    
    @staticmethod
    async def __increaseParticipations(idInst: int, idDiscord: int, idServer: int, db: aiosqlite.core.Connection) -> None:
        """Méthode de classe privée qui vient accroître le nombre de participations total d'un Utilisateur
        
        Args:
            idInst (int): Identifiant de l'Instance ("game" du Quiz) représentant une nouvelle participation
            idServer (int): Identifiant du serveur
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        
        """
        async with db.execute("SELECT COUNT(DISTINCT idRep) FROM Reponse WHERE idInst = (?) AND idDiscord = (?)", (idInst, idDiscord,)) as cursor:
            res = await cursor.fetchone()
            if not res[0]:
                await db.execute("UPDATE Statistiques SET nbParticipations = nbParticipations + 1 WHERE idDiscord = (?) AND idServer = (?)", (idDiscord, idServer,))
                await db.commit()
    
    @staticmethod
    async def getAll(db: aiosqlite.core.Connection, idInst: int, snowflake: int) -> list:
        """Accesseur de classe qui permet de retourner une liste d'instances de Reponse d'un utilisateur pour une Instance (ou "game" de quiz)
        

        Args:
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            idInst (int): Identifiant de l'Instance (ou "game") dont on veut récupérer les réponses
            snowflake (int): Identifiant unique Discord de l'utilisateur dont on veut récupérer les réponses

        Returns:
            list: Liste des instances de Réponse correspondant à l'utilisateur `snowflake` sur l'Instance (ou "game") `idInst`

        """
        if idInst is not None:
            async with db.execute("""SELECT DISTINCT * FROM Reponse WHERE idInst = (?) AND idDiscord = (?)""",(idInst, snowflake,)) as cursor:
                allReponse = []
                async for row in cursor:
                    allReponse.append(await Reponse.get(row['idRep'], db))
        else:
            async with db.execute("""SELECT DISTINCT * FROM Reponse WHERE idDiscord = (?)""",(snowflake,)) as cursor:
                allReponse = []
                async for row in cursor:
                    allReponse.append(await Reponse.get(row['idRep'], db))            
        return allReponse
    
    @staticmethod
    async def create(idInst: int, idQuestion: int, idChoix: int, snowflake: int, db: aiosqlite.core.Connection) -> object:
        """Méthode de classe (dites "Usine") qui permet de créer une réponse dans la BD et de retourner son Instance de Reponse.
        
        Args:
            idInst (int): Identifiant du Quiz auquel on veut ajouter une réponse
            idQuestion (int): Identifiant (ou numéro) de la question auquel on veut ajouter une réponse
            idChoix (int): Identifiant (ou numéro) du choix que l'on veut ajouter comme réponse
            snowflake (int): Identifiant unique Discord de l'utilisateur auquel on veut ajouter une réponse
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite

        Returns:
            object: Instance de Réponse que l'on vient d'ajouter dans la BD
        """
        try:
            instance = await Instance.get(idInst, db)
            idServer = await instance.getIdServer()
            quiz = await instance.getQuiz()
            idQuiz = await quiz.getIdQuiz()
            estValide = await Reponse.__estValide(idQuiz, idQuestion, idChoix, db)
            async with db.execute("INSERT INTO Reponse (idQuiz, idQuestion, idChoix, idDiscord, idInst, estCorrecte) VALUES(?,?,?,?,?,?) RETURNING idRep", 
                                  (idQuiz, idQuestion, idChoix, snowflake, idInst, estValide,)) as cursor:
                res = await cursor.fetchone()
                idRep = res['idRep']
            await db.commit()
            instance = await Reponse.get(idRep, db)
            if estValide:
                await Reponse.__addGrade(snowflake, idInst, idServer, quiz, db)
            await Reponse.__increaseParticipations(idInst, snowflake, idServer, db)
        except Exception as e:
            print("[ ERROR ] On Reponse.create() " + str(e))
            instance = False
        return instance
    
    @classmethod
    async def get(cls, idRep: int, db: aiosqlite.core.Connection) -> object:
        """Accésseur qui permet de retourner une instance de Réponse à partir de son identifiant
        
        Args:
            idRep (int): Identifiant unique de la réponse dont on veut récupérer l'instance
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance de Réponse d'identifiant idRep

        """
        async with db.execute("SELECT * FROM Reponse WHERE idRep = (?)", (idRep,)) as cursor:
            rep = await cursor.fetchone()
            if not rep:
                self = False
            else:
                self = Reponse()
                idRep, idQuiz, idQuestion, idChoix, idDiscord, idInst, estCorrecte = rep['idRep'], rep['idQuiz'], rep['idQuestion'], rep['idChoix'], rep['idDiscord'], rep['idInst'], rep['estCorrecte']
                self.__idRep = idRep
                self.__idQuiz = idQuiz
                self.__idQuestion = idQuestion
                self.__idChoix = idChoix
                self.__idDiscord = idDiscord
                self.__idInst = idInst
                self.__estCorrecte = estCorrecte
                self.__db = db
        return self
    
    async def estCorrecte(self) -> int:
        """Accésseur qui retourne si l'instance de Réponse courante représente une bonne Réponse
        
        Returns:
            int: Si l'instance courante est une réponse Correcte (1) ou non (0)
        """
        return self.__estCorrecte
    
    async def getIdRep(self) -> int:
        """Accésseur qui retourne l'identifiant de l'instance de Reponse courante
        
        Returns:
            int: Identifiant de l'instance courante
        """
        return self.__idRep
    
    async def getUtilisateur(self, idServer: int) -> object:
        """Accésseur qui retourne l'instance d'Utilisateur correspondant à l'utilisateur de l'instance de Réponse courante
        
        Args:
            idServer (int): Identifiant du serveur Discord pour lequel on veut récupérer l'utilisateur
        
        Returns:
            object: Instance d'Utilisateur correspondant au créateur de l'instance de Réponse courant
        """
        return await Utilisateur.get(self.__idDiscord, idServer, self.__db)
    
    async def getInstance(self) -> object:
        """Accesseur qui retourne l'instance d'Instance (ou "game" de Quiz) correspondant à la réponse courante
        
        Returns:
            object: Instance d'Instance (ou "game" de quiz) correspondant à l'instance de Réponse courante
        """
        return await Instance.get(self.__idInst, self.__db)
    
    async def getQuiz(self) -> object:
        """Accesseur qui retourne l'instance de Quiz correspondant à la réponse courante
        
        Returns:
            object: Instance de Quiz auquelle l'instance de Reponse courante est liée
        """
        return await Quiz.get(self.__idQuiz, self.__db)
    
    async def getQuestion(self) -> object:
        """Accesseur qui retourne l'instance de Question correspondant à la réponse courante
        
        Returns:
            object: Instance de Question auquelle l'instance de Reponse courante est liée
        """
        return await Question.get(self.__idQuiz,self.__IdQuestion, self.__db)
    
    async def getChoix(self) -> object or False:
        """Accesseur qui retourne l'instance de Choix correspondant à la réponse courante
        
        Returns:
            object: Instance de Choix auquelle l'instance de Reponse courante est liée
        """
        if self.__idChoix:
            return await Choix.get(self.__idQuiz, self.__idQuestion, self.__idChoix, self.__db)
        else:
            return False
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

class Statistiques(object):
    """Classe d'instance de la table Statistiques
    
    Permet l'instanciation d'objets correspondant à une ligne de la table Statistiques
    permet la récupération des données correspondant dans la base de donnée.
    """    
    
    @staticmethod
    async def __aenumerate(ait: iter, start: int = 0) -> tuple:
        """Méthode de classe qui permet de reproduire la fonctionnalité de `enumerate`
        
        La fonction enumerate() en python permet d'énumerer un Itérable ou un Generator. Mais enumerate()
        ne fonctionne pas pour les itérables/generators asynchronisés. Cette fonction permet de reproduire
        les fonctionalités d'enumerate pour un Itérable ou un Generator asynchronisé
        
        Args:
            ait (iter): Iterable/Generator asynchronisé à énumerer
            start (int): Permet de définir un point de départ
            (default 0)
        
        Returns:
            tuple: Generator contenant l'élément énuméré et son énumération (tel le ferai enumerate())
        """
        i = start
        async for item in ait:
            yield i, item
            i += 1
        
    @staticmethod
    async def clearLeaderboard(idServer: int, db: aiosqlite.core.Connection) -> None:
        """Méthode de classe qui permet pour un serveur donner de remettre à 0 les scores de joueurs et le leaderboard
        
        Args:
            idServer (int): Id du serveur dont on veut reinitialiser les scores
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
        
        """
        
        await db.execute("UPDATE Statistiques SET nbParticipations = 0, scoreTotal = 0 WHERE idServer = (?)",(idServer,))
        await db.commit()
    
    @staticmethod
    async def create(idServer: int, idDiscord: int, db: aiosqlite.core.Connection) -> object:
        """Méthode de classe (dites "Usine") qui permet la création d'une ligne de Statistiques pour
        un utilisateur dans un Serveur, puis retourne l'instance de Statistiques de la ligne créée.
        
        Args:
            idServer (int): Identifiant du Serveur 
            idDiscord (int): Identifiant de l'utilisateur auquel lier les statistiques
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance de Statistiques que l'on vient de créer
        """
        try:
            await db.execute("INSERT INTO Statistiques (idServer, idDiscord) VALUES(?,?)", (idServer, idDiscord,))
            await db.commit()
            instance = await Statistiques.get(idServer, idDiscord, db)
        except Exception as e:
            print("[ ERROR ] On Statistiques.create() " + str(e))
            instance = False
        return instance
    
    @staticmethod
    async def getAll(db: aiosqlite.core.Connection, idServer: int) -> list:
        """Méthode de classe qui retourne une liste des instances de Statistiques pour un serveur donné
        
        Args:
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            idServer (int): Identifiant unique du Serveur Discord depuis lequel on veut récupérer les statistiques de chaque joueur
        
        Returns:
            list: Liste d'instance de Statistiques pour chaque joueur du serveur d'identifiant `idServer`
        """
        async with db.execute("""SELECT DISTINCT * FROM Statistiques WHERE idServer = (?)""",(idServer,)) as cursor:
            allStats = []
            async for row in cursor:
                allStats.append(await Statistiques.get(row['idServer'], row['idDiscord'], db))
        return allStats


    @classmethod
    async def get(cls, idServer: int, snowflake: int, db: aiosqlite.core.Connection) -> object:
        """Accésseur qui permet de retourner une instance de Statistiques à partir de l'identifiant d'un utilisateur et d'un serveur
        
        Args:
            idServer (int): Identifiant unique du serveur Discord dont on veut récupérer les statistiques
            snowflake (int): Identifiant unique d'un utilisateur Discord dont on veut récupérer les statistiques
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite
            
        Returns:
            object: Instance de Statistiques correspondant

        """        
        async with db.execute("SELECT * FROM Statistiques WHERE idServer = (?) AND idDiscord = (?)", (idServer, snowflake,)) as cursor:
            stats = await cursor.fetchone()
            if not stats:
                self = False
            else:
                self = Statistiques()
                idServer, idDiscord, nbParticipations, scoreTotal = stats['idServer'], stats['idDiscord'], stats['nbParticipations'], stats['scoreTotal']
                self.__idServer = idServer
                self.__idDiscord = idDiscord
                self.__nbParticipations = nbParticipations
                self.__scoreTotal = scoreTotal
                self.__db = db
                
        return self
    
    async def getUser(self) -> object:
        """Accesseur qui retourne l'Instance de Utilisateur correspondant au joueur de l'instance courante
        
        Returns:
            object: Instance d'utilisateur correspondant au joueur de l'instance de Statistiques courante
        """
        return await Utilisateur.get(self.__idDiscord, self.__idServer, self.__db)
    
    async def getIdServer(self) -> int:
        """Accésseur qui retourne l'identifiant du Serveur correspondant à l'instance courante
        
        Returns:
            int: Identifiant du Serveur correspondant à l'instance de Statistiques courante
        """
        return self.__idServer
    
    async def getIdDiscord(self) -> int:
        """Accésseur qui retourne l'identifiant de l'utilisateur correspondant à l'instance courante
        
        Returns:
            int: Identifiant de l'utilisateur correspondant à l'instance de Statistiques courante
        """
        return self.__idDiscord
    
    async def getNbParticipations(self) -> int:
        """Accésseur qui retourne le nombre de participations d'un utilisateur
        
        Returns:
            int: Nombre de participation à un quiz de la part de l'utilisateur dans le serveur lié à l'instance courante de Statistiques
        """
        return self.__nbParticipations
    
    async def getScoreTotal(self, globale : bool = False) -> float:
        """Accésseur qui retourne le score Total d'un utilisateur
        
        Si globale est True, alors la méthode retournera le scoreTotale de l'utilisateur, tout serveurs confondus
        Sinon, ce sera le scoreTotal pour le serveur lié à l'instance courante de Statistiques
        
        Args:
            globale (bool): Si l'on récupère le scoreTotal du serveur courant ou tout serveurs confonduss
        Returns:
            float: ScoreTotal de l'utilisateur (pour un serveur ou globale)
        """
        scoreTotal = self.__scoreTotal
        if globale:
            async with self.__db.execute("""SELECT SUM(scoreTotal) FROM Statistiques WHERE idDiscord = (?)""",(self.__idDiscord,)) as cursor:
                res = await cursor.fetchone()
                if res and res[0]:
                    scoreTotal = res[0]
        return scoreTotal
    
    @staticmethod
    async def getLeaderboard(idServer: int, db: aiosqlite.core.Connection) -> list:
        """Méthode de classe qui permet de retourner le classement des joueurs d'un serveur
        
        Args:
            idServer (int): Identifiant unique du serveur Discord dont on veut récupérer le classement des joueurs
            db (aiosqlite.core.Connection): Connection à la bd via aiosqlite

        Returns:
            list: Liste de tuples contenant pour chaque joueur du serveur l'instance de Utilisateur et l'instance de Statistiques correspondant
        """
        async with db.execute("""SELECT * FROM Statistiques WHERE idServer = (?) ORDER BY scoreTotal DESC""",(idServer,)) as cursor:
            allUsers = []
            async for index, row in Statistiques.__aenumerate(cursor):
                if index >= 10:
                    break
                allUsers.append([await Utilisateur.get(row['idDiscord'], idServer, db), await Statistiques.get(row['idServer'], row['idDiscord'], db)])

        return allUsers