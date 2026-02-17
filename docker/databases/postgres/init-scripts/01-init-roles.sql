-- Script de inicialización que se ejecuta SOLO en primera creación
-- Crea roles especializados para diferentes tipos de aplicaciones

-- 1. Rol para migraciones (máximos privilegios)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'migrator') THEN
        CREATE ROLE migrator WITH LOGIN PASSWORD '';
        ALTER ROLE migrator SET search_path = public;
    END IF;
END
$$;

-- 2. Rol para aplicaciones con permisos de lectura/escritura
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'writer') THEN
        CREATE ROLE writer WITH LOGIN PASSWORD '';
    END IF;
END
$$;

-- 3. Rol para aplicaciones de solo lectura (reporting, analytics)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'reader') THEN
        CREATE ROLE reader WITH LOGIN PASSWORD '';
    END IF;
END
$$;

-- 4. Grupo para organizar permisos
CREATE ROLE app_users;
GRANT writer, reader TO app_users;