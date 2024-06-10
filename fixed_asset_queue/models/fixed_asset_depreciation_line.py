# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models

from odoo.addons.queue_job.job import job


class FixedAssetDepreciationLine(models.Model):
    _name = "fixed.asset.depreciation.line"
    _inherit = "fixed.asset.depreciation.line"

    @api.multi
    @job
    def create_move(self):
        _super = super(FixedAssetDepreciationLine, self)
        _super.create_move()
