import frappe
# from frappe.desk.doctype.notification_log.notification_log import (
# 	set_notifications_as_unseen,
# 	send_notification_email
# )
from frappe.desk.doctype.notification_log.notification_log import NotificationLog
# from frappe.desk.doctype.notification_settings.notification_settings import (
# 	is_email_notifications_enabled_for_type, 
# )
def after_insert(self):
	pass
	# frappe.publish_realtime("notification", after_commit=True, user=self.for_user)
	# set_notifications_as_unseen(self.for_user)
	# if is_email_notifications_enabled_for_type(self.for_user, self.type):
		# try:
		# 	send_notification_email(self)
		# except frappe.OutgoingEmailError:
		# 	self.log_error(_("Failed to send notification email"))
  
NotificationLog.after_insert = after_insert