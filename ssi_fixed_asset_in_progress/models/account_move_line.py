# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _name = "account.move.line"

    fixed_asset_in_progress_id = fields.Many2one(
        string="Fixed Asset in Progress",
        comodel_name="fixed_asset.in_progress",
        ondelete="set null",
        copy=False,
        readonly=True,
    )

    def _create_asset_in_progress_reverse_ml(self, move):
        self.ensure_one()
        AML = self.env["account.move.line"]
        data = self._prepare_asset_in_progress_reverse_ml(move)
        AML.with_context(check_move_validity=False).create(data)

    def _prepare_asset_in_progress_reverse_ml(self, move):
        self.ensure_one()
        name = "Reverse - %s" % (self.name)
        return {
            "move_id": move.id,
            "name": name,
            "account_id": self.account_id.id,
            "debit": 0.0,
            "credit": self.debit,
        }
