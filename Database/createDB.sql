CREATE TABLE Utilisateur(
   idDiscord INT NOT NULL PRIMARY KEY,
   name VARCHAR(50)
);

CREATE TABLE Quiz(
   idQuiz INTEGER NOT NULL PRIMARY KEY,
   instanceCount INT NOT NULL DEFAULT 0,
   points DOUBLE DEFAULT 1,
   titre VARCHAR(30),
   idDiscord INT NOT NULL REFERENCES Utilisateur(idDiscord) ON DELETE SET NULL
);

CREATE TABLE Statistiques(
   idServer INT,
   nbParticipations INT DEFAULT 0,
   scoreTotal INT DEFAULT 0,
   idDiscord INT NOT NULL,
   PRIMARY KEY(idServer, idDiscord),
   FOREIGN KEY(idDiscord) REFERENCES Utilisateur(idDiscord) ON DELETE CASCADE
);

CREATE TABLE Question(
   idQuiz INTEGER NOT NULL,
   idQuestion INT NOT NULL,
   titre VARCHAR(100) NOT NULL,
   PRIMARY KEY(idQuiz, idQuestion),
   FOREIGN KEY(idQuiz) REFERENCES Quiz(idQuiz) ON DELETE CASCADE
);

CREATE TABLE Choix(
   idQuiz INTEGER NOT NULL,
   idQuestion INT NOT NULL,
   idChoix INT NOT NULL,
   titre VARCHAR(50) NOT NULL,
   estValide INT NOT NULL DEFAULT 0,
   PRIMARY KEY(idQuiz, idQuestion, idChoix),
   FOREIGN KEY(idQuiz, idQuestion) REFERENCES Question(idQuiz, idQuestion) ON DELETE CASCADE
);

CREATE TABLE Instance(
   idInst INTEGER NOT NULL,
   dateDeb INT NOT NULL,
   dateFin INT,
   multiplicateur DOUBLE DEFAULT 1,
   idServer INT NOT NULL,
   idQuiz INTEGER NOT NULL,
   PRIMARY KEY(idInst),
   FOREIGN KEY(idQuiz) REFERENCES Quiz(idQuiz) ON DELETE SET NULL
);

CREATE TABLE Reponse(
   idRep INTEGER NOT NULL,
   estCorrecte INT NOT NULL,
   idInst INTEGER NOT NULL,
   idDiscord INT NOT NULL,
   idQuiz INTEGER NOT NULL,
   idQuestion INT NOT NULL,
   idChoix INT NOT NULL,
   PRIMARY KEY(IdRep),
   FOREIGN KEY(idInst) REFERENCES Instance(idInst) ON DELETE CASCADE,
   FOREIGN KEY(idDiscord) REFERENCES Utilisateur(idDiscord) ON DELETE SET NULL,
   FOREIGN KEY(idQuiz, idQuestion, idChoix) REFERENCES Choix(idQuiz, idQuestion, idChoix) ON DELETE CASCADE
);
