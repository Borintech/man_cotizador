# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cotizador_tipo_cliente_id = fields.Many2one(
        'cotizador.tipo.cliente',
        string='Tipo de Cliente (Cotizador)',
        help='Tipo de cliente para el cálculo de coeficientes en el cotizador'
    )
    cotizador_coeficiente = fields.Float(
        string='Coeficiente Cliente',
        related='cotizador_tipo_cliente_id.coeficiente',
        store=True,
        readonly=True,
        help='Coeficiente asociado al tipo de cliente'
    )
    cotizador_tipo_flete_preferido_id = fields.Many2one(
        'cotizador.tipo.flete',
        string='Tipo de Flete Preferido',
        help='Tipo de flete preferido para este cliente'
    )
