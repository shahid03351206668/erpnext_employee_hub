// Copyright (c) 2024, CodesSoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Location', {
    get_employees: function (frm) {
        let filters = {
            "employee": frm.doc.employee || null,
            "branch": frm.doc.branch || null,
            "designation": frm.doc.designation || null,
            "department": frm.doc.department || null
        };

        frappe.call({
            method: 'erpnext_employee_hub.erpnext_employee_hub.doctype.attendance_location.attendance_location.get_employee_data',
            freeze: true,
            args: { "filters": filters },
            callback: function (response) {
                if (response?.message) {
                    for (const row of response.message) {
                        // console.log(frm.doc?.item?.find(i => i.employee == row.employee))
                        if (!frm.doc?.item?.find(i => i.employee == row.employee)) {
                            cur_frm.add_child("item", row);
                        }
                    }
                    frm.refresh_field("item");
                }
            }
        });

    }
});
