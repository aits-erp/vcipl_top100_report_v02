# Copyright (c) 2025, Sai Mmore
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    conditions = "WHERE si.docstatus = 1"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    elif filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
    elif filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"

    query = f"""
        SELECT
            sii.item_code AS "Item Code:Link/Item:150",
            i.item_name AS "Item Name::200",
            SUM(sii.qty) AS "Total Sold Qty:Float:120",
            SUM(sii.base_net_amount) AS "Total Sales Amount:Currency:150",
            COALESCE(SUM(b.actual_qty), 0) AS "Current Stock:Float:120"
        FROM
            `tabSales Invoice Item` sii
        INNER JOIN
            `tabSales Invoice` si ON si.name = sii.parent
        LEFT JOIN
            `tabItem` i ON i.name = sii.item_code
        LEFT JOIN
            `tabBin` b ON b.item_code = sii.item_code
        {conditions}
        GROUP BY
            sii.item_code, i.item_name
        HAVING
            COALESCE(SUM(b.actual_qty), 0) <= 0
        ORDER BY
            SUM(sii.base_net_amount) DESC
        LIMIT 50
    """

    data = frappe.db.sql(query, filters, as_list=True)

    columns = [
        "Item Code:Link/Item:150",
        "Item Name:Data:200",
        "Total Sold Qty:Float:120",
        "Total Sales Amount:Currency:150",
        "Current Stock:Float:120"
    ]

    return columns, data
