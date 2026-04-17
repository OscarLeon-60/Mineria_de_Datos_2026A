-- ==============================
-- SCHEMA: Análisis Climático Colombia
-- Timezone: America/Bogota (UTC-5)
-- ==============================

-- CIUDADES
CREATE TABLE IF NOT EXISTS ciudades (
    id            SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    departamento  VARCHAR(100) NOT NULL,
    pais          VARCHAR(100) NOT NULL DEFAULT 'Colombia',
    latitud       FLOAT,
    longitud      FLOAT,
    UNIQUE (nombre, departamento)   -- evita duplicados en upsert
);

-- MEDICIONES
CREATE TABLE IF NOT EXISTS mediciones (
    id                 SERIAL PRIMARY KEY,
    ciudad_id          INTEGER NOT NULL REFERENCES ciudades(id) ON DELETE CASCADE,
    fecha_consulta     TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    temperatura        FLOAT,
    temp_min           FLOAT,
    temp_max           FLOAT,
    sensacion_termica  FLOAT,
    humedad            INTEGER,
    presion            FLOAT,
    velocidad_viento   FLOAT,
    direccion_viento   FLOAT,
    descripcion        VARCHAR(200),
    nubosidad          INTEGER
);

-- ALERTAS CLIMÁTICAS
CREATE TABLE IF NOT EXISTS alertas_climaticas (
    id           SERIAL PRIMARY KEY,
    ciudad_id    INTEGER NOT NULL REFERENCES ciudades(id) ON DELETE CASCADE,
    fecha        TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    tipo_alerta  VARCHAR(100) NOT NULL,
    descripcion  TEXT
);

-- ==============================
-- ÍNDICES (mejoran velocidad de consultas)
-- ==============================

CREATE INDEX IF NOT EXISTS idx_mediciones_ciudad    ON mediciones (ciudad_id);
CREATE INDEX IF NOT EXISTS idx_mediciones_fecha     ON mediciones (fecha_consulta);
CREATE INDEX IF NOT EXISTS idx_alertas_ciudad       ON alertas_climaticas (ciudad_id);
CREATE INDEX IF NOT EXISTS idx_alertas_fecha        ON alertas_climaticas (fecha);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo         ON alertas_climaticas (tipo_alerta);