# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    asset_useful_life_sequence_id = fields.Many2one(
        string="Fixed Asset Useful Life Estimation Change Sequence",
        comodel_name="ir.sequence",
    )
    asset_useful_life_confirm_grp_ids = fields.Many2many(
        string="Allowed To Confirm Fixed Asset Useful Life Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_useful_life_allowed_confirm",
        column1="company_id",
        column2="group_id",
    )
    asset_useful_life_valid_grp_ids = fields.Many2many(
        string="Allowed To Validate Fixed Asset Useful Life Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_useful_life_allowed_valid",
        column1="company_id",
        column2="group_id",
    )
    asset_useful_life_cancel_grp_ids = fields.Many2many(
        string="Allowed To Cancel Fixed Asset Useful Life Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_useful_life_allowed_cancel",
        column1="company_id",
        column2="group_id",
    )
    asset_useful_life_restart_grp_ids = fields.Many2many(
        string="Allowed To Restart Fixed Asset Useful Life Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_useful_life_allowed_restart",
        column1="company_id",
        column2="group_id",
    )
    asset_useful_life_restart_validation_grp_ids = fields.Many2many(
        string="Allowed To Restart Validation Asset Useful Life Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_useful_life_allowed_restart_validation",
        column1="company_id",
        column2="group_id",
    )
    asset_salvage_sequence_id = fields.Many2one(
        string="Fixed Asset Salvage Value Estimation Change Sequence",
        comodel_name="ir.sequence",
    )
    asset_salvage_confirm_grp_ids = fields.Many2many(
        string="Allowed To Confirm Fixed Asset Salvage Value "
               "Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_salvage_allowed_confirm",
        column1="company_id",
        column2="group_id",
    )
    asset_salvage_open_grp_ids = fields.Many2many(
        string="Allowed To Start Fixed Asset Salvage Value "
               "Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_salvage_allowed_open",
        column1="company_id",
        column2="group_id",
    )
    asset_salvage_valid_grp_ids = fields.Many2many(
        string="Allowed To Validate Fixed Asset Salvage Value "
               "Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_salvage_allowed_valid",
        column1="company_id",
        column2="group_id",
    )
    asset_salvage_cancel_grp_ids = fields.Many2many(
        string="Allowed To Cancel Fixed Asset Salvage Value "
               "Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_salvage_allowed_cancel",
        column1="company_id",
        column2="group_id",
    )
    asset_salvage_restart_grp_ids = fields.Many2many(
        string="Allowed To Restart Fixed Asset Salvage Value "
               "Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_salvage_allowed_restart",
        column1="company_id",
        column2="group_id",
    )
    asset_salvage_restart_validation_grp_ids = fields.Many2many(
        string="Allowed To Restart Validation Asset Salvage Value "
               "Estimation Change",
        comodel_name="res.groups",
        relation="rel_company_asset_salvage_allowed_restart_validation",
        column1="company_id",
        column2="group_id",
    )
