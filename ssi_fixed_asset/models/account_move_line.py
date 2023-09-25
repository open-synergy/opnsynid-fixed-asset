# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fixed_asset_id = fields.Many2one(
        string="Fixed Asset",
        comodel_name="fixed.asset.asset",
        ondelete="set null",
        copy=False,
        readonly=True,
    )
    fixed_asset_ids = fields.One2many(
        string="Fixed Assets",
        comodel_name="fixed.asset.asset",
        inverse_name="asset_acquisition_move_line_id",
    )

    def action_create_fixed_asset(self):
        for record in self.sudo():
            if record.quantity > 0.0:
                num_of_asset = int(record.quantity)
            else:
                num_of_asset = 1
            for _asset_acount in range(0, num_of_asset):
                record._create_fixed_asset()

    def _create_fixed_asset(self):
        self.ensure_one()

        if not self._check_fixed_asset_exist():
            error_message = """
            Context: Creating fixed asset from accounting entry item
            Database ID: %s
            Problem: A fixed asset already created from this accounting entry line
            Solution: Do not try to create fixed asset from this accounting entry line
            """ % (
                self.id
            )
            raise UserError(_(error_message))

        FixedAsset = self.env["fixed.asset.asset"]
        vals = self._prepare_create_fixed_asset()
        asset_cache = FixedAsset.new(vals)
        asset_cache.onchange_category_id()
        asset_cache.onchange_date_min_prorate()
        asset_cache.onchange_amount_depreciation_line()
        asset_cache.onchange_line_date_depreciation_line()
        asset_cache.onchange_method_time()
        asset_cache.onchange_type_date_start()
        asset_cache.onchange_type_category_id()
        asset_cache.onchange_type_purchase_value()
        asset_cache.onchange_type_salvage_value()
        asset_cache.onchange_type_code()
        asset_cache.onchange_type_depreciation_line_ids()
        FixedAsset.create(asset_cache._convert_to_write(asset_cache._cache))

    def _prepare_create_fixed_asset(self):
        fixed_asset_category = self._get_fixed_asset_category()
        if self.quantity > 0.0:
            num_of_asset = int(self.quantity)
        else:
            num_of_asset = 1
        return {
            "name": self.name,
            "category_id": fixed_asset_category.id,
            "purchase_value": self.balance / float(num_of_asset),
            "partner_id": self.partner_id and self.partner_id.id or False,
            "date_start": fields.Date.to_string(self.date),
            "account_analytic_id": self.analytic_account_id
            and self.analytic_account_id.id
            or False,
            "asset_acquisition_move_line_id": self.id,
        }

    def _get_fixed_asset_category(self):
        self.ensure_one()
        if not self.account_id.fixed_asset_category_id:
            error_message = """
            Context: Creating fixed asset from accounting entry item
            Database ID: %s
            Problem: Account does not have fixed asset category
            Solution: Setup fixed asset category on account used on accounting entry item
            """ % (
                self.id
            )
            raise UserError(_(error_message))
        return self.account_id.fixed_asset_category_id

    def _check_fixed_asset_exist(self):
        self.ensure_one()
        result = True
        if self.fixed_asset_id:
            result = False
        return result
