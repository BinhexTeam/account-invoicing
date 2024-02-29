# Copyright (C) 2019-Today: Odoo Community Association
# @ 2019-Today: Binhex - www.binhex.cloud -
#   Christian-RB <c.ramos@binhex.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiced(self):
        """
        Override to get the invoices related to the stock moves of the sale order
        """
        super()._get_invoiced()
        for order in self:
            invoices = order.order_line.move_ids.invoice_line_ids.move_id.filtered(
                lambda r: r.move_type in ("out_invoice", "out_refund")
            )
            order.invoice_ids = [(6, 0, invoices.ids)]
            order.invoice_count = len(invoices)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("move_ids.invoice_line_ids.move_id.state")
    def _get_invoice_qty(self):
        """
        Override to get the quantity invoiced related to the stock moves of the sale order
        """
        super()._get_invoice_qty()
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.move_ids.invoice_line_ids:
                if invoice_line.move_id.state != "cancel":
                    if invoice_line.move_id.move_type == "out_invoice":
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
                    elif invoice_line.move_id.move_type == "out_refund":
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
            line.qty_invoiced = qty_invoiced
