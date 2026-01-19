# -*- coding: utf-8 -*-
from ..controllers.calculo_coef import cotiza
from ..controllers.api_dolar_euro import valor_dolar_euro
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


def get_safe_price_from_dict(actualizados2, line_id, line_price_unit):
    """
    Función helper para obtener precio de manera segura del diccionario actualizados2
    """
    if line_id in actualizados2:
        return actualizados2[line_id]
    else:
        # Si no existe, usar el precio de la línea como fallback
        safe_price = line_price_unit if line_price_unit > 0 else 0.0
        actualizados2[line_id] = safe_price
        return safe_price


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

def _make_utilidad_tabla2():
    # rr = request.env['cotizador.bobinas'].search([])

    q = "select * from cotizador_utilidad"
    request.cr.execute(q)
    rr = request.cr.fetchall()

    m = f'<table style="width:50%">'
    m += f'<tr> <th> Tipo de cliente </th> <th style="text-align:right"> Porcentaje de utilidad  </th></tr>'
    for r in rr:
        m += f'<tr><td> {r[1]} </td> <td style="text-align:right" > {r[2]} </td></tr>'

    m += "</table>"

    return m

class SaleOrder(models.Model):
    _inherit = "sale.order"

    activar_coef = fields.Boolean("Act.Coef")

    peso_adicional = fields.Float(readonly=False, help="Agregar peso para ajustar \nvalores del campo \nPeso Total en Kg")

    gasto_envio_local = fields.Float("Gasto Envios")
    gasto_envio_despacho = fields.Float("Gasto Despacho")

    dias_almacenamiento = fields.Float(
        string="Días almacenamiento",
        compute="_compute_dias_almacenamiento",
        store=True,
        help="Se sincroniza con el valor manual configurado en Dias de Almacenamiento"
    )

    cotizar = fields.Boolean("Cotizar", default=False)
    
    # Estado de cotización para mostrar visualmente
    cotizacion_estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('cotizado', 'Cotizado'),
    ], string='Estado Cotización', default='pendiente', compute='_compute_cotizacion_estado', store=True)
    
    dias_almacenamiento2 = fields.Integer()

    enume = [('maritimo', "Marítimo"), ('aereo', "Aéreo"), ('currier', "Currier")]
    medio_envio = fields.Selection(string="Envío", selection=enume, store=True, default='currier')

    # Campos para tipo de cliente y tipo de flete
    cotizador_tipo_cliente_id = fields.Many2one(
        'cotizador.tipo.cliente',
        string='Tipo de Cliente',
        help='Tipo de cliente para aplicar coeficiente automático'
    )
    cotizador_coef_cliente = fields.Float(
        string='Coef. Cliente',
        related='cotizador_tipo_cliente_id.coeficiente',
        store=True,
        readonly=True
    )
    cotizador_tipo_flete_id = fields.Many2one(
        'cotizador.tipo.flete',
        string='Tipo de Flete',
        help='Tipo de flete para aplicar coeficiente automático'
    )
    cotizador_coef_flete = fields.Float(
        string='Coef. Flete',
        related='cotizador_tipo_flete_id.coeficiente',
        store=True,
        readonly=True
    )
    
    # Modo de coeficiente: Cliente, Calculado o Manual
    modo_coeficiente = fields.Selection([
        ('automatico', 'Automático (Cliente si existe, sino Calculado)'),
        ('cliente', 'Usar Coef. Cliente'),
        ('calculado', 'Usar Coef. Calculado'),
        ('manual', 'Coef. Manual'),
    ], string='Modo Coeficiente', default='automatico',
       help='Automático: Usa coef. cliente si existe, sino el calculado\n'
            'Cliente: Fuerza usar el coef. del tipo de cliente\n'
            'Calculado: Fuerza usar el coef. calculado del sistema\n'
            'Manual: Permite ingresar un coeficiente manualmente')
    
    # Campo para coeficiente final manual
    coef_final_manual = fields.Float(
        string='Coef. Final Manual',
        digits=(16, 4),
        default=1.0,
        help='Coeficiente final que se aplicará a los precios cuando está activado el modo manual'
    )
    
    @api.depends('cotizar')
    def _compute_cotizacion_estado(self):
        for order in self:
            order.cotizacion_estado = 'cotizado' if order.cotizar else 'pendiente'

    @api.depends('dias_almacenamiento2')
    def _compute_dias_almacenamiento(self):
        """Evita recomputaciones costosas al instalar el módulo"""
        for order in self:
            order.dias_almacenamiento = float(order.dias_almacenamiento2 or 0.0)

    @api.onchange('partner_id')
    def _onchange_partner_id_cotizador(self):
        """Carga automáticamente el tipo de cliente y flete preferido del partner"""
        if self.partner_id:
            if self.partner_id.cotizador_tipo_cliente_id:
                self.cotizador_tipo_cliente_id = self.partner_id.cotizador_tipo_cliente_id
            if self.partner_id.cotizador_tipo_flete_preferido_id:
                self.cotizador_tipo_flete_id = self.partner_id.cotizador_tipo_flete_preferido_id

    @api.onchange('medio_envio')
    def _onchange_medio_envio_tipo_flete(self):
        """Carga automáticamente el tipo de flete según el medio de envío seleccionado"""
        if self.medio_envio:
            tipo_flete = self.env['cotizador.tipo.flete'].search([
                ('codigo', '=', self.medio_envio),
                ('active', '=', True)
            ], limit=1)
            if tipo_flete:
                self.cotizador_tipo_flete_id = tipo_flete

    @api.onchange('cotizar')
    def _onchange_cotizar(self):
        """Ejecuta el cálculo cuando se activa o desactiva cotizar"""
        if self.env.context.get('install_mode'):
            return
        self.aplica_coef_ejemplo()

    def action_calcular_cotizacion(self):
        """Botón para calcular/recalcular la cotización"""
        for order in self:
            order.cotizar = True
            order.aplica_coef_ejemplo()
        return True
    
    def action_limpiar_cotizacion(self):
        """Botón para limpiar/resetear la cotización"""
        for order in self:
            order.cotizar = False
        return True

    @api.onchange('modo_coeficiente', 'coef_final_manual')
    def _onchange_modo_coeficiente(self):
        """Recalcula precios cuando se cambia el modo o el coeficiente manual"""
        if self.env.context.get('install_mode'):
            return
        if self.cotizar:
            self.aplica_coef_ejemplo()

    @api.onchange('medio_envio', 'activar_coef', 'porcentaje_gasto_envio_despacho')
    def get_porcentaje_gasto_envio_despacho(self):
        try:
            for s in self:
                if not s.activar_coef:
                    r = 0
                    if s.medio_envio == 'maritimo':
                        q = """select * from cotizador_configuracion order by id desc"""
                        request.cr.execute(q)
                        r = request.cr.dictfetchall()[0]['porcentaje_gasto_maritimo']
                    if s.medio_envio == 'aereo':
                        q = """select * from cotizador_configuracion order by id desc"""
                        request.cr.execute(q)
                        r = request.cr.dictfetchall()[0]['porcentaje_gasto_aereo']
                    if s.medio_envio == 'currier':
                        r = 0
                    s.porcentaje_gasto_envio_despacho = float(r)
        except:
            self.porcentaje_gasto_envio_despacho = 0

    porcentaje_gasto_envio_despacho = fields.Float(compute="get_porcentaje_gasto_envio_despacho",
                                                   store=True,
                                                   readonly=False)
    gasto_envio_calculado = fields.Float(readonly=False)
    gasto_envio_agregado = fields.Float(readonly=False, help="sume o reste para ajustar \nvalores del campo \nTotal Gastos de Despacho")
    bobina_tabla = fields.Html(string='Tabla Bobina', readonly=True)
    caja_tabla = fields.Html(string="Tabla Caja", readonly=True)
    utilidad_tabla = fields.Html(string='Tabla Utilidad', readonly=True)
    bonina_datos = fields.Many2many('cotizador.bobinas')

    @api.onchange('gasto_envio_local')
    def _make_bobina_tabla22(self):
        # rr = request.env['cotizador.bobinas'].search([])
        if self.medio_envio:
            m = _make_bobina_tabla2()
            self.bobina_tabla = m

            m = _make_caja_tabla2()
            self.caja_tabla = m

            m = _make_utilidad_tabla2()
            self.utilidad_tabla= m

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
    valor_dolar = fields.Float("Valor Dólar BNA")
    valor_euro = fields.Float("Valor Euro BNA")
    coef_real_euro_dolar = fields.Float("Coef. Real Euro2Dólar")
    coef_cotizacion = fields.Float("Coef.Cotización")
    valor_dolar_blue = fields.Float("Valor Dólar Blue")
    coef_cotizacion_blue = fields.Float("Coef. Cotización Blue")
    
    # Nuevos campos para coeficiente manual y cálculo según fórmula
    coef_cotizacion_manual = fields.Boolean(
        string="Coeficiente Manual",
        default=False,
        help="Si está activo, permite modificar manualmente el coeficiente final y recalcula los precios de venta."
    )
    total_compra_euros = fields.Float(
        string="Total Compra (EUR)",
        compute="_compute_total_compra_euros",
        store=True,
        help="Suma total de los precios de compra del proveedor en euros."
    )
    coef_cotizacion_calculado = fields.Float(
        string="Coef. Calculado",
        compute="_compute_coef_cotizacion_calculado",
        store=True,
        digits=(16, 4),
        help="Coeficiente resultante = Precio Total Venta / (Precio Total Compra × Coef EUR/USD Real)"
    )

    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_total_compra_euros(self):
        """Calcula el total de compra en euros basado en precios de proveedor"""
        for order in self:
            total_compra = 0.0
            for line in order.order_line:
                if line.product_id:
                    # Buscar precio del proveedor
                    precio_proveedor = 0.0
                    try:
                        supplier_info = line.product_id.variant_seller_ids
                        if supplier_info:
                            cantidad_line = line.product_uom_qty
                            mejor_precio = 0.0
                            mejor_dif = 9999.99
                            for supplier in supplier_info:
                                if cantidad_line >= supplier.min_qty:
                                    dif = abs(cantidad_line - supplier.min_qty)
                                    if dif <= mejor_dif:
                                        mejor_dif = dif
                                        mejor_precio = supplier.price
                            precio_proveedor = mejor_precio if mejor_precio > 0 else (supplier_info[0].price if supplier_info else 0.0)
                    except:
                        precio_proveedor = 0.0
                    total_compra += precio_proveedor * line.product_uom_qty
            order.total_compra_euros = total_compra

    @api.depends('amount_total', 'total_compra_euros', 'coef_real_euro_dolar')
    def _compute_coef_cotizacion_calculado(self):
        """Calcula el coeficiente como: Precio Venta Total / (Precio Compra Total × Coef EUR/USD Real)"""
        for order in self:
            if order.total_compra_euros > 0 and order.coef_real_euro_dolar > 0:
                denominador = order.total_compra_euros * order.coef_real_euro_dolar
                if denominador > 0:
                    order.coef_cotizacion_calculado = order.amount_total / denominador
                else:
                    order.coef_cotizacion_calculado = 0.0
            else:
                order.coef_cotizacion_calculado = 0.0

    @api.onchange('coef_cotizacion', 'coef_cotizacion_manual')
    def _onchange_coef_cotizacion_manual(self):
        """Cuando se modifica manualmente el coeficiente, recalcula los precios de las líneas"""
        if not self.coef_cotizacion_manual or not self.coef_cotizacion:
            return
        
        if self.env.context.get('install_mode') or not self._origin:
            return
            
        # Solo recalcular si estamos en modo manual y tenemos coeficiente
        if self.coef_cotizacion > 0 and self.coef_real_euro_dolar > 0:
            for line in self.order_line:
                if line.product_id:
                    # Obtener precio de proveedor
                    precio_proveedor = 0.0
                    try:
                        supplier_info = line.product_id.variant_seller_ids
                        if supplier_info:
                            cantidad_line = line.product_uom_qty
                            mejor_precio = 0.0
                            mejor_dif = 9999.99
                            for supplier in supplier_info:
                                if cantidad_line >= supplier.min_qty:
                                    dif = abs(cantidad_line - supplier.min_qty)
                                    if dif <= mejor_dif:
                                        mejor_dif = dif
                                        mejor_precio = supplier.price
                            precio_proveedor = mejor_precio if mejor_precio > 0 else (supplier_info[0].price if supplier_info else 0.0)
                    except:
                        precio_proveedor = 0.0
                    
                    if precio_proveedor > 0:
                        # Aplicar: precio_proveedor × coef_real_euro_dolar × coef_cotizacion
                        line.price_unit = precio_proveedor * self.coef_real_euro_dolar * self.coef_cotizacion

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

    @api.depends('gasto_envio_local', 'gasto_envio_despacho', 'dias_almacenamiento2')
    def _tomar_coeficiente(self,
                           medio_envio,
                           total_euro,
                           total_peso2,
                           gasto_envio_local,
                           gasto_envio_despacho,
                           dias_almacenamiento2,
                           coef_euro2dolar,
                           coef_subtotal2,
                           coef_dexport,
                           coef_utilidad,
                           porc_gastos_desp,
                           env_agr,
                           v_d_blue,
                           v_dolar_of,
                           g_env_calculado=0
                           ):
        coti = cotiza()
        r = coti.calcular_coeficiente(medio_envio,
                                      total_euro,
                                      total_peso2,
                                      gasto_envio_local,
                                      gasto_envio_despacho,
                                      dias_almacenamiento2,
                                      coef_euro2dolar,
                                      coef_subtotal2,
                                      coef_dexport,
                                      coef_utilidad,
                                      porc_gastos_desp,
                                      env_agr,
                                      v_d_blue,
                                      v_dolar_of,
                                      g_env_calculado)
        return r

    def _can_modify_order_prices(self, order):
        """Verificar si se pueden modificar los precios de una orden"""
        return hasattr(order, 'state') and order.state in ['draft', 'sent']

    def aplica_coef_ejemplo(self):
        # Evitar ejecuciones masivas durante instalación o actualizaciones
        if not self or self.env.context.get('install_mode'):
            return
        
        # Diccionario local para almacenar precios (reemplaza variable global)
        precios_lineas = {}
            
        # Validar que las órdenes estén en estado que permita modificaciones
        orders_bloqueadas = []
        for order in self:
            if not self._can_modify_order_prices(order) and order.cotizar:
                orders_bloqueadas.append(f"{order.name} (Estado: {order.state})")
                
        # Si hay órdenes bloqueadas, mostrar advertencia al usuario
        if orders_bloqueadas:
            mensaje = f"ADVERTENCIA: No se pueden modificar precios en las siguientes órdenes porque están confirmadas o bloqueadas:\n\n{chr(10).join(orders_bloqueadas)}\n\nSolo se procesarán las órdenes en estado 'Borrador' o 'Enviada'."
            print(f"Cotizador: {mensaje}")
            
        # muestra en sale_order valor dolar y euro según api
        fecha = datetime.strptime('2022-09-01 00:32:33', '%Y-%m-%d %H:%M:%S')
        for order in self:
            if order.date_order and order.date_order > fecha:
                print(order.date_order)
                valor_dolar, valor_euro = valor_dolar_euro()
                order.valor_dolar = valor_dolar
                order.valor_euro = valor_euro
            try:
                order.coef_real_euro_dolar = float(valor_euro) / float(valor_dolar)
            except:
                order.coef_real_euro_dolar = 0

            # Procesar solo si cotizar está activo
            if order.cotizar:
                total_peso = 0
                total_euros = 0

                for line in order.order_line:
                    precio_unitario = 0.0

                    try:
                        suppler = line.product_id.variant_seller_ids
                        suppler_ids = suppler.ids
                        precio_candidato = 0
                        cantidad_sale_order = line.product_uom_qty
                        dif_init = 9999.99
                        cantidad = 0.0
                        dif = 0.0

                        for precio in suppler_ids:
                            dondeestaelprecio = """SELECT min_qty, price FROM public.product_supplierinfo
                            where id = %s """ % precio
                            request.cr.execute(dondeestaelprecio)
                            cantidad = request.cr.dictfetchall()[0]['min_qty']
                            dif = abs(cantidad_sale_order - cantidad)

                            if dif <= dif_init and (cantidad_sale_order >= cantidad):
                                dif_init = dif
                                request.cr.execute(dondeestaelprecio)
                                precio_candidato = request.cr.dictfetchall()[0]['price']
                                print("precio candidato", precio_candidato)

                        if line.id not in precios_lineas:
                            precios_lineas[line.id] = precio_candidato

                        precio_unitario = precios_lineas[line.id]

                    except Exception as e:
                        print(e)
                        try:
                            producto_precio_standard = line.product_id.variant_seller_ids.price
                            if line.id not in precios_lineas:
                                precios_lineas[line.id] = producto_precio_standard

                            precio_unitario = precios_lineas[line.id]
                        except:
                            print("No se halló standard_price. línea 259 sale_order_cotizador.py")
                            precio_unitario = 0.0

                    total_euros += precio_unitario * line.product_uom_qty

                    try:
                        peso_unitario = self._peso(line.product_id)
                        total_peso += peso_unitario * line.product_uom_qty
                    except:
                        pass

                if order.activar_coef:
                    if order.coef_dexport > 0:
                        try:
                            order.coef_dexport /= 100
                        except:
                            pass
                    if order.coef_utilidad > 0:
                        try:
                            order.coef_utilidad /= 100
                        except:
                            pass
                    coef, s2, s3, s4, c2, c3, c4, c0, coef_real, subtotal5, s1, peso_despues, g_e_calc, valor_dolar_blue, coef_coti_blue = \
                        order._tomar_coeficiente(
                            order.medio_envio,
                            total_euros,
                            total_peso + order.peso_adicional,
                            order.gasto_envio_local,
                            order.gasto_envio_despacho,
                            order.dias_almacenamiento2,
                            order.coef_euro2dolar,
                            order.coef_subtotal2,
                            order.coef_dexport,
                            order.coef_utilidad,
                            order.porcentaje_gasto_envio_despacho,
                            order.gasto_envio_agregado,
                            order.valor_dolar_blue,
                            order.valor_dolar,
                            order.gasto_envio_calculado
                        )
                else:
                    coef, s2, s3, s4, c2, c3, c4, c0, coef_real, subtotal5, s1, peso_despues, g_e_calc, valor_dolar_blue, coef_coti_blue = order._tomar_coeficiente(
                        order.medio_envio,
                        total_euros,
                        total_peso + order.peso_adicional,
                        order.gasto_envio_local,
                        order.gasto_envio_despacho,
                        order.dias_almacenamiento2,
                        0,
                        0,
                        0,
                        0,
                        order.porcentaje_gasto_envio_despacho,
                        order.gasto_envio_agregado,
                        order.valor_dolar_blue,
                        order.valor_dolar
                    )

                if order.medio_envio == 'currier':
                    order.dias_almacenamiento2 = -1
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
                order.valor_dolar_blue = valor_dolar_blue
                order.coef_cotizacion_blue = coef_coti_blue

                # Coeficiente calculado del sistema (para referencia)
                coef_calculado_sistema = coef_real * c0 * coef_coti_blue
                
                # Determinar coeficiente final según el modo seleccionado
                coef_cliente = order.cotizador_coef_cliente if order.cotizador_coef_cliente > 0 else 0
                
                if order.modo_coeficiente == 'manual' and order.coef_final_manual > 0:
                    # Modo manual: usar el valor ingresado
                    coef_final = order.coef_final_manual
                elif order.modo_coeficiente == 'cliente' and coef_cliente > 0:
                    # Modo cliente forzado: usar coef del cliente
                    coef_final = coef_cliente
                elif order.modo_coeficiente == 'calculado':
                    # Modo calculado forzado: usar coef calculado del sistema
                    coef_final = coef_calculado_sistema
                else:
                    # Modo automático: si el cliente tiene coeficiente, usarlo; sino usar calculado
                    if coef_cliente > 0:
                        coef_final = coef_cliente
                    else:
                        coef_final = coef_calculado_sistema

                for line in order.order_line:
                    if not self._can_modify_order_prices(order):
                        continue

                    if line.id not in precios_lineas:
                        precios_lineas[line.id] = line.price_unit
                        precio = precios_lineas[line.id]
                    else:
                        precio = get_safe_price_from_dict(precios_lineas, line.id, line.price_unit)
                    
                    line.price_unit = precio * coef_final
            else:
                # Si cotizar está desactivado, restaurar precios originales
                if not self._can_modify_order_prices(order):
                    continue

                for line in order.order_line:
                    try:
                        precio = get_safe_price_from_dict(precios_lineas, line.id, line.price_unit)
                        line.price_unit = precio
                    except Exception as e:
                        precio_fallback = line.price_unit if line.price_unit > 0 else 0.0
                        line.price_unit = precio_fallback
                        print(f"Error al obtener precio para línea {line.id}: {e}, usando precio fallback: {precio_fallback}")

    @api.onchange('coef_utilidad')
    def cotizar_ejemplo(self):
        # Evitar ejecución durante la instalación del módulo
        if self.env.context.get('install_mode') or not self._origin:
            return
            
        if self.cotizar:
            self.aplica_coef_ejemplo()
           # raise ValidationError("Invocando a la función de cotización")
