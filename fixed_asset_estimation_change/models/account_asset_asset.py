# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class AccountAsset(models.Model):
    _inherit = "account.asset.asset"

    useful_life_ids = fields.One2many(
        string="Useful Life Estimation Change",
        comodel_name="account.asset_change_estimation_useful_life",
        inverse_name="asset_id",
        readonly=True,
    )
