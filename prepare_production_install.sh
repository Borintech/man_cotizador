#!/bin/bash

# Script de preparación para instalación de man_cotizador en producción
# Este script debe ejecutarse ANTES de instalar el módulo

DB_NAME="$1"
DB_USER="${2:-odoo}"
DB_HOST="${3:-localhost}"

if [ -z "$DB_NAME" ]; then
    echo "Uso: $0 <nombre_base_datos> [usuario_db] [host_db]"
    echo "Ejemplo: $0 mi_empresa_prod odoo localhost"
    exit 1
fi

echo "Preparando base de datos '$DB_NAME' para instalación de man_cotizador..."

# Verificar conexión a la base de datos
if ! psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Error: No se puede conectar a la base de datos"
    exit 1
fi

echo "1. Creando backup de seguridad..."
BACKUP_FILE="backup_pre_cotizador_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
echo "Backup creado: $BACKUP_FILE"

echo "2. Verificando órdenes de venta problemáticas..."
PROBLEMATIC_ORDERS=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM sale_order 
    WHERE cotizar = true;
")

echo "Órdenes con cotizar=true: $PROBLEMATIC_ORDERS"

PROBLEMATIC_LINES=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM sale_order_line 
    WHERE price_unit IS NULL OR price_unit < 0;
")

echo "Líneas con precios problemáticos: $PROBLEMATIC_LINES"

echo "3. Aplicando correcciones..."

# Desactivar cotización en todas las órdenes
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "
    UPDATE sale_order 
    SET cotizar = false 
    WHERE cotizar IS NULL OR cotizar = true;
"

# Normalizar precios problemáticos
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "
    UPDATE sale_order_line 
    SET price_unit = COALESCE(price_unit, 0.0)
    WHERE price_unit IS NULL OR price_unit < 0;
"

echo "4. Verificando correcciones aplicadas..."

REMAINING_PROBLEMS=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM sale_order WHERE cotizar = true;
")

echo "Órdenes con cotizar=true restantes: $REMAINING_PROBLEMS"

REMAINING_PRICE_PROBLEMS=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM sale_order_line WHERE price_unit IS NULL OR price_unit < 0;
")

echo "Líneas con precios problemáticos restantes: $REMAINING_PRICE_PROBLEMS"

echo ""
echo "✅ Preparación completada!"
echo "La base de datos está lista para la instalación de man_cotizador"
echo ""
echo "Comandos de instalación:"
echo "  odoo-bin -d $DB_NAME -i man_cotizador --stop-after-init"
echo ""
echo "En caso de problemas, restaurar desde: $BACKUP_FILE"
