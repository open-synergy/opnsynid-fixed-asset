# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_number(self):
        _super = super(AccountInvoice, self)
        res = _super.action_number()
        for inv in self:
            move = inv.move_id
            assets = [
                aml.asset_id for aml in filter(lambda x: x.asset_id, move.line_id)
            ]
            ctx_asset = {"create_asset_from_move_line": True}
            for asset in assets:
                asset.with_context(ctx_asset).write({"code": inv.internal_number})
                asset_line_name = asset._get_depreciation_entry_name(0)
                asset_line = asset.depreciation_line_ids[0]
                ctx_asset_line = {"allow_asset_line_update": True}
                asset_line.with_context(ctx_asset_line).write({"name": asset_line_name})
        return res

    @api.multi
    def action_cancel(self):
        _super = super(AccountInvoice, self)
        res = _super.action_cancel()
        assets = []
        for inv in self:
            move = inv.move_id
            assets = move and [
                aml.asset_id for aml in filter(lambda x: x.asset_id, move.line_id)
            ]
        if assets:
            assets.unlink()
        return res

    @api.model
    def line_get_convert(self, line, part, date):
        _super = super(AccountInvoice, self)
        res = _super.line_get_convert(line, part, date)
        if line.get("asset_category_id"):
            if res.get("debit") or res.get("credit"):
                res["asset_category_id"] = line["asset_category_id"]
        return res

    @api.multi
    def inv_line_characteristic_hashcode(self, invoice_line):
        self.ensure_one()
        _super = super(AccountInvoice, self)
        res = _super.inv_line_characteristic_hashcode(invoice_line)
        res += "-%s" % invoice_line.get("asset_category_id", False)
        return res
