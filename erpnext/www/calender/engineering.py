import frappe
from frappe.utils import today, add_days

@frappe.whitelist(allow_guest=True)
def get_today_leave_employees():
    leave_applications = frappe.get_all('Leave Application',
                                        filters={'from_date': ['<=', today()],
                                                 'to_date': ['>=', today()],
                                                 'status' : ['not in', ('Cancelled', 'Rejected')],
                                                 'department': ['=', 'Engineering - MISL'],
                                                 },
                                        fields=['employee', 'preferred_name'])

    engineering_employees = frappe.get_all('Employee',
                                        #    filters={'department': 'Engineering - MISL'},
                                           fields=['name', 'preferred_name'])

    engineering_employee_ids = [emp['name'] for emp in engineering_employees]

    today_leave_employees = [la for la in leave_applications if la['employee'] in engineering_employee_ids]

    return today_leave_employees

@frappe.whitelist(allow_guest=True)
def get_next_30_days_leave_employees():
    start_date = add_days(today(), 1)
    end_date = add_days(today(), 365)

    leave_applications = frappe.get_all('Leave Application',
                                        filters={'from_date': ['<=', end_date],
                                                 'to_date': ['>=', start_date],
                                                 'status' : ['not in', ('Cancelled', 'Rejected')],
                                                 'department': ['=', 'Engineering - MISL']
                                                 },
                                        fields=['employee', 'preferred_name', 'from_date', 'to_date'])

    engineering_employees = frappe.get_all('Employee',
                                        #    filters={'department': 'Engineering - MISL'},
                                           fields=['name', 'preferred_name'])

    engineering_employee_ids = [emp['name'] for emp in engineering_employees]

    next_30_days_leave_employees = [la for la in leave_applications if la['employee'] in engineering_employee_ids]

    return next_30_days_leave_employees

@frappe.whitelist(allow_guest=True)
def get_next_60_days_company_holidays():
    start_date = today()
    end_date = add_days(today(), 365)

    holidays = frappe.get_all('Holiday List', filters={'is_default': 1}, fields=['name'])
    holiday_list = holidays[0].get('name') if holidays else None

    if holiday_list:
        company_holidays = frappe.get_all('Holiday', filters={'parent': holiday_list,
                                                              'holiday_date': ['between', [start_date, end_date]],
															  'weekly_off': ['=', 0	]},
                                          fields=['holiday_date', 'description', 'weekly_off'],
                                          order_by='holiday_date')

        return company_holidays

    return []

def get_context(context):
    context.today = today()
    context.today_leave_employees = get_today_leave_employees()
    context.next_30_days_leave_employees = get_next_30_days_leave_employees()
    context.next_60_days_company_holidays = get_next_60_days_company_holidays()
