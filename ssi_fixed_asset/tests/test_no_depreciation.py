# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import Form, tagged


@tagged("post_install", "-at_install")
class TestNoDepreciation(YamlTransactionCase):
    def test_no_depreciation(self):
        self.run_yaml_scenario("test_data_no_depreciation.yaml")

    def test_onchange_category_id_no_depreciation_resets_method(self):
        """Memilih kategori no_depreciation harus mereset method_number ke 0."""
        account_asset = self.env["account.account"].create(
            {
                "name": "Test Asset Account OC",
                "code": "TND_OC_A01",
                "user_type_id": self.env.ref(
                    "account.data_account_type_non_current_assets"
                ).id,
                "internal_type": "other",
            }
        )
        category = self.env["fixed.asset.category"].create(
            {
                "name": "Land Category OC",
                "code": "TND_OC_C01",
                "no_depreciation": True,
                "account_asset_id": account_asset.id,
            }
        )
        form = Form(self.env["fixed.asset.asset"])
        form.name = "Land Test OC"
        form.category_id = category
        self.assertEqual(form.method_number, 0)
        self.assertFalse(form.prorata)
