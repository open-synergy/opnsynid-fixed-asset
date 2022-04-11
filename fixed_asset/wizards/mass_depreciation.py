# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


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

    @api.multi
    def action_confirm(self):
        for wizard in self:
            wizard._mass_depreciate()

    @api.multi
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
