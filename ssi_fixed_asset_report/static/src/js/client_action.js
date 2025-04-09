odoo.define("ssi_fixed_asset_report.client_action", function (require) {
    "use strict";

    var ReportAction = require("report.client_action");
    var core = require("web.core");

    var QWeb = core.qweb;

    const AFRReportAction = ReportAction.extend({
        start: function () {
            return this._super.apply(this, arguments).then(() => {
                this.$buttons = $(
                    QWeb.render(
                        "ssi_fixed_asset_report.client_action.ControlButtons",
                        {}
                    )
                );
                this.$buttons.on("click", ".o_report_print", this.on_click_print);
                this.$buttons.on("click", ".o_report_export", this.on_click_export);

                this.controlPanelProps.cp_content = {
                    $buttons: this.$buttons,
                };

                this._controlPanelWrapper.update(this.controlPanelProps);
            });
        },

        on_click_export: function () {
            const action = {
                type: "ir.actions.report",
                report_type: "xlsx",
                report_name: "a_f_r.report_fixed_asset_yearly_xlsx",
                report_file: "report_fixed_asset_yearly",
                data: this.data,
                context: this.context,
                display_name: this.title,
            };
            return this.do_action(action);
        },
    });

    core.action_registry.add("ssi_fixed_asset_report.client_action", AFRReportAction);

    return AFRReportAction;
});
