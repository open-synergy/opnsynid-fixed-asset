# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from openerp.tests.common import TransactionCase


class BaseCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(BaseCase, self).setUp(*args, **kwargs)
        self.obj_asset_category = self.env["account.asset.category"]
        self.obj_asset = self.env["account.asset.asset"]
        self.obj_move = self.env["account.move"]
        self.obj_move_line = self.env["account.move.line"]
        self.obj_period = self.env["account.period"]
        self.obj_user = self.env["res.users"]
        self.obj_group = self.env["res.groups"]
        self.obj_analytic = self.env["account.analytic.account"]

        self.group_employee = self.env.ref("base.group_user")

        self.asset_category_building = self.env.ref("fixed_asset.demo_asset_category1")
        self.asset_category_vehicle = self.env.ref("fixed_asset.demo_asset_category2")
        self.asset_category_equipment = self.env.ref("fixed_asset.demo_asset_category2")
        return result

    def _create_asset_no_error(
        self,
        category,
        purchase_value,
        salvage_value,
        day_start_offset,
        month_start_offset,
        year_start_offset,
    ):
        dt_start = datetime(date.today().year, 1, 1)
        dt_start = dt_start + relativedelta(
            years=year_start_offset, months=month_start_offset, days=day_start_offset
        )
        date_start = dt_start.strftime("%Y-%m-%d")
        values = {
            "category_id": category.id,
            "type": "normal",
            "name": "Test Asset",
            "code": "/",
            "date_start": date_start,
            "purchase_value": purchase_value,
            "salvage_value": salvage_value,
        }
        rec_cache = self.obj_asset.new(values)
        rec_cache.onchange_category_id()
        rec_cache.onchange_date_min_prorate()
        rec_cache.onchange_amount_depreciation_line()
        rec_cache.onchange_line_date_depreciation_line()
        rec_cache.onchange_method_time()
        rec_cache.onchange_type_date_start()
        rec_cache.onchange_type_category_id()
        rec_cache.onchange_type_purchase_value()
        rec_cache.onchange_type_salvage_value()
        rec_cache.onchange_type_code()
        rec_cache.onchange_type_depreciation_line_ids()
        values = rec_cache._convert_to_write(rec_cache._cache)
        asset = self.obj_asset.create(values)
        return asset

    def action_asset_create_depreciation_table_no_error(self, asset, attribute):
        asset.compute_depreciation_board()

    def action_asset_confirm_no_error(self, asset, attribute):
        asset.action_confirm()
        self.assertEqual(asset.state, "confirm")

    def action_asset_approve_no_error(self, asset, attribute):
        asset.restart_validation()
        self.assertEqual(asset.definition_id.name, "Fixed Asset - (test)")
        asset.invalidate_cache()
        asset.validate_tier()
        self.assertTrue(asset.validated)
        self.assertEqual(asset.state, "open")

    def action_asset_cancel_no_error(self, asset, attribute):
        asset.action_cancel()
        self.assertEqual(asset.state, "cancel")

    def action_asset_restart_no_error(self, asset, attribute):
        asset.action_restart()
        self.assertEqual(asset.state, "draft")

    def action_asset_depreciate_no_error(self, asset, attribute):
        index = 0
        depreciations = asset.depreciation_line_ids.filtered(
            lambda r: r.type == "depreciate"
            and not r.move_check
            and not r.subtype_id
            and not r.init_entry
        )
        self.assertEqual(len(depreciations), len(attribute["depreciation"]))
        for schedule in attribute["depreciation"]:
            depreciation_line = depreciations[index]
            depreciation_line.create_move()
            self.assertEqual(asset.value_residual, schedule["asset_value"])
            self.assertEqual(asset.value_depreciated, schedule["depreciated_value"])
            index += 1
        if len(depreciations) == 0:
            self.assertEqual(asset.state, "close")
