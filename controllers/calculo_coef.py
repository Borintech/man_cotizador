from odoo.http import request

class cotiza():

    def _valor_dolar(self):
        # todo hacer función
        return 200

    def _valor_euro(self):
        # todo hacer función
        return 300

    def _valor_coef_ajuste(self):
        # todo hacer función
        return 1.20

    def _valor_coef_dexport(self):
        # todo hacer función
        return 25

    def _valor_coef_utilidad(self):
        # todo hacer función
        q = f'select utilidad from configuracion limit 1'
        request.cr.execute(q)
        r = request.fetchall()[0][0]
        return r

    def _valor_total_almacenaje_dolar(self, dias, peso):
        # todo hacer función
        q = f'select importe from cotizador.gastos_almacenamiento where kg_desde >= {peso} and kg_hasta <= {peso}'
        request.cr.execute(q)
        r = request.fetchall()[0][0]
        return r


    def __init__(self):
        self.dolar = self._valor_dolar()
        self.euro = self._valor_euro()

    def calcular_coeficiente(self, total_euros, total_peso,
                             gasto_envio_local=0, gasto_envio_despacho=0,
                             dias_almacenamiento=15):

        """
        Esta función se encarga calcular el coerficiente de conversión.

        IN: Toma como valores de entrada todos los datos necesarios que provienen del sale.order,
        luego averigua valores externos de tablas.
        OUT: Por último, hace todos los cálculos necesarios y devuelve el valor
        """

        # 1. de euro a dolar ---------------------
        coef_euro2dolar = self.euro / self.dolar

        # 2. subtotal1 --------------------------
        total_dolar = total_euros * coef_euro2dolar
        subtotal1 = total_dolar

        # 3. total peso ajustado -----------------
        coef_subtotal2 = self._valor_coef_ajuste()
        subtotal2_flete = total_peso * coef_subtotal2

        # 4. coef_dexport
        coef_dexport = self._valor_coef_dexport()
        subtotal3_dexport = (coef_dexport * subtotal2_flete)

        # 5. coef_utilidad
        coef_utilidad = self._valor_coef_utilidad()
        subtotal4_utilidad = (subtotal3_dexport * coef_utilidad)

        # 6. total_almacenaje_dolares =  ver tabla de peso y dias
        total_almacenaje_dolares = self._valor_total_almacenaje_dolar(dias_almacenamiento)

        # 7. subtotal5
        subtotal5 = gasto_envio_local + gasto_envio_despacho + total_almacenaje_dolares + subtotal4_utilidad

        # 8. cálculo del coeficiente de conversión
        coef_cotizador = subtotal5 / subtotal1

        return coef_cotizador