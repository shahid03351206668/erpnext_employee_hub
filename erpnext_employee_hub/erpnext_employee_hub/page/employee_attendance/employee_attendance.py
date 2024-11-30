import json
import frappe
import datetime


# def _get_duration(time2, time1):
#     elapsed_time = time2 - time1
#     total_seconds = int(elapsed_time.total_seconds())
#     hours, remainder = divmod(total_seconds, 3600)
#     minutes, seconds = divmod(remainder, 60)


def get_duration(time1, time2):
    elapsed_time = time2 - time1
    total_seconds = int(elapsed_time.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours} Hrs {minutes} Mins"


@frappe.whitelist()
def get_attendance_data(filters={}):
    query_filters = {}
    if filters:
        try:
            query_filters = json.loads(filters)
        except Exception:
            query_filters = filters

    checkin_conds = ""
    # checkin_fkeys = ["log_type"]
    emp_conds = ""
    if query_filters.get("from_date"):
        checkin_conds += f""" and DATE(time) >= '{query_filters.get("from_date")}' """
    if query_filters.get("to_date"):
        checkin_conds += f""" and DATE(time) <=  '{query_filters.get("to_date")}'  """
    if query_filters.get("log_type"):
        checkin_conds += f""" and log_type =  '{query_filters.get("log_type")}'  """

    # if query_filters.get("employee"):
    #     emp_conds += f""" and e.employee =  '{query_filters.get("employee")}'  """
    # if query_filters.get("branch"):
    #     emp_conds += f""" and e.branch =  '{query_filters.get("branch")}'  """
    # if query_filters.get("designation"):
    #     emp_conds += f""" and e.designation =  '{query_filters.get("designation")}'  """
    # if query_filters.get("department"):
    #     emp_conds += f""" and e.department =  '{query_filters.get("department")}'  """

    employees = frappe.db.sql(
        f""" SELECT e.employee_name, e.name, e.image, e.designation, e.department, e.branch FROM `tabEmployee` e inner join `tabEmployee Checkin` ec on ec.employee = e.name {emp_conds} """,
        as_dict=True,
        debug=True,
    )

    employee_filters = {}
    if query_filters.get("employee"):
        employee_filters.update({"employee": query_filters.get("employee")})

    if query_filters.get("branch"):
        employee_filters.update({"branch": query_filters.get("branch")})

    if query_filters.get("designation"):
        employee_filters.update({"designation": query_filters.get("designation")})

    if query_filters.get("department"):
        employee_filters.update({"department": query_filters.get("department")})

    employees = frappe.get_list(
        "Employee",
        filters=employee_filters,
        fields=[
            "employee_name",
            "name",
            "image",
            "designation",
            "department",
            "branch",
        ],
    )

    checkins_length = [1]
    serialized_checkins = {}
    for i in employees:
        checkins = frappe.db.sql(
            f"""  SELECT  e.custom_location_name as location_name,  e.log_type, e.shift, e.time, e.device_id, e.custom_latitude, e.custom_longitude, e.custom_front_image, e.custom_rear_image FROM `tabEmployee Checkin` e where  e.employee = '{i.get("name")}' {checkin_conds} order by e.time """,
            as_dict=True,
            debug=False,
        )
        if checkins:
            date_wise_checkins = []
            for j in checkins:
                j["checkin_date"] = j.get("time").strftime("%d-%m-%Y")
                j["checkin_time"] = j.get("time").strftime("%I:%M %p")

            checkins_dates = [_.get("checkin_date") for _ in checkins]
            date_wise_checkins = {date: [] for date in checkins_dates}

            for row in checkins:
                date_wise_checkins[row.get("checkin_date")].append(row)

            fdata = []

            for key in date_wise_checkins.keys():
                checkins = date_wise_checkins[key]
                checkins_length.append(len(checkins))
                st = checkins[0].get("time")
                end = checkins[-1].get("time")
                total_worked_secs = 0
                last_check_time = None

                for row in checkins:
                    if last_check_time:
                        elapsed_time = row.get("time") - last_check_time
                        total_worked_secs += int(elapsed_time.total_seconds())

                    last_check_time = row.get("time")

                worked_hours, w_remainder = divmod(total_worked_secs, 3600)
                worked_minutes, w_seconds = divmod(w_remainder, 60)
                fdata.append(
                    {
                        "date": key,
                        "checkins": checkins,
                        "total_duration": get_duration(st, end),
                        "total_work_duration": f"{worked_hours} Hrs {worked_minutes} Mins",
                    }
                )

            obj = {
                "employee_name": i.get("employee_name"),
                "checkins": checkins,
                "image": i.get("image"),
                "designation": i.get("designation"),
                "date_wise_checkins": fdata,
                "department": i.get("department"),
                "branch": i.get("branch"),
            }
            serialized_checkins[i.name] = obj

    frappe.response["max_calls"] = max(checkins_length) + 1
    return serialized_checkins
