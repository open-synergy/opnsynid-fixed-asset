# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMassDepreciation(models.TransientModel):
    _name = "account.mass_depreciation"
    _description = "Mass Depreciation"

    category_ids = fields.Many2many(
        string="Categories",
        comodel_name="fixed.asset.category",
    )
    date = fields.Date(
        string="Date Depreciation",
        required=True,
    )

    def action_confirm(self):
        for wizard in self.sudo():
            wizard._mass_depreciate()

    def _mass_depreciate(self):
        self.ensure_one()
        obj_line = self.env["fixed.asset.depreciation.line"]
        criteria = [
            ("asset_id.state", "=", "open"),
            ("type", "=", "depreciate"),
            ("init_entry", "=", False),
            ("move_id", "=", False),
            ("line_date", "=", self.date),
        ]
        if self.category_ids:
            criteria.append(("asset_id.category_id", "in", self.category_ids.ids))

        for line in obj_line.search(criteria):
            line.create_move()
