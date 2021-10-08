# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ddt import data, ddt, unpack

from .base import BaseCase


@ddt
class TestOnchange(BaseCase):
    @data(
        ["year", False],
    )
    @unpack
    def test_account_asset_category_onchange_prorata(self, method_time, value_check):
        values = {"method_time": method_time}
        categ1 = self.obj_asset_category.new(values)
        categ1.onchange_prorata()
        self.assertEqual(categ1.prorata, value_check)
