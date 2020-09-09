# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class AccountAssetCategory(models.Model):
    _inherit = "account.asset.category"

    improvement_journal_id = fields.Many2one(
        string="Improvement Journal",
        comodel_name="account.journal",
    )
