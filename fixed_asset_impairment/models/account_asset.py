# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset.asset"

    @api.multi
    @api.depends(
        "impairment_ids",
        "impairment_ids.state",
        "impairment_reversal_ids",
        "impairment_reversal_ids.state",
        "value_residual",
    )
    def _compute_impairment(self):
        for asset in self:
            impairment = reversal = 0.0
            for imp in asset.impairment_ids.filtered(lambda r: r.state == "valid"):
                impairment += imp.impairment_amount
            for rev in asset.impairment_reversal_ids.filtered(
                lambda r: r.state == "valid"
            ):
                reversal += rev.impairment_amount
            asset.amount_impairment = impairment - reversal
            asset.amount_residual_impairment = (
                asset.value_residual - asset.amount_impairment
            )

    impairment_ids = fields.One2many(
        string="Impairment",
        comodel_name="account.asset.impairment",
        inverse_name="asset_id",
        readonly=True,
    )
    impairment_reversal_ids = fields.One2many(
        string="Impairment Reversal",
        comodel_name="account.asset.impairment_reversal",
        inverse_name="asset_id",
        readonly=True,
    )
    amount_impairment = fields.Float(
        string="Impairment Value",
        compute="_compute_impairment",
    )
    amount_residual_impairment = fields.Float(
        string="Residual - Impairment Value",
        compute="_compute_impairment",
    )
