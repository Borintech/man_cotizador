# -*- coding: utf-8 -*-

import base64

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from odoo.modules import get_module_resource
from odoo.tools import image_process

from ..controllers.calculo_coef import cotiza
from ..controllers.api_dolar_euro import valor_dolar_euro
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError

bandera = 1
actualizados = []
total_euros = 0
total_peso = 0
actualizados2 = {}
leer = True


def _make_bobina_tabla2():
    # rr = request.env['cotizador.bobinas'].search([])

    q = "select * from cotizador_bobinas"
    request.cr.execute(q)
    rr = request.cr.fetchall()

    m = f'<table style="width:50%">'
    m += f'<tr> <th> Medidas de Bobinas </th> <th style="text-align:right"> Peso Bruto </th> <th style="text-align:right"> Peso Volumétrico </th></tr>'
    for r in rr:
        m += f'<tr><td> {r[1]} </td> <td style="text-align:right"> {r[2]} </td> <td style="text-align:right"> {r[3]} </td></tr>'

    m += "</table>"

    return m


def _make_caja_tabla2():
    # rr = request.env['cotizador.bobinas'].search([])

    q = "select * from cotizador_cajas"
    request.cr.execute(q)
    rr = request.cr.fetchall()

    m = f'<table style="width:50%">'
    m += f'<tr> <th> Medidas Cajas </th> <th style="text-align:right"> Peso Volumétrico  </th> <th style="text-align:right"> Volumen Interior </th></tr>'
    for r in rr:
        m += f'<tr><td> {r[1]} </td> <td style="text-align:right" > {r[2]} </td> <td style="text-align:right"> {r[3]} </td></tr>'

    m += "</table>"

    return m


