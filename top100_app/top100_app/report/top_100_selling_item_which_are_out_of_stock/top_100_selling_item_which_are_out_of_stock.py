# Copyright (c) 2025, Sai More
# For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Total Sold Quantity", "fieldname": "total_qty", "fieldtype": "Float", "width": 150},
        {"label": "Total Sales Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Current Stock", "fieldname": "current_stock", "fieldtype": "Float", "width": 120},
        {"label": "Safety Stock", "fieldname": "safety_stock", "fieldtype": "Float", "width": 120},
        {"label": "Shortage Qty", "fieldname": "shortage_qty", "fieldtype": "Float", "width": 130}
    ]


def get_data(filters):
    conditions = ["si.docstatus = 1"]
    params = {}

    # Optional filters
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("si.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params.update({
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        })
    elif filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        params["from_date"] = filters.get("from_date")
    elif filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        params["to_date"] = filters.get("to_date")

    where_clause = "WHERE " + " AND ".join(conditions)

    # 🧮 Apply limit based on user filter (default to 50)
    limit = int(filters.get("limit") or 50)

    # Main query
    query = f"""
        SELECT
            sii.item_code AS item_code,
            i.item_name AS item_name,
            SUM(sii.qty) AS total_qty,
            SUM(sii.base_net_amount) AS total_amount,
            COALESCE(SUM(b.actual_qty), 0) AS current_stock,
            COALESCE(i.safety_stock, 0) AS safety_stock,
            (COALESCE(i.safety_stock, 0) - COALESCE(SUM(b.actual_qty), 0)) AS shortage_qty
        FROM
            `tabSales Invoice Item` sii
        INNER JOIN
            `tabSales Invoice` si ON si.name = sii.parent
        LEFT JOIN
            `tabItem` i ON i.name = sii.item_code
        LEFT JOIN
            `tabBin` b ON b.item_code = sii.item_code
        {where_clause}
        GROUP BY
            sii.item_code, i.item_name, i.safety_stock
        HAVING
            current_stock < safety_stock
        ORDER BY
            shortage_qty DESC
        LIMIT {limit}
    """

    return frappe.db.sql(query, params, as_dict=True)
