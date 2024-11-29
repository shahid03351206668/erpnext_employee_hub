import frappe
from .main import get_user_details
import json


@frappe.whitelist()
def get_user_todo():
    user = get_user_details()
    user_email = user.get("email")
    todos = []
    if user_email:
        todos = frappe.db.sql(
            f"""SELECT status, description, name, priority FROM `tabToDo`
        WHERE owner = '{user_email}' """,
            as_dict=True,
        )
    frappe.response["data"] = todos


@frappe.whitelist(allow_guest=True)
def create_todo():
    data = frappe.request.data
    try:
        data = json.loads(data)
    except Exception:
        data = data

    if data:
        todo_doc = frappe.new_doc("ToDo")
        todo_doc.status = data.get("status")
        todo_doc.description = data.get("description")
        todo_doc.priority = data.get("priority")

        todo_doc.flags.ignore_permissions = True
        todo_doc.save()
        frappe.db.commit()

        if todo_doc.name:
            frappe.response["message"] = "Todo created successfully!"
            return

    frappe.response["message"] = "Something went wrong"


@frappe.whitelist(allow_guest=True)
def update_todo():
    data: dict = frappe.request.data
    try:
        data = json.loads(data)
    except Exception:
        data = data

    if data:
        todo_doc = frappe.get_doc("ToDo", data.get("name"))
        if todo_doc:
            if data.get("status"):
                todo_doc.status = data.get("status")
            if data.get("description"):
                todo_doc.description = data.get("description")
            if data.get("priority"):
                todo_doc.priority = data.get("priority")

            todo_doc.flags.ignore_permissions = True
            todo_doc.save()
            frappe.db.commit()

        if todo_doc.name:
            frappe.response["message"] = "Todo update successfully!"
            return

    frappe.response["message"] = "Something went wrong"
