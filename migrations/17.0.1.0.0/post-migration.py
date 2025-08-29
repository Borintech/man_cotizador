# -*- coding: utf-8 -*-
"""
Script de post-migración para man_cotizador
Este script se ejecuta después de la instalación del módulo para asegurar
que no haya problemas con órdenes de venta existentes.
"""

def migrate(cr, version):
    """
    Migración post-instalación para man_cotizador
    """
    # Desactivar temporalmente el campo 'cotizar' en órdenes de venta existentes
    # para evitar la ejecución automática de métodos problemáticos durante la instalación
    cr.execute("""
        UPDATE sale_order 
        SET cotizar = false 
        WHERE cotizar IS NULL OR cotizar = true;
    """)
    
    # Actualizar órdenes de venta que no tengan precios válidos en sus líneas
    cr.execute("""
        UPDATE sale_order_line 
        SET price_unit = COALESCE(price_unit, 0.0)
        WHERE price_unit IS NULL OR price_unit < 0;
    """)
    
    print("Migración post-instalación completada: campos cotizar desactivados y precios normalizados")
