# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_fields_affects_asset_move(self):
        fields = [
            "credit",
            "debit",
            "account_id",
            "journal_id",
            "date",
            "asset_category_id",
            "asset_id",
            "tax_code_id",
            "tax_amount",
        ]
        return fields

    @api.multi
    def unlink(self):
        _super = super(AccountMove, self)
        res = _super.unlink()
        context = self.env.context
        obj_depreciation_line = self.env["account.asset.depreciation.line"]
        for move_id in self:
            depr_ids = obj_depreciation_line.search([
                ("move_id", "=", move_id.id),
                ("type", "in", ["depreciate", "remove"])])
            if depr_ids and not context.get("unlink_from_asset"):
                raise UserError(
                    _("Error!"),
                    _("You are not allowed to remove an accounting entry "
                      "linked to an asset."
                      "\nYou should remove such entries from the asset."))
            depr_ids.write({"move_id": False})
        return res

    @api.multi
    def write(self, vals):
        _super = super(AccountMove, self)
        res = _super.write(vals)
        fields = self._get_fields_affects_asset_move()
        if vals in fields:
            obj_depreciation_line = \
                self.env["account.asset.depreciation.line"]
            for move_id in self:
                depr_ids = obj_depreciation_line.search([
                    ("move_id", "=", move_id.id),
                    ("type", "=", "depreciate")])
                if depr_ids:
                    raise UserError(
                        _("Error!"),
                        _("You cannot change an accounting entry "
                          "linked to an asset depreciation line."))
        return res
