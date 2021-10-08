# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from ddt import ddt, file_data

from .base import BaseCase


@ddt
class TestWorklowAsset(BaseCase):
    @file_data("scenario_asset_workflow.yaml")
    def test_workflow_asset(self, attribute, workflow_steps):
        category = getattr(self, attribute["category_name"])
        purchase_value = attribute["purchase_value"]
        salvage_value = attribute["salvage_value"]
        day_start = attribute["day_start"]
        month_start = attribute["month_start"]
        if attribute["year_start"]:
            year_start = attribute["year_start"]
        else:
            year_start = date.today().year
        date_start = date(year_start, month_start, day_start).strftime("%Y-%m-%d")
        asset = self._create_asset_no_error(
            category, purchase_value, salvage_value, date_start
        )
        for workflow_step in workflow_steps:
            method_name = "action_asset_" + workflow_step["name"]
            if workflow_step["error"]:
                method_name += "_error"
            else:
                method_name += "_no_error"
            method_to_run = getattr(self, method_name)
            method_to_run(asset, attribute)
