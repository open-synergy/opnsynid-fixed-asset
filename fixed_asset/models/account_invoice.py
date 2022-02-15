# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def line_get_convert(self, line, part):
        _super = super(AccountInvoice, self)
        res = _super.line_get_convert(line, part)
        if line.get("fixed_asset_category_id"):
            if res.get("debit") or res.get("credit"):
                res["fixed_asset_category_id"] = line["fixed_asset_category_id"]
        return res

    @api.multi
    def inv_line_characteristic_hashcode(self, invoice_line):
        self.ensure_one()
        _super = super(AccountInvoice, self)
        res = _super.inv_line_characteristic_hashcode(invoice_line)
        res += "-%s" % invoice_line.get("fixed_asset_category_id", False)
        return res

    @api.model
    def invoice_line_move_line_get(self):
        _super = super(AccountInvoice, self)
        result = _super.invoice_line_move_line_get()
        if self.type == "in_invoice":
            obj_line = self.env["account.invoice.line"]
            for index, data in enumerate(result):
                line_id = data["invl_id"]
                line = obj_line.browse([line_id])[0]
                if line.fixed_asset_category_id:
                    result[index].update(
                        {"fixed_asset_category_id": line.fixed_asset_category_id.id}
                    )
        return result
