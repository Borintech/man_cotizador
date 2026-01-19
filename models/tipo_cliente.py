# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CotizadorTipoCliente(models.Model):
    _name = 'cotizador.tipo.cliente'
    _description = 'Tipo de Cliente para Cotizador'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre del tipo de cliente (ej: Mayorista, Minorista, Distribuidor)'
    )
    codigo = fields.Char(
        string='Código',
        required=True,
        help='Código único para identificar el tipo de cliente'
    )
    coeficiente = fields.Float(
        string='Coeficiente',
        required=True,
        default=1.0,
        digits=(16, 4),
        help='Coeficiente a aplicar para este tipo de cliente. Ej: 0.95 para 5% descuento, 1.10 para 10% recargo'
    )
    descripcion = fields.Text(
        string='Descripción',
        help='Descripción detallada del tipo de cliente y sus condiciones'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10
    )
    partner_count = fields.Integer(
        string='Cantidad de Clientes',
        compute='_compute_partner_count'
    )

    _sql_constraints = [
        ('codigo_uniq', 'unique(codigo)', 'El código del tipo de cliente debe ser único.'),
    ]

    @api.constrains('coeficiente')
    def _check_coeficiente(self):
        for record in self:
            if record.coeficiente <= 0:
                raise ValidationError(_('El coeficiente debe ser mayor a 0.'))

    def _compute_partner_count(self):
        for record in self:
            record.partner_count = self.env['res.partner'].search_count([
                ('cotizador_tipo_cliente_id', '=', record.id)
            ])

    def action_view_partners(self):
        """Acción para ver los partners asociados a este tipo de cliente"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Clientes - %s') % self.name,
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('cotizador_tipo_cliente_id', '=', self.id)],
            'context': {'default_cotizador_tipo_cliente_id': self.id},
        }
