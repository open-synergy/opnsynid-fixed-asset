# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _


class AssetDepreciationConfirmationWizard(models.TransientModel):
    _name = "asset.depreciation.confirmation.wizard"
    _description = "asset.depreciation.confirmation.wizard"

    @api.model
    def _default_period_id(self):
        context = self.env.context
        ctx = dict(context or {}, account_period_prefer_normal=True)
        periods = self.env["account.period"].with_context(ctx).find()
        if periods:
            return periods[0]
        else:
            return False

    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
        domain=[
            ("special", "=", False),
            ("state", "=", "draft")
        ],
        required=True,
        default=lambda self: self._default_period_id(),
        help="Choose the period for which you want to automatically "
             "post the depreciation lines of running assets",
     )

    @api.multi
    def asset_compute(self):
        self.ensure_one()
        obj_account_asset = \
            self.env["account.asset.asset"]
        asset_ids = obj_account_asset.search([
            ("state", "=", "open"),
            ("type", "=", "normal")
        ])
        created_move_ids = asset_ids._compute_entries(
            period_id=self.period_id, check_triggers=True)
        domain = "[('id', 'in', [" + \
            ','.join(map(str, created_move_ids)) + "])]"
        return {
            "name": _("Created Asset Moves"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "view_id": False,
            "domain": domain,
            "type": 'ir.actions.act_window',
        }
