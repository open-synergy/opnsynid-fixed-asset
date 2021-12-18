# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    asset_category_id = fields.Many2one(
        string="Default Asset Category",
        comodel_name="account.asset.category",
    )
