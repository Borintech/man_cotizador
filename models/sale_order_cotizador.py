# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError

from ..controllers.calculo_coef import cotiza

bandera = 1
actualizados = []
total_euros = 0
total_peso = 0
actualizados2 = {}

class SaleOrder(models.Model):
    _inherit = "sale.order"

    gasto_envio_local = fields.Float("Gasto Envios")
    gasto_envio_despacho = fields.Float("Gasto Despacho")
    dias_almacenamiento = fields.Float(string="Días almacenamiento",  compute = "aplica_coef_ejemplo", store=True)

    #dias_almacenamiento = fields.Float("Días almacenamiento")
    cotizar = fields.Boolean("Cotizar")
    dias_almacenamiento2 = fields.Float(string="D.Almacen")


    def funcion_ale(self, precio_a_cambiar):
        #pide coheficiente de algún lado
        coheficiente = 1.6
        return precio_a_cambiar * coheficiente

    def _peso(self,product_id):
        q = f"select weight from product_product where id = {product_id.ids[0]}"
        request.cr.execute(q)
        peso = request.cr.fetchall()[0][0]
        return peso

    def _cal_coef(self,total_orden, total_peso):
        pass



    @api.depends('order_line')
    def aplica_coef(self):
        # calculo el total
        total_orden = 0
        peso_unitario = 0
        total_peso = 0

        for order in self:
            for line in order.order_line:
                total_orden += line.price_unit
                # se obtiene el peso del producto
                peso_unitario  += self._peso(line.product_id)
                # total del peso es la cantiadad por el peso unitario
                total_peso += peso_unitario + line.product_uom_qty

        # calculo el coeficiente
        coef  = self._cal_coef(total_orden,total_peso)


        # actualización del precio unitario detodas las lineas de los items de la órden
        for order in self:
            for line in order.order_line:
                line.price_unit = line.price_unit * coef


    def _tomar_coeficiente(self, total_euro, total_peso,,gasto_envio_local,gasto_envio_despacho,dias_almacenamiento2):
        coti = cotiza()
        r = coti.calcular_coeficiente(total_euro,total_peso,gasto_envio_local,gasto_envio_despacho,dias_almacenamiento2)
        return r


    @api.depends('order_line','cotizar','gasto_envio_local','gasto_envio_despacho','dias_almacenamiento2')
    def aplica_coef_ejemplo(self):

        global bandera
        bandera += 1

        if bandera > 2 and self.cotizar:
            print("Entrando aplica_coef_ejemplo")

            for order in self:
                total_peso = 0
                total_euros = 0

                for line in order.order_line:
                    total_euros += line.price_unit
                    try:
                        peso_unitario = self._peso(line.product_id)
                        total_peso += peso_unitario + line.product_uom_qty
                    except:
                        pass

            for order in self:
                ## acá se debería calcular el coeficiente
                coef = self._tomar_coeficiente(total_euros,total_peso,self.gasto_envio_local,self.gasto_envio_despacho,self.dias_almacenamiento2)
                coef = 100

                for line in order.order_line:

                    if not line.id in actualizados2:
                        actualizados2[line.id] = line.price_unit

                    precio = actualizados2[line.id]

                    line.price_unit = precio * coef
                    print("line.price_unit   --->  " , line.price_unit, "   precio original: ", precio)
                    #actualizados.append(line.id)

                    # se obtiene el peso del producto

    def cotizar_ejemplo(self):
        if self.cotizar:
            self.aplica_coef_ejemplo()
            raise ValidationError("Invocando a la función de cotización")


    @api.model
    def create(self, vals_list):

        # averigua el último id de sale.order
        q = " select id from  public.sale_order order by id desc  limit 1"
        request.cr.execute(q)
        r = request.cr.fetchall()[0][0]
        #ultimo_id = self.env['sale.order'].search([])[-1].id
        men = f'Último id de sale.order  =  {r}'
        print(men)
        # -----

        result = super(SaleOrder, self).create(vals_list)

        return result