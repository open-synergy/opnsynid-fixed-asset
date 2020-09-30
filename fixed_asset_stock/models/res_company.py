# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_capitalization_limit = fields.Float(
        string="Auto Capitalization Limit",
    )
