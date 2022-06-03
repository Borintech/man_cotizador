from odoo.http import request
import os
import datetime

def _log(dato):
    nombre = os.path.dirname(__file__) + '/coe_log.log'
    log = open(nombre, 'a')
    dato = "- Log: " + str(datetime.datetime.now()) + " ---> " + dato
    log.write(dato + '\n')
    log.close()

class cotiza:
    print("CARGANDO LA CLASE COTIZA")
    q = """SELECT * FROM cotizador_configuracion
    ORDER BY id ASC """
    request.cr.execute(q)
    valores = request.cr.dictfetchall()
    print('xx8 valores', valores)
    v_dolar = valores[0]['precio_dolar']
    v_euro = valores[0]['precio_euro']
    v_coef_peso_ajuste = valores[0]['coef_peso_ajuste']
    v_coef_flete = valores[0]['coef_flete']
    v_coef_dexport = valores[0]['coef_dexport']
    v_coef_utilidad = valores[0]['coef_utilidad']

    def __init__(self):
        self.dolar = self._valor_dolar()
        self.euro = self._valor_euro()

    def _valor_dolar(self):
        #hago un try por si no vienen valores (falla de consulta)
        # y para que no rompa al multiplicar pongo que v_dolar = 1 ???
        return self.v_dolar

    def _valor_euro(self):
        return self.v_euro

    def _valor_coef_ajuste(self):
        return self.v_coef_peso_ajuste

    def _valor_coef_dexport(self):
        return self.v_coef_dexport

    def _valor_coef_utilidad(self):
        #q = f'select utilidad from configuracion limit 1'
        #request.cr.execute(q)
        #r = request.fetchall()[0][0]
        return self.v_coef_utilidad

    def _valor_total_almacenaje_dolar(self, dias, peso):
        # todo hacer función
        print("xx44", peso)
        #q = f'select importe from cotizador_costos_almacenamiento where kg_desde >= {peso} and kg_hasta <= {peso}'
        q = f'select importe from cotizador_costos_almacenamiento where {peso} between kg_desde and kg_hasta'

        try:
            request.cr.execute(q)
            r = request.cr.dictfetchall()[0]['importe']
        except:
            r = 0

        # si el día es -1 es porque el usuario seleccionó currier y not tiene que tener almacen
        if dias == -1:
            r = 0

        print('xx46 valor_total_almacenaje_dolar', r)
        almacenaje = r * dias
        return almacenaje

    def calcular_coeficiente(self, total_euros, total_peso,
                             gasto_envio_local=0, gasto_envio_despacho=0,
                             dias_almacenamiento=15,coef_euro2dolar=0,coef_subtotal2=0,coef_dexport=0,coef_utilidad=0):
        """
        Esta función se encarga calcular el coerficiente de conversión.

        IN: Toma como valores de entrada todos los datos necesarios que provienen del sale.order,
        luego averigua valores externos de tablas.
        OUT: Por último, hace todos los cálculos necesarios y devuelve el valor
        """
        print("DENTRO DE CALCULAR_COEFICIENTE")
        print("total_euros", total_euros)
        print("total_peso", total_peso)
        print("gasto_envio_local", gasto_envio_local)
        print("gasto_envio_despacho", gasto_envio_despacho)
        print("dias_almacenamiento2", dias_almacenamiento)


        _log("Calculando coef para los valores de:")

        _log("total_euros : " + str(total_euros))
        _log("total_peso : " + str(total_peso))
        _log("gasto_envio_local: " + str(gasto_envio_local))
        _log("gasto_envio_despacho " + str(gasto_envio_despacho))
        _log("dias_almacenamiento2 " +  str(dias_almacenamiento))

        try:
            # 1. de euro a dolar ---------------------
            if coef_euro2dolar ==0:
                coef_euro2dolar = self.euro / self.dolar

            _log(f' - coef euro a dolar : {coef_euro2dolar}')

            # 2. subtotal1 --------------------------
            total_dolar = total_euros * coef_euro2dolar
            subtotal1 = total_dolar
            print("x71", subtotal1)

            _log(f' - subtotal1 : {subtotal1}')

            # 3. total peso ajustado -----------------
            if coef_subtotal2 ==0:
                coef_subtotal2 = self._valor_coef_ajuste()

            subtotal2_flete = total_peso * coef_subtotal2

            _log(f' - subtotal2_flete : {subtotal2_flete}')

            # 4. coef_dexport
            if coef_dexport ==0:
                coef_dexport = self._valor_coef_dexport()

            subtotal3_dexport = (coef_dexport * subtotal2_flete)

            _log(f' - subtotal3_dexport : {subtotal3_dexport}')

            # 5. coef_utilidad

            if coef_utilidad == 0:
                coef_utilidad = self._valor_coef_utilidad()

            subtotal4_utilidad = (subtotal3_dexport * coef_utilidad)

            _log(f' - subtotal4_utilidad : {subtotal4_utilidad}')

            # 6. total_almacenaje_dolares =  ver tabla de peso y dias
            total_almacenaje_dolares = self._valor_total_almacenaje_dolar(dias_almacenamiento, total_peso)

            _log(f' - total_almacenaje_dolares : {total_almacenaje_dolares}')

            # 7. subtotal5
            subtotal5 = gasto_envio_local + gasto_envio_despacho + total_almacenaje_dolares + subtotal4_utilidad

            _log(f' - subtotal5 : {subtotal5}')

            # 8. cálculo del coeficiente de conversión
            coef_cotizador = subtotal5 / subtotal1

            _log(f' - coef_cotizador : {coef_cotizador}')

            # 9. ahora lo paso a pesos

            coef_cotizador = coef_cotizador * self.dolar

            _log("------------------------------------------------")

            return coef_cotizador,subtotal2_flete,subtotal3_dexport,subtotal4_utilidad,coef_subtotal2,coef_dexport,coef_utilidad,coef_euro2dolar

        except:
            return 0,0,0,0,0,0,0,0