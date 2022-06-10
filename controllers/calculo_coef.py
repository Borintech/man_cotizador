from odoo.http import request
import os
import datetime

#cambios para poder hacer commit
def _log(dato):
    nombre = os.path.dirname(__file__) + '/coe_log.log'
    log = open(nombre, 'a')
    dato = "- Log: " + str(datetime.datetime.now()) + " ---> " + dato
    log.write(dato + '\n')
    log.close()


class cotiza:

    def __init__(self):
        global v_dolar, v_euro, v_coef_peso_ajuste, v_coef_flete, \
            v_coef_dexport, v_coef_utilidad, v_coef_flete_maritimo, \
            v_coef_flete_aereo, v_coef_flete_currier

        try:
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

            v_coef_flete_maritimo = valores[0]['coef_flete_maritimo']
            v_coef_flete_aereo = valores[0]['coef_flete_aereo']
            v_coef_flete_currier = valores[0]['coef_flete_currier']
        except Exception as e:
            v_dolar = 1
            v_euro = 1
            v_coef_peso_ajuste = 1
            v_coef_flete = 1
            v_coef_dexport = 1
            v_coef_utilidad = 1
            v_coef_flete_maritimo = 0
            v_coef_flete_aereo = 0
            v_coef_flete_currier = 0

        self.dolar = v_dolar
        self.euro = v_euro

    # def _valor_dolar(self):
    #     #hago un try por si no vienen valores (falla de consulta)
    #     # y para que no rompa al multiplicar pongo que v_dolar = 1 ???
    #     return self.v_dolar
    #
    # def _valor_euro(self):
    #     return self.v_euro

    def _valor_coef_ajuste(self):
        return v_coef_peso_ajuste

    def _valor_coef_dexport(self):
        try:
            r = v_coef_dexport / 100
        except:
            r = 0
        return r

    def _valor_coef_utilidad(self):
        try:
            r = v_coef_utilidad / 100
        except:
            r = 0
        return r

    def _valor_total_almacenaje_dolar(self, dias, peso):
        # todo hacer función
        print("xx44", peso)
        # q = f'select importe from cotizador_costos_almacenamiento where kg_desde >= {peso} and kg_hasta <= {peso}'
        q = f'select importe from cotizador_costos_almacenamiento where {peso} between kg_desde and kg_hasta'

        try:
            request.cr.execute(q)
            r = request.cr.dictfetchall()[0]['importe']
        except:
            r = 0

        # si el día es -1 es porque el usuario seleccionó currier y not tiene que tener almacen
        if dias <= -1:
            r = 0

        print('xx46 valor_total_almacenaje_dolar', r)
        almacenaje = r * dias
        print(almacenaje)
        return almacenaje

    def calcular_coeficientex2(self, medio_envio, total_euros, total_peso,
                             gasto_envio_local=0, gasto_envio_despacho=0,
                             dias_almacenamiento=15, coef_euro2dolar=0, coef_subtotal2=0, coef_dexport=0,
                             coef_utilidad=0):
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
        _log("dias_almacenamiento2 " + str(dias_almacenamiento))

        try:
            # 1. de euro a dolar ---------------------
            if coef_euro2dolar == 0:
                coef_euro2dolar = self.euro / self.dolar

            _log(f' - coef euro a dolar : {coef_euro2dolar}')

            # 2. subtotal1 --------------------------
            total_dolar = total_euros  # * coef_euro2dolar
            subtotal1 = total_dolar

            _log(f' - subtotal1 : {subtotal1}')

            # 3. total peso ajustado -----------------
            if coef_subtotal2 == 0:
                coef_subtotal2 = self._valor_coef_ajuste()

            coe_medio_envio = 22

            if medio_envio == 'maritimo':
                coe_medio_envio = v_coef_flete_maritimo

            if medio_envio == 'aereo':
                coe_medio_envio = v_coef_flete_aereo

            if medio_envio == 'currier':
                coe_medio_envio = v_coef_flete_currier

            subtotal2_flete = total_peso * coef_subtotal2 * coe_medio_envio

            subtotal2_flete = subtotal2_flete + subtotal1

            _log(f' - subtotal2_flete : {subtotal2_flete}')

            # 4. coef_dexport
            if coef_dexport == 0:
                coef_dexport = self._valor_coef_dexport()

            subtotal3_dexport = (coef_dexport * subtotal2_flete) + subtotal2_flete

            _log(f' - subtotal3_dexport : {subtotal3_dexport}')

            # 5. coef_utilidad

            if coef_utilidad == 0:
                coef_utilidad = self._valor_coef_utilidad()

            subtotal4_utilidad = (subtotal3_dexport * coef_utilidad) + subtotal3_dexport

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
            coef_real = coef_cotizador
            coef_cotizador = coef_cotizador * self.dolar
            # coef_cotizador = coef_cotizador

            _log("------------------------------------------------")

            return coef_cotizador, subtotal2_flete, subtotal3_dexport, subtotal4_utilidad, coef_subtotal2, coef_dexport, coef_utilidad, coef_euro2dolar, coef_real

        except:
            # retornaba 8 valores, se esperan 9
            return 0, 0, 0, 0, 0, 0, 0, 0, 0

    def calcular_coeficiente(self, medio_envio, total_euros, total_peso,
                             gasto_envio_local=0, gasto_envio_despacho=0,
                             dias_almacenamiento=15, coef_euro2dolar=0, coef_subtotal2=0, coef_dexport=0,
                             coef_utilidad=0):
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
        _log("dias_almacenamiento2 " + str(dias_almacenamiento))

        try:
            # 1. de euro a dolar ---------------------
            if coef_euro2dolar == 0:
                coef_euro2dolar = self.euro / self.dolar

            _log(f' - coef euro a dolar : {coef_euro2dolar}')

            # 2. subtotal1 --------------------------
            total_dolar = total_euros  # * coef_euro2dolar
            subtotal1 = total_dolar

            _log(f' - subtotal1 : {subtotal1}')

            # 3. total peso ajustado -----------------
            if coef_subtotal2 == 0:
                coef_subtotal2 = self._valor_coef_ajuste()

            if medio_envio == 'maritimo':
                coe_medio_envio = v_coef_flete_maritimo

            elif medio_envio == 'aereo':
                coe_medio_envio = v_coef_flete_aereo

            else:
                coe_medio_envio = v_coef_flete_currier

            nuevo_peso = total_peso * coef_subtotal2
            print("x250:", total_peso, coef_subtotal2, coe_medio_envio)
            subtotal2_flete = total_peso * coef_subtotal2 * coe_medio_envio

            subtotal2_flete = subtotal2_flete + subtotal1

            _log(f' - subtotal2_flete : {subtotal2_flete}')

            # 4. coef_dexport
            if coef_dexport == 0:
                coef_dexport = self._valor_coef_dexport()

            subtotal3_dexport = (coef_dexport * subtotal2_flete) + subtotal2_flete

            _log(f' - subtotal3_dexport : {subtotal3_dexport}')

            # 5. coef_utilidad

            if coef_utilidad == 0:
                coef_utilidad = self._valor_coef_utilidad()

            subtotal4_utilidad = (subtotal3_dexport * coef_utilidad) + subtotal3_dexport

            _log(f' - subtotal4_utilidad : {subtotal4_utilidad}')

            # 6. total_almacenaje_dolares =  ver tabla de peso y dias
            total_almacenaje_dolares = self._valor_total_almacenaje_dolar(dias_almacenamiento, total_peso)

            _log(f' - total_almacenaje_dolares : {total_almacenaje_dolares}')

            # 7. subtotal5
            subtotal5 = gasto_envio_local + gasto_envio_despacho + total_almacenaje_dolares + subtotal4_utilidad

            _log(f' - subtotal5 : {subtotal5}')
            print("x289 subtotal5", subtotal5)

            # 8. cálculo del coeficiente de conversión
            coef_cotizador = subtotal5 / subtotal1
            print("x293 coef_cotizador", coef_cotizador)

            _log(f' - coef_cotizador : {coef_cotizador}')

            # 9. ahora lo paso a pesos
            coef_real = coef_cotizador
            print("x297 coef_real", coef_real)
            coef_cotizador = coef_cotizador * self.dolar
            # coef_cotizador = coef_cotizador

            _log("------------------------------------------------")

            return coef_cotizador, subtotal2_flete, subtotal3_dexport, subtotal4_utilidad, coef_subtotal2, coef_dexport, coef_utilidad, coef_euro2dolar, coef_real, subtotal5, subtotal1, nuevo_peso

        except:
            return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
