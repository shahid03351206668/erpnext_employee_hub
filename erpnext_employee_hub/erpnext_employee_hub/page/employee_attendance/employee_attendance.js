
function get_data(filters = {}) {
	frappe.call({
		method: 'erpnext_employee_hub.erpnext_employee_hub.page.employee_attendance.employee_attendance.get_attendance_data',
		args: { filters: filters },
		freeze: true,
		callback: (r) => {
			const { message: data } = r;
			console.log(data);
			if (filters?.with_images == "Yes") {
				generate_employee_wise_table_rows(data, cint(r.max_calls), true);
			}
			else {
				generate_employee_wise_table_rows(data, cint(r.max_calls));
			}
		},
		error: (r) => { }
	})
}

// function view_image(url, title) {
// 	// url ? frappe.msgprint(`<img src="${url} " style="max-width: 300px;width: 100%;height: 100%;margin-inline: auto;display: block;object-fit: contain;">`, "Image") : null;
// 	// const title = url.includes("custom_front_image") ? "Front Image" : "Rear Image";
// 	url ? frappe.msgprint(`<img src="${url} " style="max-width: 300px;width: 100%;height: 100%;margin-inline: auto;display: block;object-fit: contain;">`, title) : null;
// }

function view_image(element) {


	frappe.msgprint(`
<div style="display:flex;max-height:500px; gap:.5rem;">
	<div style="flex-basis:100%;">
		<img src="${element.getAttribute("data-front-image")}" style=" width: 100%;height: inherit;margin-inline:
			auto;display: block;object-fit: contain;">
	</div>
	<div style="flex-basis:100%;">
		<img src="${element.getAttribute("data-back-image")}" style=" width: 100%;height: inherit;margin-inline:
			auto;display: block;object-fit: contain;">
	</div>
</div>
	`,)
}

function view_location(element) {
	const obj = JSON.parse(element.getAttribute("data-checkin"));
	frappe.msgprint(`<div style="width: 100%"><iframe width="100%" height="600" frameborder="0" scrolling="no" marginheight="0"
        marginwidth="0"
        src="https://maps.google.com/maps?width=100%25&amp;height=600&amp;hl=en&amp;q=${obj.custom_latitude}, ${obj.custom_longitude}&amp;t=&amp;z=14&amp;ie=UTF8&amp;iwloc=B&amp;output=embed"><a
            href="https://www.gps.ie/">gps trackers</a></iframe></div>`, "Location");
}

let api_filters = { with_images: "Yes" };

frappe.pages['employee-attendance'].on_page_load = function (wrapper) {
	const page_filters = [
		{
			label: 'Employee',
			fieldtype: 'Link',
			fieldname: 'employee',
			options: "Employee",
		}, {
			label: 'Branch',
			fieldtype: 'Link',
			fieldname: 'branch',
			options: "Branch",
		},
		{
			label: 'Designation',
			fieldtype: 'Link',
			fieldname: 'designation',
			options: "Designation",
		},
		{
			label: 'Department',
			fieldtype: 'Link',
			fieldname: 'department',
			options: "Department",
		},
		{
			label: 'Log Type',
			fieldtype: 'Select',
			fieldname: 'log_type',
			options: ["", "IN", "OUT"],
		},
		{
			label: 'From Date',
			fieldtype: 'Date',
			fieldname: 'from_date',
			default: frappe.datetime.month_start()
		},
		{
			label: 'To Date',
			fieldtype: 'Date',
			fieldname: 'to_date',
			default: frappe.datetime.get_today()
		},
		{
			label: 'With Images',
			fieldtype: 'Select',
			fieldname: 'with_images',
			options: ["Yes", "No"],
			default: "Yes",
			change() {
				console.log(this)
				api_filters[this.df.fieldname] = this?.get_value();
				get_data(api_filters);

			}
			// default: frappe.datetime.get_today()
		},
	];

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Employee Attendance',
		single_column: true
	});

	let $btn = page.set_secondary_action('Refresh', () => get_data(api_filters));
	for (const field of page_filters) {
		if (!field.change) {
			page.add_field({
				...field,
				change() {
					api_filters[this.df.fieldname] = this?.get_value();
					get_data(api_filters);
				}
			});

		}
		else { page.add_field(field) }
	}

	$(wrapper).find(".row.layout-main").append(`<div id="db-content"></div>`);
	get_data(api_filters);
}

