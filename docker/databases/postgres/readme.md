# 🗄️ PostgreSQL en Docker - Configuración para Producción Multi-Aplicación

## 📋 Descripción General

Esta configuración proporciona una instancia de **PostgreSQL 16.11 LTS** (Long Term Support) lista para producción, diseñada específicamente para entornos con múltiples aplicaciones concurrentes. Incluye configuración optimizada, seguridad robusta y herramientas de mantenimiento integradas.

### ✨ Características Principales

- ✅ **PostgreSQL 16.11** - Última versión LTS con soporte hasta 2028
- ✅ **Configuración optimizada** para cargas de trabajo multi-aplicación
- ✅ **Seguridad por capas** con autenticación SCRAM-SHA-256
- ✅ **Roles especializados** para diferentes tipos de aplicaciones
- ✅ **Persistencia de datos** mediante volúmenes Docker
- ✅ **Health checks** integrados para monitoreo
- ✅ **Logging configurado** para auditoría y troubleshooting
- ✅ **Extensibilidad** con extensiones comunes preconfiguradas

## 📁 Estructura del Proyecto

```
postgres/
├── docker-compose.yml          # Configuración principal del stack
├── .env                        # Variables de entorno (no versionar)
├── .env.example                # Plantilla de variables de entorno
├── README.md                   # Este archivo
├── secrets/                    # Contraseñas y secrets (NO VERSIONAR)
│   ├── POSTGRES_ADMIN_PASSWORD.txt
│   ├── POSTGRES_MIGRATOR_PASSWORD.txt
│   ├── POSTGRES_RW_PASSWORD.txt
│   └── POSTGRES_RO_PASSWORD.txt
├── conf/
│   └── postgres.conf      # Configuración personalizada de PostgreSQL
├── init-scripts/          # Scripts SQL de inicialización
│   ├── 01-init-roles.sql
│   └── 02-grant-permissions.sql
└── scripts/                 
    ├── backup.sh
    ├── generate-secrets.sh
    └── monitor-connections.sh
```

## 🚀 Inicio Rápido

### Prerrequisitos

- **Docker** 20.10+ y **Docker Compose** 2.0+
- 4GB RAM mínimo (8GB recomendado para producción)
- 20GB de espacio en disco
- Linux/macOS/WSL2 (Windows)

### Paso 1: Clonar y Configurar

```bash
# 1. Crear estructura de directorios
git clone <repo-url> postgres-production
cd postgres-production

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores preferidos
nano .env

# 3. Generar secrets seguros
chmod +x scripts/generate-secrets.sh
./scripts/generate-secrets.sh

# 4. Iniciar el stack
docker compose up -d

# 5. Verificar estado
docker compose ps
docker compose logs -f postgres
```

### Paso 2: Verificar la Instalación

```bash
# Conectar con psql
docker compose exec postgres psql -U postgres_admin -d application_db

# Desde el host (si tienes psql instalado)
psql -h localhost -p 5432 -U postgres_admin -d application_db

# Comandos útiles de verificación
\conninfo                    # Información de conexión
\du                         # Listar usuarios/roles
\l                          # Listar bases de datos
\dx                         # Listar extensiones
SELECT version();           # Versión de PostgreSQL
```

## ⚙️ Configuración Detallada

### Variables de Entorno (.env)

| Variable | Valor por Defecto | Descripción |
|----------|------------------|-------------|
| `POSTGRES_ADMIN_USER` | `postgres_admin` | Usuario administrador principal |
| `POSTGRES_DEFAULT_DB` | `application_db` | Base de datos predeterminada |
| `TZ` | `UTC` | Zona horaria para timestamps |

### Roles y Permisos Preconfigurados

La configuración crea automáticamente 4 roles especializados:

