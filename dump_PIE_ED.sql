CREATE DATABASE IF NOT EXISTS PIE_ED;
USE PIE_ED;

DROP TABLE IF EXISTS Obtiene, Otorga, Contiene, Responde, Juega, Crea, Respuesta,
    Alumno, Tema, Logro, Pregunta, Profesor;

CREATE TABLE Alumno (
    Alumno_ID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Correo VARCHAR(255) UNIQUE
);

CREATE TABLE Tema (
    Tema_ID VARCHAR(100) PRIMARY KEY
);

CREATE TABLE Logro (
    Logro_ID INT PRIMARY KEY,
    Alias VARCHAR(100)
);

CREATE TABLE Pregunta (
    Pregunta_ID INT PRIMARY KEY,
    Tema VARCHAR(100),
    Enunciado TEXT,
    Dificultad ENUM('Facil', 'Media', 'Dificil'),
    Puntuacion INT
);

CREATE TABLE Profesor (
    Profesor_ID INT PRIMARY KEY,
    Correo VARCHAR(255) UNIQUE
);

CREATE TABLE Respuesta (
    Respuesta_ID INT,
    Pregunta_ID INT,
    Solucion ENUM('Correcta', 'Incorrecta'),
    Contenido TEXT,
    PRIMARY KEY (Respuesta_ID, Pregunta_ID),
    FOREIGN KEY (Pregunta_ID) REFERENCES Pregunta(Pregunta_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Juega (
    Alumno_ID INT,
    Tema_ID VARCHAR(100),
    Fecha DATE,
    Puntuacion INT,
    Intento INT,
    PRIMARY KEY (Alumno_ID, Tema_ID, Intento),
    FOREIGN KEY (Alumno_ID) REFERENCES Alumno(Alumno_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID)
);

CREATE TABLE Responde (
    Alumno_ID INT,
    Pregunta_ID INT,
    Fecha DATE,
    Hora TIME,
    Puntuacion INT,
    PRIMARY KEY (Alumno_ID, Pregunta_ID, Fecha, Hora),
    FOREIGN KEY (Alumno_ID) REFERENCES Alumno(Alumno_ID),
    FOREIGN KEY (Pregunta_ID) REFERENCES Pregunta(Pregunta_ID)
);

CREATE TABLE Crea (
    Profesor_ID INT,
    Tema_ID VARCHAR(100),
    Fecha DATE,
    Hora TIME,
    PRIMARY KEY (Profesor_ID, Tema_ID),
    FOREIGN KEY (Profesor_ID) REFERENCES Profesor(Profesor_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID)
);

CREATE TABLE Otorga (
    Logro_ID INT,
    Tema_ID VARCHAR(100),
    Puntuacion_Maxima INT,
    PRIMARY KEY (Logro_ID, Tema_ID),
    FOREIGN KEY (Logro_ID) REFERENCES Logro(Logro_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID)
);

CREATE TABLE Obtiene (
    Alumno_ID INT,
    Logro_ID INT,
    PRIMARY KEY (Alumno_ID, Logro_ID),
    FOREIGN KEY (Alumno_ID) REFERENCES Alumno(Alumno_ID),
    FOREIGN KEY (Logro_ID) REFERENCES Logro(Logro_ID)
);

CREATE TABLE Contiene (
    Tema_ID VARCHAR(100),
    Pregunta_ID INT,
    PRIMARY KEY (Tema_ID, Pregunta_ID),
    FOREIGN KEY (Tema_ID) REFERENCES Tema(Tema_ID),
    FOREIGN KEY (Pregunta_ID) REFERENCES Pregunta(Pregunta_ID)
);

-- Insertar datos de ejemplo
INSERT INTO Tema (Tema_ID) VALUES 
    ('Tema pruebas aplicacion 1'),
    ('Tema pruebas aplicacion 2');

INSERT INTO Pregunta (Pregunta_ID, Tema, Enunciado, Dificultad, Puntuacion) VALUES
    (1, 'Tema pruebas aplicacion 1', '¿2+2?', 'Facil', 1),
    (2, 'Tema pruebas aplicacion 2', 'Empareja correctamente', 'Media', 2);

INSERT INTO Respuesta (Respuesta_ID, Pregunta_ID, Solucion, Contenido) VALUES
    -- Respuestas para pregunta 1 (¿2+2?)
    (1, 1, 'Correcta', '4'),
    (2, 1, 'Incorrecta', '5'),
    (3, 1, 'Incorrecta', '7'),
    (4, 1, 'Incorrecta', 'Viva er Betih'),
    -- Respuestas para pregunta 2 (Empareja correctamente)
    (1, 2, 'Correcta', '2+2 -> 4'),
    (2, 2, 'Correcta', '3+3 -> 6'),
    (3, 2, 'Correcta', '5+5 -> 10');

INSERT INTO Contiene (Tema_ID, Pregunta_ID) VALUES
    ('Tema pruebas aplicacion 1', 1),
    ('Tema pruebas aplicacion 2', 2);
