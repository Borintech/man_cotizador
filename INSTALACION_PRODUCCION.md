# Instalación del módulo man_cotizador en Producción

## Problema identificado

Durante la instalación del módulo en bases de datos con datos existentes, se produce un error repetitivo:
```
no hay precio en lista -except línea 351 sale_order_cotizador.py
```

## Solución implementada

Se han realizado las siguientes mejoras al código:

### 1. Mejora en el manejo de errores
- Se agregó una función helper `get_safe_price_from_dict()` para obtener precios de manera segura
- Se mejoró el manejo de excepciones para evitar errores repetitivos
- Se agregaron validaciones para evitar ejecución problemática durante la instalación

### 2. Validaciones de contexto
- Se agregaron verificaciones para evitar ejecución durante la instalación del módulo
- Se mejoró el método `@api.onchange` para no ejecutarse en contextos problemáticos

### 3. Script de migración
- Se creó un script post-migración que:
  - Desactiva temporalmente el campo 'cotizar' en órdenes existentes
  - Normaliza precios problemáticos en líneas de órdenes de venta

## Pasos para la instalación en producción

### Opción 1: Instalación directa (recomendada)
```bash
# 1. Hacer backup de la base de datos
pg_dump -U odoo_user -h localhost nombre_base > backup_antes_cotizador.sql

# 2. Instalar el módulo
odoo-bin -d nombre_base -i man_cotizador --stop-after-init

# 3. Verificar que no hay errores en el log
```

### Opción 2: Instalación manual con preparación previa
Si la opción 1 aún presenta problemas, ejecutar estas consultas SQL antes de la instalación:

```sql
-- Desactivar cotización en órdenes existentes
UPDATE sale_order SET cotizar = false WHERE cotizar IS NULL OR cotizar = true;

-- Normalizar precios en líneas de órdenes
UPDATE sale_order_line SET price_unit = COALESCE(price_unit, 0.0) 
WHERE price_unit IS NULL OR price_unit < 0;

-- Verificar que no hay líneas problemáticas
SELECT COUNT(*) FROM sale_order_line WHERE price_unit IS NULL OR price_unit < 0;
```

Luego proceder con la instalación normal del módulo.

## Verificación post-instalación

1. Verificar que el módulo se instaló correctamente:
```sql
SELECT name, state FROM ir_module_module WHERE name = 'man_cotizador';
```

2. Comprobar que las órdenes de venta funcionan correctamente:
   - Abrir una orden de venta existente
   - Activar el campo 'cotizar' manualmente
   - Verificar que no se producen errores

## Contacto

Si persisten problemas durante la instalación, contactar al equipo de desarrollo con:
- Log completo del error
- Versión de Odoo
- Información sobre la base de datos (cantidad de órdenes de venta, etc.)
