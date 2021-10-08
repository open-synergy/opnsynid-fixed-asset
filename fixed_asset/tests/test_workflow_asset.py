# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from ddt import ddt, file_data

from .base import BaseCase


@ddt
class TestWorklowAsset(BaseCase):
    @file_data("scenario_asset_workflow.yaml")
    def test_workflow_asset(self, attribute, workflow_steps):
        category = getattr(self, attribute["category_name"])
        purchase_value = attribute["purchase_value"]
        salvage_value = attribute["salvage_value"]
        day_start_offset = attribute["day_start_offset"]
        month_start_offset = attribute["month_start_offset"]
        year_start_offset = attribute["year_start_offset"]
        asset = self._create_asset_no_error(
            category,
            purchase_value,
            salvage_value,
            day_start_offset,
            month_start_offset,
            year_start_offset,
        )
        for workflow_step in workflow_steps:
            method_name = "action_asset_" + workflow_step["name"]
            if workflow_step["error"]:
                method_name += "_error"
            else:
                method_name += "_no_error"
            method_to_run = getattr(self, method_name)
            method_to_run(asset, attribute)
