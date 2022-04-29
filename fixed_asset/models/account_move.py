# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tests.common import Form


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
            "fixed_asset_category_id",
            "fixed_asset_id",
        ]
        return fields

    def write(self, vals):
        FIELDS_AFFECTS_ASSET = self._get_fields_affects_asset_move()
        if set(vals).intersection(FIELDS_AFFECTS_ASSET):
            deprs = self.env["fixed.asset.depreciation.line"].search(
                [("move_id", "in", self.ids), ("type", "=", "depreciate")]
            )
            if deprs:
                raise UserError(
                    _(
                        "You cannot change an accounting entry "
                        "linked to an asset depreciation line."
                    )
                )
        return super().write(vals)

    def _prepare_asset_vals(self, aml):
        depreciation_base = aml.balance
        return {
            "name": aml.name,
            "code": self.name,
            "fixed_asset_category_id": aml.fixed_asset_category_id,
            "purchase_value": depreciation_base,
            "partner_id": aml.partner_id,
            "date_start": self.date,
            "account_analytic_id": aml.analytic_account_id,
        }

    def action_post(self):
        super().action_post()
        for move in self:
            for aml in move.line_ids.filtered(
                lambda line: line.fixed_asset_category_id and not line.tax_line_id
            ):
                vals = move._prepare_asset_vals(aml)
                if not aml.name:
                    raise UserError(
                        _("Asset name must be set in the label of the line.")
                    )
                if aml.fixed_asset_id:
                    continue
                asset_form = Form(
                    self.env["fixed.asset.asset"]
                    .with_company(move.company_id)
                    .with_context(create_asset_from_move_line=True, move_id=move.id)
                )
                for key, val in vals.items():
                    setattr(asset_form, key, val)
                asset = asset_form.save()
                asset.analytic_tag_ids = aml.analytic_tag_ids
                aml.with_context(
                    allow_asset=True, allow_asset_removal=True
                ).fixed_asset_id = asset.id
            refs = [
                "<a href=# data-oe-model=fixed.asset.asset data-oe-id=%s>%s</a>"
                % tuple(name_get)
                for name_get in move.line_ids.filtered(
                    "fixed_asset_category_id"
                ).fixed_asset_id.name_get()
            ]
            if refs:
                message = _("This invoice created the asset(s): %s") % ", ".join(refs)
                move.message_post(body=message)

    def button_draft(self):
        invoices = self.filtered(lambda r: r.is_purchase_document())
        if invoices:
            invoices.line_ids.fixed_asset_id.unlink()
        super().button_draft()

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super()._reverse_move_vals(default_values, cancel)
        if move_vals["move_type"] not in ("out_invoice", "out_refund"):
            for line_command in move_vals.get("line_ids", []):
                line_vals = line_command[2]  # (0, 0, {...})
                asset = self.env["fixed.asset.asset"].browse(line_vals["asset_id"])
                # We remove the asset if we recognize that we are reversing
                # the asset creation
                if asset:
                    asset_line = self.env["fixed.asset.depreciation.line"].search(
                        [("asset_id", "=", asset.id), ("type", "=", "create")], limit=1
                    )
                    if asset_line and asset_line.move_id == self:
                        asset.unlink()
                        line_vals.update(
                            fixed_asset_category_id=False, fixed_asset_id=False
                        )
        return move_vals
