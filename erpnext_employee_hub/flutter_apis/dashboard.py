import frappe
import calendar
from calendar import monthrange

from datetime import datetime
from frappe.utils import cstr, cint, flt, getdate
from .main import (
    create_log,
    make_response,
    get_user_details,
    get_date_time_to_use,
)
from .leave_application_custom import get_leave_details
from json import loads


def get_attendance_data(employee, st_date, ed_date):
    sql_conditions = (
        f""" AND attendance_date >= '{st_date}' and  attendance_date <= '{ed_date}' """
    )
    attendances = frappe.db.sql(
        f""" 
        SELECT 
            employee,
            in_time,
            out_time,
            status
        FROM `tabAttendance`
        WHERE employee = '{employee}' {sql_conditions}
        AND docstatus = 1
        GROUP BY attendance_date, employee
        ORDER BY attendance_date DESC

    """,
        as_dict=True,
    )

    presents = len([i for i in attendances if i.get("status") == "Present"])

    response = {
        "Absent": len([i for i in attendances if i.get("status") == "Absent"]),
        "Present": presents,
        "Total": monthrange(
            cint(datetime.now().strftime("%Y")),
            cint(datetime.now().strftime("%m")),
        )[1],
    }

    return response


@frappe.whitelist(allow_guest=True)
def get_dashboard_data():
    try:
        user_details = get_user_details()
        if user_details:
            leaves = {}
            leave_allocation = {}
            leave_data = get_leave_details(user_details.employee, str(getdate()))
            # leave_data = {}

            if leave_data:
                leave_allocation = leave_data.get("leave_allocation", {})
                for leave_type, leave_type_data in leave_allocation.items():
                    if leave_type not in leaves:
                        leaves[leave_type] = {
                            "total_leaves": 0,
                            "leaves_used": 0,
                        }
                    if leave_type_data:
                        leaves[leave_type]["total_leaves"] += leave_type_data.get(
                            "total_leaves"
                        )
                        leaves[leave_type]["leaves_used"] += leave_type_data.get(
                            "leaves_taken"
                        )
            dt = get_date_time_to_use()
            month = dt.month

            data_get_dict = {
                # "current_task": f""" SELECT creation, priority, name as id, actual_time, expected_time, exp_end_date from `tabTask` where  1 = 1  ORDER BY creation desc""",
                "pending_request": f"""SELECT ec.name as id, ec.status,expense_date, ecd.description, ecd.expense_type,ecd.amount from `tabExpense Claim` ec inner join `tabExpense Claim Detail` ecd on ec.name = ecd.parent where ec.docstatus=1 and MONTH(ec.posting_date) = {month}  and employee = '{user_details.employee}' """,
                "salary_details": f"""SELECT MONTHNAME(posting_date) as month_name,total_working_days,gross_pay from `tabSalary Slip` where 1 = 1 and MONTH(posting_date) = {month}  and employee = '{user_details.employee}' """,
            }

            for field, query in data_get_dict.items():
                data = frappe.db.sql(query, as_dict=1, debug=True)
                data_get_dict[field] = data

            data_get_dict["current_task"] = frappe.db.get_list(
                "Task",
                fields=[
                    "name",
                    "status",
                    "priority",
                    "subject",
                    "project",
                    "exp_start_date",
                    "exp_end_date",
                    "expected_time",
                    "progress",
                    "issue",
                    "type",
                    "completed_by",
                    "completed_on",
                    "description",
                    "_assign",
                ],
                order_by="creation desc",
                page_length=1,
                limit=1,
            )

            data_get_dict_counts = {
                "attendance_present": f"""SELECT COUNT(name)from `tabAttendance` where status = 'Present' and MONTH(attendance_date) = {month} """,
                "attendance_absent": f"""SELECT COUNT(name) from `tabAttendance` where status = 'Absent' and MONTH(attendance_date) = {month} """,
            }
            for field, query in data_get_dict_counts.items():
                data = frappe.db.sql(query)
                if data:
                    data_get_dict[field] = data[0][0]

            data_get_dict["leave_balance"] = [
                {
                    "leave_type": k,
                    "total_leaves": v.get("total_leaves"),
                    "leaves_used": v.get("leaves_used"),
                }
                for k, v in leaves.items()
            ]

            # count_data = (
            #     frappe.db.sql(
            #         f""" SELECT status, COUNT(name) as data_count FROM `tabAttendance` WHERE employee = '{user_details.get("employee")}'
            #         AND MONTHNAME(attendance_date) = '{datetime.now().strftime("%B")}'
            # 	GROUP BY status
            # 	""",
            #         as_dict=1,
            #     )
            #     or []
            # )

            graph_data = {
                "Work From Home": 0,
                "Half Day": 0,
                "On Leave": 0,
                "Absent": 0,
                "monthname": datetime.now().strftime("%B"),
                "no_of_days": monthrange(
                    cint(datetime.now().strftime("%Y")),
                    cint(datetime.now().strftime("%m")),
                )[1],
            }

            current_shift = frappe.db.sql(
                f"""  SELECT start_time, end_time,name  FROM `tabShift Type` where name = '{frappe.db.get_value("Employee", user_details.get("employee"), "default_shift")}' """,
                as_dict=True,
            )

            last_employee_checkin = frappe.db.sql(
                f""" SELECT time, log_type FROM `tabEmployee Checkin` WHERE employee = '{user_details.get("employee")}'
                    ORDER BY time DESC LIMIT 1
                 """,
                as_dict=True,
            )
            if last_employee_checkin:
                data_get_dict["recent_checkin"] = last_employee_checkin[0]

            if current_shift:
                data_get_dict["current_shift"] = current_shift[0]

            # for abc in count_data:
            #     graph_data[abc.status] = flt(abc.data_count)
            graph_data.update(
                get_attendance_data(
                    user_details.get("employee"),
                    frappe.utils.get_first_day(frappe.utils.getdate()),
                    frappe.utils.get_last_day(frappe.utils.getdate()),
                )
            )
            data_get_dict["attendence_graph_data"] = graph_data
            make_response(success=True, data=data_get_dict)
        else:
            make_response(success=False, message="Invalid User!")
    except Exception as e:
        make_response(success=False, message=str(e))
