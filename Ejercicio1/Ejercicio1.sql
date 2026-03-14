-- Crear tablas para almacenar datos de costos y envejecimiento de países
CREATE TABLE pais_costos (
    _id VARCHAR(50) PRIMARY KEY,
    continente VARCHAR(100),
    pais VARCHAR(100),
    poblacion BIGINT,
    costo_bajo_hospedaje NUMERIC(10,2),
    costo_promedio_comida NUMERIC(10,2),
    costo_bajo_transporte NUMERIC(10,2),
    costo_promedio_entretenimiento NUMERIC(10,2)
);

CREATE TABLE pais_envejecimiento (
    id_pais INT PRIMARY KEY,
    nombre_pais VARCHAR(100),
    capital VARCHAR(100),
    continente VARCHAR(100),
    region VARCHAR(100),
    poblacion BIGINT,
    tasa_de_envejecimiento NUMERIC(10,2)
);

-- verificar datos nulos o vacíos en pais_costos y pais_envejecimiento
SELECT *
FROM pais_costos
WHERE pais IS NULL OR TRIM(pais) = '';

SELECT *
FROM pais_envejecimiento
WHERE nombre_pais IS NULL OR TRIM(nombre_pais) = '';

# ver duplicados en pais_costos y pais_envejecimiento
SELECT pais, COUNT(*)
FROM pais_costos
GROUP BY pais
HAVING COUNT(*) > 1;

SELECT nombre_pais, COUNT(*)
FROM pais_envejecimiento
GROUP BY nombre_pais
HAVING COUNT(*) > 1;

-- verificar datos nulos en la columna de población en ambas tablas
SELECT *
FROM pais_costos
WHERE poblacion IS NULL;

SELECT *
FROM pais_envejecimiento
WHERE poblacion IS NULL;

--  identificar países que están en pais_costos pero no en pais_envejecimiento
SELECT c.pais
FROM pais_costos c
LEFT JOIN pais_envejecimiento e
  ON TRIM(LOWER(c.pais)) = TRIM(LOWER(e.nombre_pais))
WHERE e.nombre_pais IS NULL;

-- contar cuando nulos hay en cada columna de pais_envejecimiento
SELECT
    COUNT(*) AS total_filas,
    COUNT(*) FILTER (WHERE nombre_pais IS NULL) AS nulos_nombre_pais,
    COUNT(*) FILTER (WHERE capital IS NULL) AS nulos_capital,
    COUNT(*) FILTER (WHERE continente IS NULL) AS nulos_continente,
    COUNT(*) FILTER (WHERE region IS NULL) AS nulos_region,
    COUNT(*) FILTER (WHERE poblacion IS NULL) AS nulos_poblacion,
    COUNT(*) FILTER (WHERE tasa_de_envejecimiento IS NULL) AS nulos_tasa
FROM pais_envejecimiento;

-- verificar que el join funcionó
SELECT 
    c.pais,
    e.nombre_pais,
    e.tasa_de_envejecimiento
FROM pais_costos c
JOIN pais_envejecimiento e
  ON TRIM(LOWER(c.pais)) = TRIM(LOWER(e.nombre_pais))
LIMIT 10;