# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        # do actual processing
        result = super(StockMove, self).action_done()
        for move in self:
            for quant in move.quant_ids:
                if (
                    quant.lot_id
                    and quant.lot_id.asset_id
                    and quant.lot_id._get_initial_move() == move
                ):
                    quant.lot_id.asset_id.write(
                        {
                            "date_start": move.date,
                        }
                    )
                    quant.lot_id.asset_id.depreciation_line_ids[0].write(
                        {
                            "line_date": quant.lot_id.asset_id._get_date_start(),
                        }
                    )
        return result
