-- Conceder permisos específicos por base de datos
-- Este patrón permite múltiples aplicaciones con aislamiento lógico

\connect default;

-- Revocar privilegios públicos por defecto (seguridad)
REVOKE ALL ON DATABASE default FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Asignar ownership al migrator para gestionar esquemas
ALTER SCHEMA public OWNER TO migrator;

-- Permisos para migrator
GRANT CREATE, USAGE ON SCHEMA public TO migrator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO migrator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO migrator;

-- Permisos para aplicaciones de lectura/escritura
GRANT CONNECT ON DATABASE default TO writer;
GRANT USAGE ON SCHEMA public TO writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO writer;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO writer;

-- Permisos para aplicaciones de solo lectura
GRANT CONNECT ON DATABASE default TO reader;
GRANT USAGE ON SCHEMA public TO reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO reader;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO reader;

-- Privilegios por defecto para futuros objetos
ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO writer;

ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
    GRANT SELECT ON TABLES TO reader;

-- Crear extensiones comunes
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";