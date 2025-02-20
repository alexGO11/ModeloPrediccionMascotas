DROP TABLE test;
DROP TABLE mascota;
DROP TABLE codigo_postal_adyacente;
DROP TABLE codigo_postal;

CREATE TABLE codigo_postal (
    cod_postal INT PRIMARY KEY,
    latitud FLOAT,
    longitud FLOAT
);

CREATE TABLE codigo_postal_adyacente (
    cod_postal_origen INT,
    cod_postal_adyacente INT,
    PRIMARY KEY (cod_postal_origen, cod_postal_adyacente),
    FOREIGN KEY (cod_postal_origen) REFERENCES codigo_postal(cod_postal),
    FOREIGN KEY (cod_postal_adyacente) REFERENCES codigo_postal(cod_postal)
);

CREATE TABLE test (
    id_test SERIAL PRIMARY KEY,
    cod_postal INT REFERENCES codigo_postal(cod_postal),
	cantidad_casos INT DEFAULT 0,
    fecha DATE NOT NULL,
    enfermedad VARCHAR(50) NOT NULL,
    resultado BOOLEAN NOT NULL,  -- TRUE = positivo, FALSE = negativo
    ciudad VARCHAR(50),
    edad INT,
    sexo VARCHAR(10)  
);

INSERT INTO codigo_postal (cod_postal, latitud, longitud) VALUES 
(28001, 40.4218, -3.6844),
(28002, 40.4490, -3.6783),
(28003, 40.4415, -3.7038);

INSERT INTO codigo_postal_adyacente (cod_postal_origen, cod_postal_adyacente) VALUES 
(28001, 28002),
(28002, 28003),
(28003, 28001);

-- Insertando pruebas médicas
INSERT INTO test (cod_postal, cantidad_casos, fecha, enfermedad, resultado, ciudad, edad, sexo) VALUES
(28001, 5, '2024-02-01', 'Leishmania', TRUE, 'Madrid', 30, 'Macho'),
(28002, 2, '2024-02-02', 'Giardia', FALSE, 'Madrid', 25, 'Hembra'),
(28003, 10, '2024-02-03', 'Leishmania', TRUE, 'Madrid', 40, 'Hembra');

-- Obtener adyacentes de un CP
SELECT cod_postal_adyacente 
FROM codigo_postal_adyacente 
WHERE cod_postal_origen = '28001';

-- Obtener todas las pruebas positivas en un código postal específico
SELECT * FROM test 
WHERE cod_postal = 28001 AND resultado = TRUE;

-- Contar el número total de casos positivos por enfermedad
SELECT enfermedad, COUNT(*) AS total_casos
FROM test
WHERE resultado = TRUE
GROUP BY enfermedad;