| Rol | Propósito | Privilegios |
|-----|-----------|-------------|
| **app_migrator** | Migraciones de esquema | CREATE, ALTER, DROP, ALL PRIVILEGES |
| **app_rw** | Aplicaciones lectura/escritura | SELECT, INSERT, UPDATE, DELETE |
| **app_ro** | Aplicaciones solo lectura | SELECT |
| **postgres_admin** | Administración | SUPERUSER (solo mantenimiento) |

### Configuración de Red

```yaml
# Red privada aislada
Subnet: 172.20.0.0/24
Servicio DNS: postgres (resuelve a 172.20.0.2)
Puerto expuesto: 5432 (solo necesario para acceso externo)
```

**⚠️ Nota de Seguridad:** En producción, considera:
1. No exponer el puerto 5432 públicamente
2. Usar red interna (`internal: true`)
3. Conectar aplicaciones vía Docker network

## 🔐 Gestión de Secretos

### Generar Secrets Automáticamente

```bash
# Script incluido
./scripts/generate-secrets.sh

# O manualmente
mkdir -p secrets
openssl rand -base64 32 > secrets/POSTGRES_ADMIN_PASSWORD.txt
openssl rand -base64 32 > secrets/POSTGRES_MIGRATOR_PASSWORD.txt
openssl rand -base64 32 > secrets/POSTGRES_RW_PASSWORD.txt
openssl rand -base64 32 > secrets/POSTGRES_RO_PASSWORD.txt

# Permisos seguros
chmod 600 secrets/*.txt
chmod 700 secrets/
```

### Rotación de Contraseñas

```bash
# 1. Generar nuevas contraseñas
openssl rand -base64 32 > secrets/POSTGRES_RW_PASSWORD_NEW.txt

# 2. Actualizar en PostgreSQL
docker compose exec postgres psql -U postgres_admin -c \
  "ALTER ROLE app_rw WITH PASSWORD '$(cat secrets/POSTGRES_RW_PASSWORD_NEW.txt)';"

# 3. Actualizar archivo (mantener historial)
mv secrets/POSTGRES_RW_PASSWORD_NEW.txt secrets/POSTGRES_RW_PASSWORD.txt

# 4. Reiniciar aplicaciones gradualmente
```

## 📊 Configuración de Rendimiento

### Ajustes por Tamaño de Servidor

| Recursos | `shared_buffers` | `work_mem` | `max_connections` |
|----------|------------------|------------|-------------------|
| **2GB RAM** | 512MB | 2MB | 100 |
| **4GB RAM** | 1GB | 4MB | 200 |
| **8GB RAM** | 2GB | 8MB | 400 |
| **16GB RAM** | 4GB | 16MB | 800 |

### Modificar Configuración

```bash
# 1. Editar configuración
nano postgres/conf/postgres.conf

# 2. Aplicar cambios (sin reinicio para algunos parámetros)
docker compose exec postgres psql -U postgres_admin -c \
  "SELECT pg_reload_conf();"

# 3. Ver configuración actual
docker compose exec postgres psql -U postgres_admin -c \
  "SELECT name, setting FROM pg_settings WHERE name LIKE '%buffer%';"
```

## 🗃️ Operaciones Diarias

### Backup y Restauración

**Backup Automático Diario:**
```bash
# Ejecutar manualmente
./scripts/backup.sh

# O configurar cron
crontab -e
# Agregar línea: 0 2 * * * /ruta/completa/postgres-production/scripts/backup.sh
```

**Restaurar desde Backup:**
```bash
# Listar backups disponibles
ls -la backup/

# Restaurar backup específico
./scripts/restore.sh backup/postgres-full-20240115.sql.gz
```

**Backup en Caliente (WAL Archiving):**
```yaml
# En docker-compose.yml, agregar:
environment:
  POSTGRES_WAL_ARCHIVE: /var/lib/postgresql/wal_archive
volumes:
  - wal_archive:/var/lib/postgresql/wal_archive
```

### Monitoreo

