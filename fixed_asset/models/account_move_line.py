# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="account.asset.asset",
        ondelete="restrict",
    )
    asset_category_id = fields.Many2one(
        string="Asset Category",
        comodel_name="account.asset.category",
    )

    @api.multi
    def onchange_account_id(self, account_id=False, partner_id=False):
        _super = super(AccountMoveLine, self)
        res = _super.onchange_account_id(account_id, partner_id)
        obj_account_account = self.env["account.account"]
        if account_id:
            asset_category =\
                obj_account_account.browse(account_id).asset_category_id
            if asset_category:
                if not res.get("value", False):
                    res["value"] = {}
                else:
                    res["value"]["asset_category_id"] = asset_category.id
        return res

    @api.model
    def _get_fields_affects_asset_move_line(self):
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

    @api.model
    def create(self, vals):
        _super = super(AccountMoveLine, self)
        res = _super.create(vals)

        context = self.env.context
        if vals.get("asset_id") and not context.get("allow_asset"):
            raise UserError(
                _("Error!"),
                _("You are not allowed to link "
                  "an accounting entry to an asset."
                  "\nYou should generate such entries from the asset."))
        if vals.get("asset_category_id"):
            obj_account_asset = self.env["account.asset.asset"]
            obj_account_move = self.env["account.move"]
            move = obj_account_move.browse(vals["move_id"])
            asset_value = vals["debit"] or -vals["credit"]
            asset_vals = {
                "name": vals["name"],
                "category_id": vals["asset_category_id"],
                "purchase_value": asset_value,
                "partner_id": vals["partner_id"],
                "date_start": move.date,
            }
            if context.get("company_id"):
                asset_vals["company_id"] = context["company_id"]
            ctx = dict(context, create_asset_from_move_line=True,
                       move_id=vals['move_id'])
            asset_id = obj_account_asset.with_context(ctx).create(asset_vals)
            asset_id.onchange_category_id()
            vals["asset_id"] = asset_id
        return res

    @api.multi
    def write(self, vals, context=None, check=True):
        _super = super(AccountMoveLine, self)
        res = _super.write(vals, context=context, check=check)
        context = self.env.context
        fields = self._get_fields_affects_asset_move_line()
        for move_line in self:
            if move_line.asset_id.id:
                if vals in fields:
                    raise UserError(
                        _("Error!"),
                        _("You cannot change an accounting item "
                          "linked to an asset depreciation line."))
        if vals.get("asset_id"):
            raise UserError(
                _("Error!"),
                _("You are not allowed to link "
                  "an accounting entry to an asset."
                  "\nYou should generate such entries from the asset."))
        if vals.get("asset_category_id"):
            assert len(self) == 1, \
                "This option should only be used for a single id at a time."
            obj_account_asset = self.env["account.asset.asset"]
            for aml in self:
                if vals["asset_category_id"] == aml.asset_category_id.id:
                    continue
                debit = "debit" in vals and vals.get("debit", 0.0) or aml.debit
                credit = "credit" in vals and \
                    vals.get("credit", 0.0) or aml.credit
                asset_value = debit - credit
                partner_id = "partner" in vals and \
                    vals.get("partner", False) or aml.partner_id.id
                date_start = "date" in vals and \
                    vals.get("date", False) or aml.date
                asset_vals = {
                    "name": vals.get("name") or aml.name,
                    "category_id": vals["asset_category_id"],
                    "purchase_value": asset_value,
                    "partner_id": partner_id,
                    "date_start": date_start,
                    "company_id": vals.get("company_id") or aml.company_id.id,
                }
                ctx = dict(context, create_asset_from_move_line=True,
                           move_id=aml.move_id.id)
                asset_id =\
                    obj_account_asset.with_context(ctx).create(asset_vals)
                asset_id.onchange_category_id()
                vals["asset_id"] = asset_id
        return res
