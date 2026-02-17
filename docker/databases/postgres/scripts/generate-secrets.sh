# Generar contraseñas seguras
openssl rand -base64 32 > secrets/POSTGRES_ADMIN_PASSWORD.txt
openssl rand -base64 32 > secrets/POSTGRES_MIGRATOR_PASSWORD.txt
openssl rand -base64 32 > secrets/POSTGRES_RW_PASSWORD.txt
openssl rand -base64 32 > secrets/POSTGRES_RO_PASSWORD.txt

# Establecer permisos seguros
chmod 600 secrets/*.txt
chmod 700 secrets/