**Conexiones Activas:**
```bash
./scripts/monitor-connections.sh
# o
docker compose exec postgres psql -U postgres_admin -c \
  "SELECT datname, usename, state, COUNT(*) 
   FROM pg_stat_activity 
   GROUP BY 1, 2, 3;"
```

**Consultas Lentas:**
```bash
docker compose exec postgres psql -U postgres_admin -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;"
```

**Uso de Disco:**
```bash
docker compose exec postgres psql -U postgres_admin -c "
  SELECT datname, pg_size_pretty(pg_database_size(datname))
  FROM pg_database
  ORDER BY pg_database_size(datname) DESC;"
```

## 🔄 Mantenimiento

### Actualización de PostgreSQL

```bash
# 1. Backup completo
./scripts/backup.sh

# 2. Detener contenedor actual
docker compose down

# 3. Cambiar versión en docker-compose.yml
# image: postgres:16.11-alpine3.22 → image: postgres:17.0-alpine3.22

# 4. Iniciar nueva versión
docker compose up -d

# 5. Verificar migración automática (PostgreSQL la maneja)
docker compose logs postgres | grep -i "upgrade\|migrat"
```

### Limpieza de Logs

```bash
# Los logs se rotan automáticamente:
# - Por tamaño: 100MB máximo
# - Por tiempo: 1 día máximo
# - Se mantienen 3 archivos máximo

# Limpieza manual
docker compose exec postgres find /var/log/postgresql -name "*.log" -mtime +7 -delete
```

### Vacuum y Analyze

```bash
# Vacuum manual (si auto-vacuum no es suficiente)
docker compose exec postgres psql -U postgres_admin -c "VACUUM VERBOSE ANALYZE;"

# Estadísticas de vacuum
docker compose exec postgres psql -U postgres_admin -c "
  SELECT schemaname, relname,
         last_vacuum, last_autovacuum,
         last_analyze, last_autoanalyze
  FROM pg_stat_user_tables;"
```

## 🛠️ Troubleshooting

### Problemas Comunes

**1. Contenedor no inicia:**
```bash
# Ver logs detallados
docker compose logs --tail=100 postgres

# Verificar permisos de volumes
ls -la postgres_data/

# Verificar configuración
docker compose config
```

**2. "Password authentication failed":**
```bash
# Verificar secrets
cat secrets/POSTGRES_ADMIN_PASSWORD.txt

# Reiniciar con secrets
docker compose down
docker compose up -d
```

**3. Conexiones agotadas:**
```bash
# Ver conexiones actuales
docker compose exec postgres psql -U postgres_admin -c "
  SELECT COUNT(*) as active_connections,
         (SELECT setting FROM pg_settings WHERE name='max_connections') as max
  FROM pg_stat_activity;"

# Matar conexiones inactivas
docker compose exec postgres psql -U postgres_admin -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle'
  AND now() - state_change > interval '10 minutes';"
```

**4. Alto uso de CPU:**
```bash
# Identificar consultas problemáticas
docker compose exec postgres psql -U postgres_admin -c "
  SELECT pid, usename, query, NOW() - query_start as duration
  FROM pg_stat_activity
  WHERE state = 'active'
  ORDER BY duration DESC
  LIMIT 5;"
```

### Comandos de Diagnóstico

```bash
# Health check manual
docker compose exec postgres pg_isready -U postgres_admin

# Ver uso de memoria
docker stats postgres_prod

# Ver logs en tiempo real
docker compose logs -f --tail=50 postgres

# Shell dentro del contenedor
docker compose exec postgres sh
```

## 🔗 Integración con Aplicaciones

### Strings de Conexión

**Para aplicaciones con acceso lectura/escritura:**
```
postgresql://app_rw:PASSWORD@postgres:5432/application_db?sslmode=require&pool_max_connections=20
```

**Para aplicaciones de solo lectura:**
```
postgresql://app_ro:PASSWORD@postgres:5432/application_db?sslmode=require&pool_max_connections=50
```

