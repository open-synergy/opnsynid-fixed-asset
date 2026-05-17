# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSalvageValueChangeDocumensoSigning(YamlTransactionCase):
    def test_salvage_value_change_documenso_signing(self):
        self.run_yaml_scenario("test_data_salvage_value_change_documenso_signing.yaml")
