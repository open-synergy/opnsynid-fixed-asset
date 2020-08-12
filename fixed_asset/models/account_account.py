# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    asset_category_id = fields.Many2one(
        string="Asset Category",
        comodel_name="account.asset.category",
        help="Default Asset Category when creating invoice lines "
             "with this account.",
     )