**Para migraciones:**
```
postgresql://app_migrator:PASSWORD@postgres:5432/application_db?sslmode=require
```

### Ejemplos por Lenguaje

**Node.js (pg):**
```javascript
const { Pool } = require('pg');
const pool = new Pool({
  host: 'postgres',
  port: 5432,
  database: 'application_db',
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20,
  idleTimeoutMillis: 30000,
});
```

**Python (psycopg2):**
```python
import psycopg2
conn = psycopg2.connect(
    host="postgres",
    database="application_db",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    connect_timeout=10
)
```

**Spring Boot (application.yml):**
```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/application_db
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 10
      connection-timeout: 30000
```

## 📈 Escalabilidad

### Para Mayor Carga

1. **Aumentar recursos en `docker-compose.yml`:**
```yaml
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4.0'
```

2. **Configurar replicación:**
```yaml
# Agregar al docker-compose.yml
postgres-replica:
  image: postgres:16.11-alpine3.22
  environment:
    POSTGRES_PASSWORD_FILE: /run/secrets/postgres_admin_password
  command: >
    postgres
    -c primary_conninfo=host=postgres-primary user=replication_user
    -c hot_standby=on
  volumes:
    - postgres_replica_data:/var/lib/postgresql/data
  depends_on:
    - postgres
```

3. **Implementar connection pooling:**
```yaml
# Servicio separado para PgBouncer
pgbouncer:
  image: edoburu/pgbouncer
  environment:
    DATABASE_URL: postgres://postgres:5432/application_db
    POOL_MODE: transaction
    MAX_CLIENT_CONN: 1000
    DEFAULT_POOL_SIZE: 20
  ports:
    - "6432:6432"
  depends_on:
    - postgres
```

## 🚨 Seguridad

### Checklist de Producción

- [ ] Secrets generados con `openssl rand -base64 32`
- [ ] Permisos de secrets: `chmod 600`
- [ ] SSL habilitado en `postgres.conf`
- [ ] `log_connections` y `log_disconnections` activados
- [ ] Firewall configurado (solo IPs autorizadas)
- [ ] Backup automatizado y testeado
- [ ] Monitoreo de conexiones activo
- [ ] Política de rotación de contraseñas establecida

### Auditoría de Seguridad

```bash
# Revisar intentos fallidos de conexión
docker compose exec postgres grep -i "failed" /var/log/postgresql/*.log

# Verificar conexiones no autenticadas
docker compose exec postgres psql -U postgres_admin -c "
  SELECT datname, usename, client_addr, backend_start
  FROM pg_stat_activity
  WHERE usename IS NULL;"

# Revisar privilegios
docker compose exec postgres psql -U postgres_admin -c "\dp"
```

## 📚 Recursos Adicionales

### Documentación Oficial
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [Docker Official PostgreSQL Image](https://hub.docker.com/_/postgres)
- [PostgreSQL Tuning Guide](https://pgmustard.com/docs/tuning)

### Herramientas Recomendadas
- **pgAdmin 4**: Interface web de administración
- **pgBackRest**: Backup y restauración avanzada
- **pgAudit**: Auditoría detallada
- **Prometheus + Grafana**: Monitoreo y alertas

### Soporte y Comunidad
- [Stack Overflow - PostgreSQL](https://stackoverflow.com/questions/tagged/postgresql)
- [PostgreSQL Slack](https://postgres-slack.herokuapp.com/)
- [PostgreSQL Mailing Lists](https://www.postgresql.org/list/)

---

**⚠️ Importante:** Esta configuración está diseñada para entornos de producción. Realiza pruebas exhaustivas en staging antes de implementar en producción, y ajusta los parámetros según las necesidades específicas de tu carga de trabajo.

**Mantenedor:** Equipo de DevOps  
**Última Actualización:** Enero 2024  
**Versión:** PostgreSQL 16.11 LTS