# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from ddt import data, ddt, file_data, unpack

from .base import BaseCase


@ddt
class TestOnchange(BaseCase):
    @data(
        ["view", False],
        ["normal", date(date.today().year, 1, 1).strftime("%Y-%m-%d")],
    )
    @unpack
    def test_onchange_type_date_start(self, asset_type, value_check):
        values = {
            "date_start": date(date.today().year, 1, 1).strftime("%Y-%m-%d"),
            "type": asset_type,
        }
        asset = self.obj_asset.new(values)
        asset.onchange_type_date_start()
        self.assertEqual(asset.date_start, value_check)

    @data(
        ["view", "asset_category_building", False],
        ["normal", "asset_category_building", "asset_category_building"],
    )
    @unpack
    def test_onchange_type_category_id(self, asset_type, asset_category, value_check):
        category = getattr(self, asset_category)
        to_be_check = value_check
        if value_check:
            to_be_check = category
        else:
            to_be_check = self.obj_asset_category
        values = {
            "type": asset_type,
            "category_id": category.id,
        }
        asset = self.obj_asset.new(values)
        asset.onchange_type_category_id()
        self.assertEqual(asset.category_id, to_be_check)

    @data(
        ["normal", 6000.00, 6000.00],
        ["view", 6000.00, 0.00],
    )
    @unpack
    def test_onchange_type_purchase_value(
        self, asset_type, purchase_value, value_check
    ):
        values = {
            "type": asset_type,
            "purchase_value": purchase_value,
        }
        asset = self.obj_asset.new(values)
        asset.onchange_type_purchase_value()
        self.assertEqual(asset.purchase_value, value_check)

    @data(
        ["normal", 6000.00, 6000.00],
        ["view", 6000.00, 0.00],
    )
    @unpack
    def test_onchange_type_salvage_value(self, asset_type, salvage_value, value_check):
        values = {
            "type": asset_type,
            "salvage_value": salvage_value,
        }
        asset = self.obj_asset.new(values)
        asset.onchange_type_salvage_value()
        self.assertEqual(asset.salvage_value, value_check)

    @data(
        ["view", "001", False],
        ["normal", "001", "001"],
    )
    @unpack
    def test_onchange_type_code(self, asset_type, code, value_check):
        values = {
            "code": code,
            "type": asset_type,
        }
        asset = self.obj_asset.new(values)
        asset.onchange_type_code()
        self.assertEqual(asset.code, value_check)

    @file_data("scenario_asset_onchange_category_id.yaml")
    def test_onchange_category_id(self, category_name, to_be_check):
        category = getattr(self, category_name)
        if to_be_check["account_analytic"]:
            analytic = getattr(self, to_be_check["account_analytic"])
        else:
            analytic = self.obj_analytic
        values = {
            "category_id": category.id,
        }
        asset = self.obj_asset.new(values)
        asset.onchange_category_id()
        self.assertEqual(asset.method, to_be_check["method"])
        self.assertEqual(asset.method_number, to_be_check["method_number"])
        self.assertEqual(asset.method_time, to_be_check["method_time"])
        self.assertEqual(asset.method_period, to_be_check["method_period"])
        self.assertEqual(
            asset.method_progress_factor, to_be_check["method_progress_factor"]
        )
        self.assertEqual(asset.prorata, to_be_check["prorata"])
        self.assertEqual(asset.account_analytic_id, analytic)
