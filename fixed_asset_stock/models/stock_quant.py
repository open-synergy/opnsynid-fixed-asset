# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = "stock.quant"

    asset_id = fields.Many2one(
        string="Fixed Asset",
        comodel_name="account.asset.asset",
        related="lot_id.asset_id",
        store=True,
    )
    asset_value = fields.Float(
        string="Asset Value",
        related="lot_id.asset_id.asset_value",
        store=False,
    )
    join_asset_ids = fields.One2many(
        string="Join Asset",
        comodel_name="account.asset.asset",
        related="lot_id.join_asset_ids",
    )
    join_asset_id = fields.Many2one(
        string="Join Asset",
        comodel_name="account.asset.asset",
        related="lot_id.join_asset_id",
    )
    lot_relation = fields.Selection(
        string="Lot Relation",
        selection=[
            ("o2o", "Lot is an asset"),
            ("o2m", "One lot split into multiple asset"),
            ("m2o", "Multiple lot join into one asset"),
            ("no", "No relation"),
        ],
        related="lot_id.lot_relation",
        store=True,
    )

    @api.model
    def create(self, values):
        _super = super(StockQuant, self)
        result = _super.create(values)
        if result._check_autocreate_fixed_asset():
            result._create_fixed_asset()
        return result

    @api.multi
    def _get_salvage_value(self, value=0.0):
        self.ensure_one()
        result = 0.0
        product = self.lot_id.product_id
        if product.fixed_asset_salvage_value_computation == "fixed":
            result = product.fixed_asset_salvage_value
        else:
            result = (product.fixed_asset_salvage_value / 100.0) * value
        return result

    @api.multi
    def _create_fixed_asset(self):
        self.ensure_one()
        obj_asset = self.env["account.asset.asset"]
        asset = obj_asset.create(self._prepare_fixed_asset_data())
        self.lot_id.write({"asset_id": asset.id})
        asset.depreciation_line_ids[0].with_context(allow_asset_line_update=True).write(
            {
                "line_date": asset._get_date_start(),
            }
        )

    @api.multi
    def _check_autocreate_fixed_asset(self):
        self.ensure_one()
        result = False
        move = self.history_ids[0]
        if (
            self.lot_id
            and self.product_id.auto_capitalization
            and not move.override_auto_capitalization
            and self.cost > self.company_id.auto_capitalization_limit
        ):
            result = True
        elif (
            self.lot_id and move.override_auto_capitalization and move.auto_create_asset
        ):
            result = True
        return result

    @api.multi
    def _get_asset_partner(self):
        self.ensure_one()
        move = self.history_ids[0]
        if move.picking_id.partner_id:
            return move.picking_id.partner_id
        else:
            return False

    @api.multi
    def _get_asset_category(self):
        self.ensure_one()
        result = False
        product = self.product_id
        categ = product.categ_id
        if product.asset_category_id:
            result = product.asset_category_id

        if not result and categ.asset_category_id:
            result = categ.asset_category_id

        if not result:
            error_msg = _("No asset category defined")
            raise UserError(error_msg)

        return result

    @api.multi
    def _prepare_fixed_asset_data(self):
        self.ensure_one()
        product = self.product_id
        move = self.history_ids[0]  # TODO: Error prone?
        categ = self._get_asset_category()
        partner = self._get_asset_partner()
        purchase_value = self.inventory_value
        salvage_value = self._get_salvage_value(purchase_value)
        return {
            "name": product.name,
            "code": self.lot_id.name,
            "purchase_value": purchase_value,
            "salvage_value": salvage_value,
            "category_id": categ.id,
            "parent_id": False,
            "partner_id": partner and partner.id or False,
            "date_start": self.in_date,
            "method": categ.method,
            "type": "normal",
            "company_id": move.company_id.id,
            "method_number": categ.method_number,
            "method_period": categ.method_period,
            "method_progress_factor": categ.method_progress_factor,
            "method_time": categ.method_time,
            "prorata": categ.prorata,
            "lot_id": self.lot_id.id,
            "product_id": product.id,
            "date_min_prorate": categ.date_min_prorate,
        }
