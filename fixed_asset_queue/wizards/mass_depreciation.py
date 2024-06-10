# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models


class AccountMassDepreciation(models.TransientModel):
    _name = "account.mass_depreciation"
    _inherit = "account.mass_depreciation"

    @api.multi
    def action_confirm_queue(self):
        for wizard in self:
            wizard._mass_depreciate_queue()

    @api.multi
    def _mass_depreciate_queue(self):
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
            description = "Fixed asset depreciation ID %s %s" % (
                line.asset_id.id,
                self.date,
            )
            line.with_context().with_delay(description=_(description)).create_move()
