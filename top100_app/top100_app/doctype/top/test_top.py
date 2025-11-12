import frappe

def execute(filters=None):
    data = frappe.get_doc("Top").get_top_50_items()
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item"},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data"},
        {"label": "Total Quantity", "fieldname": "total_qty", "fieldtype": "Float"},
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency"}
    ]
    return columns, data
