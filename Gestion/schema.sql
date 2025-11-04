CREATE DATABASE IF NOT EXISTS PIE_ED CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE PIE_ED;

DROP TABLE IF EXISTS Obtiene, Otorga, Contiene, Responde, Juega, Crea, Respuesta,
    Alumno, Tema, Logro, Pregunta, Profesor;

CREATE TABLE Alumno (
    Alumno_ID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Correo VARCHAR(255) UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Tema (
    Tema_ID VARCHAR(100) PRIMARY KEY
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Logro (
    Logro_ID INT PRIMARY KEY,
    Alias VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Pregunta (
    Pregunta_ID INT PRIMARY KEY,
    Tema VARCHAR(100),
    Enunciado TEXT,
    Dificultad ENUM('Facil', 'Media', 'Dificil'),
    Puntuacion INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Profesor (
    Profesor_ID INT PRIMARY KEY,
    Correo VARCHAR(255) UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Respuesta (
    Respuesta_ID INT,
    Pregunta_ID INT,
    Solucion ENUM('Correcta', 'Incorrecta'),
    Contenido TEXT,
    PRIMARY KEY (Respuesta_ID, Pregunta_ID),
    FOREIGN KEY (Pregunta_ID) REFERENCES Pregunta(Pregunta_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Juega (
    Alumno_ID INT,
    Tema_ID VARCHAR(100),
    Fecha DATE,
    Puntuacion INT,
    Intento INT,
    PRIMARY KEY (Alumno_ID, Tema_ID, Intento),
    FOREIGN KEY (Alumno_ID) REFERENCES Alumno(Alumno_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Responde (
    Alumno_ID INT,
    Pregunta_ID INT,
    Fecha DATE,
    Hora TIME,
    Puntuacion INT,
    PRIMARY KEY (Alumno_ID, Pregunta_ID, Fecha, Hora),
    FOREIGN KEY (Alumno_ID) REFERENCES Alumno(Alumno_ID),
    FOREIGN KEY (Pregunta_ID) REFERENCES Pregunta(Pregunta_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Crea (
    Profesor_ID INT,
    Tema_ID VARCHAR(100),
    Fecha DATE,
    Hora TIME,
    PRIMARY KEY (Profesor_ID, Tema_ID),
    FOREIGN KEY (Profesor_ID) REFERENCES Profesor(Profesor_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Otorga (
    Logro_ID INT,
    Tema_ID VARCHAR(100),
    Puntuacion_Maxima INT,
    PRIMARY KEY (Logro_ID, Tema_ID),
    FOREIGN KEY (Logro_ID) REFERENCES Logro(Logro_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Obtiene (
    Alumno_ID INT,
    Logro_ID INT,
    PRIMARY KEY (Alumno_ID, Logro_ID),
    FOREIGN KEY (Alumno_ID) REFERENCES Alumno(Alumno_ID),
    FOREIGN KEY (Logro_ID) REFERENCES Logro(Logro_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Contiene (
    Tema_ID VARCHAR(100),
    Pregunta_ID INT,
    PRIMARY KEY (Tema_ID, Pregunta_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID),
    FOREIGN KEY (Pregunta_ID) REFERENCES Pregunta(Pregunta_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
