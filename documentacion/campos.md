# campos

precio_dolar
precio_euro

subtotal1

total_peso

coef_peso_ajuste

total_peso_ajustado = (total_peso * coef_peso_ajsute)

coef_subtotal2 = 1.20

subtotal2_flete  =   (coef_subtotal2 * total_peso)

coef_dexport = 25

subtotal3_dexport =  (coef_dexport * subtotal2_flete)

coef_utilidad = 1.60

subtotal4_utilidad = (subtotal3_dexport * coef_utilidad)

total_almacenaje_dolares =  ver tabla de peso y dias

gastos_envio_local

gastos_envios_despacho

subtotal5 = gastos_envio_local + gastos_envios_despacho + total_almacenaje_dolares + subtotal4_utilidad

coef_cotizador = subtotal5 / subtotal1

