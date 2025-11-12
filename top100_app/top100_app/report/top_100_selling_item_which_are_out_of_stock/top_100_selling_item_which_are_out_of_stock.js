// Copyright (c) 2025
// Report: Top Selling Items Which Are Out of Stock
// Author: Sai More

frappe.query_reports["Top 50 Selling Items Which Are Out of Stock"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        },
        {
            fieldname: "limit",
            label: __("Top Records"),
            fieldtype: "Select",
            options: ["50", "100"],
            default: "50",
            reqd: 1
        }
    ],

    onload: function(report) {
        report.page.set_title(__("Top Selling Items Which Are Out of Stock"));
    },

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "item_code") {
            value = `<a href="/app/item/${encodeURIComponent(data.item_code)}" target="_blank">${value}</a>`;
        }
        return value;
    }
};