class SaleOrder(models.Model):
    _inherit = "sale.order"

    activar_coef = fields.Boolean("Act.Coef")

    gasto_envio_local = fields.Float("Gasto Envios")
    gasto_envio_despacho = fields.Float("Gasto Despacho")

    dias_almacenamiento = fields.Float(string="Días almacenamiento", compute="aplica_coef_ejemplo", store=True)

    cotizar = fields.Boolean("Cotizar", default=False)
    dias_almacenamiento2 = fields.Integer()

    enume = [('maritimo', "Marítimo"), ('aereo', "Aéreo"), ('currier', "Currier")]
    medio_envio = fields.Selection(string="Envío", selection=enume, store=True, default='currier')

    @api.onchange('medio_envio', 'activar_coef', 'porcentaje_gasto_envio_despacho')
    def get_porcentaje_gasto_envio_despacho(self):

        if not self.activar_coef:
            if self.medio_envio == 'maritimo':
                q = """select * from cotizador_configuracion order by id desc"""
                request.cr.execute(q)
                r = request.cr.dictfetchall()[0]['porcentaje_gasto_maritimo']
            if self.medio_envio == 'aereo':
                q = """select * from cotizador_configuracion order by id desc"""
                request.cr.execute(q)
                r = request.cr.dictfetchall()[0]['porcentaje_gasto_aereo']
            if self.medio_envio == 'currier':
                r = 0
            self.porcentaje_gasto_envio_despacho = float(r)

    porcentaje_gasto_envio_despacho = fields.Float(compute="get_porcentaje_gasto_envio_despacho",
                                                   store=True,
                                                   readonly=False)
    gasto_envio_calculado = fields.Float(readonly=True)
    gasto_envio_agregado = fields.Float(readonly=False, help="sume o reste para ajustar \nvalores del campo \nTotal Gastos de Despacho")

    bobina_tabla = fields.Html(string='Tabla Bobina', readonly=True)
    caja_tabla = fields.Html(string="Tabla Caja", readonly=True)

    bonina_datos = fields.Many2many('cotizador.bobinas')

    @api.onchange('gasto_envio_local')
    def _make_bobina_tabla22(self):
        # rr = request.env['cotizador.bobinas'].search([])
        if self.medio_envio:
            m = _make_bobina_tabla2()
            self.bobina_tabla = m

            m = _make_caja_tabla2()
            self.caja_tabla = m

    @api.model
    def _obtener_imagen_cajas(self):
        """ Get a default image when the user is created without image

            Inspired to _get_default_image method in
            https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/res/res_partner.py

        nombre_foto = 'tamanio_cajas.png'
        image_path = get_module_resource('man_cotizador', 'static/img', nombre_foto)
        image = base64.b64encode(open(image_path, 'rb').read())
        # return image_process(image, colorize=True)
        """
        # return image_process(image)
        return

    cajas_image = fields.Image(string="Tamaño de cajas", readonly=True)

    @api.model
    def _obtener_imagen_bobinas(self):
        """
        nombre_foto = 'tamanio_bobinas.png'
        image_path = get_module_resource('man_cotizador', 'static/img', nombre_foto)
        image = base64.b64encode(open(image_path, 'rb').read())
        return image_process(image)
        """
        return 1

    # -------------------
    peso_real = fields.Float("Peso Real Total en Kg")
    peso_por_variacion = fields.Float("Peso Total en Kg")
    subtotal1_precio = fields.Float("Sub Total 1")
    coef_euro2dolar = fields.Float("Coef.Euro2Dolar")
    # - ajuste peso
    coef_subtotal2 = fields.Float("Coef.Peso")
    subtotal2_flete = fields.Float("Coef.Flete")

    # - Derechos de importacion
    coef_dexport = fields.Float("Coef.Exp")
    subtotal3_dexport = fields.Float("Sub.Exp")

    # - utilidad
    coef_utilidad = fields.Float("Coef.Utilidad")
    subtotal4_utilidad = fields.Float("Subt.Utilidad")

    # activar_coef = fields.Boolean("Act.Coef")
    # -------------------

    valor_dolar = fields.Float("Valor Dólar BNA")
    valor_euro = fields.Float("Valor Euro BNA")
    coef_real_euro_dolar = fields.Float("Coef. Real Euro2Dólar")

    coef_cotizacion = fields.Float("Coef.Cotización")

    def funcion_ale(self, precio_a_cambiar):
        # pide coheficiente de algún lado
        coheficiente = 1.6
        return precio_a_cambiar * coheficiente

    def _peso(self, product_id):
        q = f"select weight from product_product where id = {product_id.ids[0]}"
        request.cr.execute(q)
        peso = request.cr.fetchall()[0][0]
        return peso

    def _cal_coef(self, total_orden, total_peso):
        pass

    @api.depends('order_line')
    def aplica_coef(self):
        # calculo el total
        total_orden = 0
        peso_unitario = 0
        global total_peso
        total_peso = 1  # lo pongo en uno
        banderita = 0
        for order in self:
            for line in order.order_line:
                banderita += 1
                total_orden += line.price_unit
                # se obtiene el peso del producto
                peso_unitario += self._peso(line.product_id)
                # total del peso es la cantiadad por el peso unitario
                total_peso += peso_unitario * line.product_uom_qty

        coef = 1
        if banderita > 0:
            coef = self._tomar_coeficiente()

        # actualización del precio unitario de todas las lineas de los items de la órden
        for order in self:
            for line in order.order_line:
                line.price_unit = line.price_unit * coef

    @api.depends('gasto_envio_local', 'gasto_envio_despacho', 'dias_almacenamiento2')
    def _tomar_coeficiente(self, medio_envio, total_euro, total_peso2, gasto_envio_local, gasto_envio_despacho,
                           dias_almacenamiento2,
                           coef_euro2dolar, coef_subtotal2, coef_dexport, coef_utilidad, porc_gastos_desp, env_agr):
        coti = cotiza()
        r = coti.calcular_coeficiente(medio_envio, total_euro, total_peso2, gasto_envio_local, gasto_envio_despacho,
                                      dias_almacenamiento2,
                                      coef_euro2dolar, coef_subtotal2, coef_dexport, coef_utilidad, porc_gastos_desp, env_agr)
        return r

    @api.depends('order_line', 'cotizar', 'gasto_envio_local', 'gasto_envio_despacho', 'dias_almacenamiento2',
                 'medio_envio', 'activar_coef')
    def aplica_coef_ejemplo(self):
        # muestra en sale_order valor dolar y euro según api
        valor_dolar, valor_euro = valor_dolar_euro()
        self.valor_dolar = valor_dolar
        self.valor_euro = valor_euro
        try:
            self.coef_real_euro_dolar = float(valor_euro) / float(valor_dolar)
        except:
            self.coef_real_euro_dolar = 0

        global bandera, total_peso, total_euros
        bandera += 1

        if bandera > 2 and self.cotizar:
            # todo Ale... recordar que en la instalación si sacamos bandera > 2 no entiendo
            #  por qué línea 223 if self.cotizar viene en true o pasa y rompe la instalación
            #  ya que order error

            for order in self:
                total_peso = 0
                total_euros = 0

                for line in order.order_line:
                    precio_unitario = "ahora intentamos consultar el standard_price"
                    #print (line.product_id.price)
                    try:
                        #producto_precio_standard = line.product_id.standard_price
                        producto_precio_standard = line.product_id.variant_seller_ids.price
                        print(producto_precio_standard)
                        if line.id not in actualizados2:
                            # actualizados2[line.id] = line.price_unit
                            actualizados2[line.id] = producto_precio_standard

                        precio_unitario = actualizados2[line.id]
                    except:
                        print("No se halló standard_price. línea 259 sale_order_cotizador.py")
                        pass

                    total_euros += precio_unitario * line.product_uom_qty

                    try:
                        peso_unitario = self._peso(line.product_id)
                        total_peso += peso_unitario * line.product_uom_qty
                    except:
                        pass

            if self.activar_coef:
                if self.coef_dexport > 0:
                    try:
                        self.coef_dexport /= 100
                    except:
                        # aca podemos poner una ventana de advertencia
                        pass
                if self.coef_utilidad > 0:
                    try:
                        self.coef_utilidad /= 100
                    except:
                        # aca podemos poner una ventana de advertencia
                        pass
                coef, s2, s3, s4, c2, c3, c4, c0, coef_real, subtotal5, s1, peso_despues, g_e_calc = \
                    self._tomar_coeficiente(
                        self.medio_envio,
                        total_euros,
                        total_peso,
                        self.gasto_envio_local,
                        self.gasto_envio_despacho,
                        self.dias_almacenamiento2,
                        self.coef_euro2dolar,
                        self.coef_subtotal2,
                        self.coef_dexport,
                        self.coef_utilidad,
                        self.porcentaje_gasto_envio_despacho,
                        self.gasto_envio_agregado)
            else:
                coef, s2, s3, s4, c2, c3, c4, c0, coef_real, subtotal5, s1, peso_despues, g_e_calc = self._tomar_coeficiente(
                    self.medio_envio,
                    total_euros,
                    total_peso,
                    self.gasto_envio_local,
                    self.gasto_envio_despacho,
                    self.dias_almacenamiento2,
                    0,
                    0,
                    0,
                    0,
                    self.porcentaje_gasto_envio_despacho,
                    self.gasto_envio_agregado)

            for order in self:

                if self.medio_envio == 'currier':
                    self.dias_almacenamiento2 = -1

                order.coef_euro2dolar = c0
                order.subtotal2_flete = s2
                order.subtotal3_dexport = s3
                order.subtotal4_utilidad = s4

                order.peso_real = total_peso
                order.peso_por_variacion = peso_despues
                order.subtotal1_precio = s1

                order.coef_subtotal2 = c2
                order.coef_dexport = c3 * 100
                order.coef_utilidad = c4 * 100
                order.coef_cotizacion = coef_real
                order.gasto_envio_calculado = g_e_calc


                for line in order.order_line:
                    if line.id not in actualizados2:
                        actualizados2[line.id] = line.price_unit
                        precio = actualizados2[line.id]
                    else:
                        precio = actualizados2[line.id]

                    line.price_unit = precio * coef_real * c0
                    #print("line.price_unit   --->  ", line.price_unit, "   precio original: ", precio)
                    # actualizados.append(line.id)

                # if order.amount_total > 0:
                #     order.amount_total = subtotal5
                # print(order.amount_total)
        else:
            for order in self:
                for line in order.order_line:
                    try:
                        precio = actualizados2[line.id]
                        line.price_unit = precio
                    except:
                        print("no hay precio en lista -except línea 351 sale_order_cotizador.py")
                        pass

    def cotizar_ejemplo(self):
        if self.cotizar:
            self.aplica_coef_ejemplo()
            raise ValidationError("Invocando a la función de cotización")

    # @api.model
    # def create(self, vals_list):
    #
    #     # averigua el último id de sale.order
    #     q = " select id from  public.sale_order order by id desc  limit 1"
    #     request.cr.execute(q)
    #     r = request.cr.fetchall()[0][0]
    #     # ultimo_id = self.env['sale.order'].search([])[-1].id
    #     men = f'Último id de sale.order  =  {r}'
    #     print(men)
    #     # -----
    #
    #     result = super(SaleOrder, self).create(vals_list)
    #
    #     return result
