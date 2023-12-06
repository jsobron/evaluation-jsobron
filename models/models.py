# TODO 01:

def convert_hours(self, value): #Recibo los valores
    try:
        hours = int(float(value))    #Paso a float el valor
        minutes = int((float(value) - hours) * 60) #Tomo los minutos que tenemos y lo multiplico por 60
        return f"{hours:02d}:{minutes:02d}" #Retornamos hora y minutos convertidos
    except ValueError:
        return 'No es posible completar la conversión'


# TODO 02:
#  Refactorizar
@api.onchange('line_id')
def _get_packet_publishable_product_type(self):
    for record in self:
        data_product = record.env['product.product'].browse(record.product_id.id)  #Cambio search por browse para traerme todo el registro
        if data_product and data_product.publishable_ok: #Al tener todo el registro, simplifico los dos ifs en 1 solo con doble condicion
            record.publishable_product_type = data_product.publishable_product_type
        else:
            record.publishable_product_type = 'notp'

# TODO 03:
#  Refactorizar
#  Agregar una condición para cualquier otro valor de 'publishable_product_type' lanzar una excepción de Odoo
#  Sustentar el tipo de excepción que usó(¿Por que?)

# 3. Use de excepction el UserError es mas amigable a la vista del usuario.
from odoo.exceptions import UserError
def packet_product_action_publish(self):
    for rec in self:
        is_lan = False
        parameter_ids = self.env['guru.rule.country'].browse([('code', '=', 'LAN')])
        if self.env.company.country_id.id in parameter_ids.country_ids.ids:
            is_lan = True
        data_product = self.env['product.product'].browse([('id', '=', rec.guru_product_id.id)])
        #Verifico si hay data_producto o si es el publicable o no
        if not data_product or not data_product.publishable_ok:
            raise UserError("El producto no es publicable")
        

        product_type = data_product.product_tmpl_id.publishable_product_type
        if product_type == 'pacom': 
            wzd_id = self.env['guru.pacom.wzd'].create({'var_obj': 'Obj', 'is_lan': is_lan})
            return {
                'name': _('Pacom'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': [self.env.ref('guru_pacom.view_guru_pacom_simple_wzd_form').id],
                'res_model': 'guru.pacom.wzd',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': wzd_id.id,
                'context': {
                    'packet_product_line': rec.id,
                    'line_id': rec.order_line_id.id,
                    'order_id': rec.order_id.id,
                    'partner_id': rec.order_id.partner_id.id,
                },
            }
        elif product_type == 'landing_pacom':
            wzd_landing_id = self.env['guru.landing.pacom.wzd'].create({'var_obj': 'Obj'})
            return {
                'name': _('Landing Pacom'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': [self.env.ref('guru_pacom.guru_landing_pacom_wzd_form_view').id],
                'res_model': 'guru.landing.pacom.wzd',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': wzd_landing_id.id,
                'context': {
                    'packet_product_line': rec.id,
                    'line_id': rec.order_line_id.id,
                    'order_id': rec.order_id.id,
                    'partner_id': rec.order_id.partner_id.id,
                },
            }
        
        elif product_type =='web_shop':
            wzd_web_id = self.env['guru.web.product.wzd'].create({'var_obj': 'Obj', 'is_lan': is_lan})
            line_id = rec.order_line_id.product_id.guru_packet_ids.filtered(
                lambda e: e.publishable_product_type == 'web_shop')
            wzd_web_id.write({'plan_id': line_id.guru_product_id.plan_duda_id.id})
            return {
                'name': _('Webs Shop'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': [self.env.ref('guru_pacom.guru_web_wzd_form_view').id],
                'res_model': 'guru.web.product.wzd',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': wzd_web_id.id,
                'context': {
                    'packet_product_line': rec.id,
                    'line_id': rec.order_line_id.id,
                    'order_id': rec.order_id.id,
                    'partner_id': rec.order_id.partner_id.id,
                },
            }
        
        elif product_type == 'web_vertical':
            wzd_web_id = self.env['guru.web.vertical.wzd'].create({'var_obj': 'Obj', 'is_lan': is_lan})
            line_id = rec.order_line_id.product_id.guru_packet_ids.filtered(
                lambda e: e.publishable_product_type == 'web_vertical')
            return {
                'name': _('Tiendas WIX'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': [self.env.ref('guru_pacom.guru_web_vertical_wzd_form_view').id],
                'res_model': 'guru.web.vertical.wzd',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': wzd_web_id.id,
                'context': {
                    'packet_product_line': rec.id,
                    'line_id': rec.order_line_id.id,
                    'order_id': rec.order_id.id,
                    'partner_id': rec.order_id.partner_id.id,
                },
            }
        
        else:
            raise UserError(f"El tipo de producto '{product_type}' no se reconoce.")

# TODO 04:
#  Refactorizar
def get_select_sequence(self):

    return [(str(i), str(i)) for i in range(1, 11)]
