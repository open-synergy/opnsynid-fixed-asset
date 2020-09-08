# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ResConfig(models.TransientModel):
    _inherit = "account.asset.config_setting"

    complex_asset_installation_sequence_id = fields.Many2one(
        string="Complex Asset Installation Sequence",
        comodel_name="ir.sequence",
        related="company_id.complex_asset_installation_sequence_id",
        store=False,
    )
    complex_asset_installation_confirm_grp_ids = fields.Many2many(
        string="Allowed To Confirm Complex Asset Installation",
        comodel_name="res.groups",
        related="company_id.complex_asset_installation_confirm_grp_ids",
        store=False,
    )
    complex_asset_installation_valid_grp_ids = fields.Many2many(
        string="Allowed To Validate Complex Asset Installation",
        comodel_name="res.groups",
        related="company_id.complex_asset_installation_valid_grp_ids",
        store=False,
    )
    complex_asset_installation_cancel_grp_ids = fields.Many2many(
        string="Allowed To Cancel Complex Asset Installation",
        comodel_name="res.groups",
        related="company_id.complex_asset_installation_cancel_grp_ids",
        store=False,
    )
    complex_asset_installation_restart_grp_ids = fields.Many2many(
        string="Allowed To Restart Complex Asset Installation",
        comodel_name="res.groups",
        related="company_id.complex_asset_installation_restart_grp_ids",
        store=False,
    )
    complex_asset_installation_restart_val_grp_ids = fields.Many2many(
        string="Allowed To Restart Validation Complex Asset Installation",
        comodel_name="res.groups",
        related="company_id.complex_asset_installation_restart_val_grp_ids",
        store=False,
    )
    complex_asset_removal_sequence_id = fields.Many2one(
        string="Complex Asset Removal Sequence",
        comodel_name="ir.sequence",
        related="company_id.complex_asset_removal_sequence_id",
        store=False,
    )
    complex_asset_removal_confirm_grp_ids = fields.Many2many(
        string="Allowed To Confirm Complex Asset Removal",
        comodel_name="res.groups",
        related="company_id.complex_asset_removal_confirm_grp_ids",
        store=False,
    )
    complex_asset_removal_valid_grp_ids = fields.Many2many(
        string="Allowed To Validate Complex Asset Removal",
        comodel_name="res.groups",
        related="company_id.complex_asset_removal_valid_grp_ids",
        store=False,
    )
    complex_asset_removal_cancel_grp_ids = fields.Many2many(
        string="Allowed To Cancel Complex Asset Removal",
        comodel_name="res.groups",
        related="company_id.complex_asset_removal_cancel_grp_ids",
        store=False,
    )
    complex_asset_removal_restart_grp_ids = fields.Many2many(
        string="Allowed To Restart Complex Asset Removal",
        comodel_name="res.groups",
        related="company_id.complex_asset_removal_restart_grp_ids",
        store=False,
    )
    complex_asset_removal_restart_val_grp_ids = fields.Many2many(
        string="Allowed To Restart Validation Complex Asset Removal",
        comodel_name="res.groups",
        related="company_id.complex_asset_removal_restart_val_grp_ids",
        store=False,
    )
