import frappe
from frappe.utils import fmt_money, get_last_day, getdate, nowdate

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Customer Code", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 150},
        {"label": "Invoice Month", "fieldname": "invoice_month", "fieldtype": "Data", "width": 150},
        {"label": "Overdue Outstanding (₹)", "fieldname": "overdue_amount_html", "fieldtype": "HTML", "width": 180},
    ]


def get_data(filters):
    customer_group = filters.get("Customer_group")
    company = filters.get("company")
    invoice_month = filters.get("invoice_month")

    # Determine the selected month (or current month if not selected)
    selected_date = getdate(invoice_month) if invoice_month else getdate(nowdate())
    to_date = get_last_day(selected_date)
    currency = frappe.defaults.get_global_default("currency") or "INR"

    # SQL Query with Invoice Month column
    query = """
        SELECT 
            si.customer AS customer,
            c.customer_name AS customer_name,
            c.customer_group AS customer_group,
            DATE_FORMAT(si.posting_date, '%%M %%Y') AS invoice_month,
            SUM(si.outstanding_amount) AS overdue_amount
        FROM 
            `tabSales Invoice` si
        JOIN 
            `tabCustomer` c ON c.name = si.customer
        WHERE 
            si.docstatus = 1
            AND si.outstanding_amount > 0
            AND si.due_date IS NOT NULL
            AND si.due_date <= %s
            AND si.due_date < CURDATE()
    """

    args = [to_date]

    if customer_group:
        query += " AND c.customer_group = %s"
        args.append(customer_group)
    if company:
        query += " AND si.company = %s"
        args.append(company)

    query += """
        GROUP BY 
            si.customer, c.customer_name, c.customer_group, DATE_FORMAT(si.posting_date, '%%M %%Y')
        ORDER BY 
            overdue_amount DESC, c.customer_name ASC
    """

    results = frappe.db.sql(query, tuple(args), as_dict=True)

    data = []

    # Create clickable links including month filter in the URL
    for row in results:
        month_str = selected_date.strftime("%Y-%m-%d")  # Pass selected filter month
        url = (
            f"/app/sales-invoice?"
            f"customer={row.customer}"
            f"&to_due_date={to_date}"
            f"&status=Overdue"
            f"&invoice_month={month_str}"
        )

        clickable_amount = (
            f"<a href='{url}' target='_blank' "
            f"style='color:blue;text-decoration:underline;'>"
            f"{fmt_money(row.overdue_amount, currency=currency)}</a>"
        )

        data.append({
            "customer": row.customer,
            "customer_name": row.customer_name,
            "customer_group": row.customer_group,
            "invoice_month": row.invoice_month,
            "overdue_amount_html": clickable_amount
        })

    return data