function generate_employee_wise_table_rows(data, max_calls, show_images = false) {
	const keys = Object.keys(data);
	let html = `<div class="table-overflow__wrapper table"><table > <tr style="border-bottom: 2px solid lightgray; "><th style="font-weight:600;border: none; background-color: #0a6bc1;  color:white;">Employee</th
	>
	<th  style="background-color: #0a6bc1; " colspan="${max_calls}"></th></tr>`;

	for (const key of keys) {
		const { employee_name, checkins, date_wise_checkins, image, designation, date, department, branch } = data[key];
		// let tdHTML = `<td style="vertical-align: middle;background: #edf0ff;">
		// 	<div class="checkin-employeeCard">
		// 		<img src="${image || 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'}">
		// 		<div >
		// 			<div style="font-weight:700; text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;; ">${employee_name}</div>
		// 			<div style="font-size:.8rem text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;;">${designation}</div>
		// 		</div>
		// 	</div>
		// </td>`;

		let count = 0
		let checkinsRows = "";

		for (const row of date_wise_checkins) {
			let checkinsTd = `<td style="vertical-align: middle;background: #edf0ff;border-bottom: 2px solid lightgrey;">
			<div class="checkin-employeeCard">
				<img src="${image || 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'}">
				<div >
				<div style="font-weight:700; text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;; ">${employee_name}</div>
				
				<div style="font-size:.75rem; text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;;">${row.date}</div>
				<div style="font-size:.75rem; text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;;">${designation}</div>
				<div style="font-size:.75rem; text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;;">${department}</div>
				<div style="font-size:.75rem; text-overflow:ellipsis; width:160px; overflow:hidden;white-space:nowrap;;">${branch}</div>
				</div>
			</div>
		</td>`;

			const { checkins } = row;
			for (const i of checkins) {
				checkinsTd += `<td>${generate_checkin_card(i, show_images)}</td>`;
			}

			checkinsTd += `<td>			
				<div>
					<div style="font-weight:700;border-bottom: 2px solid lightgrey;text-align:center;">Total Durations</div>

				<div style="white-space:nowrap; margin-top:1rem;"><strong>Worked Duration:</strong> ${row.total_work_duration}</div>
					<div><strong>Total Duration:</strong> ${row.total_duration}</div>
				</div>
			</td>`;

			checkinsRows += `<tr style="border-bottom: 2px solid #0a6bc1;">${checkinsTd}</tr>`;
			count++;
		}

		html += checkinsRows;
	}

	html += '</table></div>'
	$("#db-content").html(html);
}


function generate_checkin_card(i, showImages = true) {
	let imageshtml = "";
	if (showImages) {
		imageshtml = `<div class="log-card__images"> ${i.custom_front_image ? `<div >
			Front Image
			<img onclick="view_image('${i.custom_front_image}', 'Front Image')" src="${i.custom_front_image}">
			</div>` : ""}
		${i.custom_rear_image ? `<div> 
			Rear Image
			<img onclick="view_image('${i.custom_rear_image}', 'Rear Image')"
		src="${i.custom_rear_image}"> </div>` : ""}</div>`
	}

	return `
	<div class="checkin-logCard-wrapper">
		
		<div class="checkin-logCard">
			<div class="checkin-logCard__upper">
				<div class="checkin-logCard__title">CHECK ${i.log_type}</div>
				<div style="display:flex;    gap: .5rem;">
					<div class="checkin-logCard__time"><b>Date</b>: ${i.checkin_date}</div>
					<div class="checkin-logCard__time"><b>Time</b>: ${i.checkin_time}</div>
				</div>

				<div class="checkin-logCard__shift"><b>Shift</b>: ${i.shift}</div>
				<div><b>Location Name</b>: ${i.location_name || ""}</div>
				<div style="overflow: hidden;white-space: nowrap;text-overflow: ellipsis;"><b>Location</b>: ${i.device_id}</div>
				${i.duration ? `<div><b>Duration:</b> ${i.duration}</div>` : ""}
			</div>
			<div style="display:flex;    gap: .5rem; ">
				<button style="flex-basis:100%;margin: 0 !important;padding: .2rem;font-size: .75rem;"  class="btn btn-primary btn-sm w-100 mt-4 ${!i.custom_rear_image && !i.custom_front_image ? "hide" : ""}" onclick='view_image(this)'
					data-checkin='${JSON.stringify(i)}'
					data-front-image="${i.custom_front_image}"
					data-back-image="${i.custom_rear_image}"
					>View Images</button>
				<button style="flex-basis:100%;margin: 0 !important;padding: .2rem;font-size: .75rem;"  class="btn btn-primary btn-sm w-100 mt-4" onclick='view_location(this)'
				
					data-checkin='${JSON.stringify(i)}'>View Location</button>
			</div>
		</div>

		<div>
		${imageshtml}
		</div>
	</div>
	
	`

}

// function generate_checkin_card(i) {
// 	return `<div class="checkin-logCard">
// 		<div class="checkin-logCard__upper">
// 			<div class="checkin-logCard__title">CHECK ${i.log_type}</div>
// 			<div class="checkin-logCard__time"><b>Date</b>: ${i.checkin_date}</div>
// 			<div class="checkin-logCard__time"><b>Time</b>: ${i.checkin_time}</div>
// 			<div class="checkin-logCard__shift"><b>Shift</b>: ${i.shift}</div>
// 			<div style="max-height: 40px;overflow: hidden;"><b>Location / Device ID</b>: ${i.device_id}</div>
// 			${i.duration ? `<div><b>Duration:</b> ${i.duration}</div>` : ""}
// 		</div>

// 		<div class="checkin-logCard__images">
// 			${i.custom_front_image ? `<div><img onclick="view_image('${i.custom_front_image}', 'Front Image')"
// 					src="${i.custom_front_image}"></div>` : ""}
// 			${i.custom_rear_image ? `<div><img onclick="view_image('${i.custom_rear_image}', 'Rear Image' )" src="${i.custom_rear_image}">
// 			</div>` : ""}
// 		</div>
// 		<div>
// 			<button class="btn btn-primary btn-sm w-100 mt-4" onclick='view_location(this)'
// 				data-checkin='${JSON.stringify(i)}'>View Location</button>
// 		</div>
// 	</div>`

// }