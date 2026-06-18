import frappe
from frappe.utils import today, add_days, getdate
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def get_today_leave_employees():
    leave_applications = frappe.get_all('Leave Application',
                                        filters={'from_date': ['<=', today()],
                                                 'to_date': ['>=', today()],
                                                 'status': ['not in', ('Cancelled', 'Rejected')],
                                                 'department': ['!=', 'Engineering - MISL']},
                                        fields=['employee', 'preferred_name', 'leave_type'])

    engineering_employees = frappe.get_all('Employee',
                                          fields=['name', 'preferred_name'])

    engineering_employee_ids = [emp['name'] for emp in engineering_employees]

    today_leave_employees = [la for la in leave_applications if la['employee'] in engineering_employee_ids]

    return today_leave_employees

@frappe.whitelist(allow_guest=True)
def get_next_30_days_leave_employees():
    start_date = add_days(today(), 1)
    end_date = add_days(today(), 30)

    leave_applications = frappe.get_all('Leave Application',
                                        filters={'from_date': ['<=', end_date],
                                                 'to_date': ['>=', start_date],
                                                 'status': ['not in', ('Cancelled', 'Rejected')],
                                                 'department': ['!=', 'Engineering - MISL']},
                                        fields=['employee', 'preferred_name', 'from_date', 'to_date', 'leave_type'])

    engineering_employees = frappe.get_all('Employee',
                                          fields=['name', 'preferred_name'])

    engineering_employee_ids = [emp['name'] for emp in engineering_employees]

    next_30_days_leave_employees = [la for la in leave_applications if la['employee'] in engineering_employee_ids]

    return next_30_days_leave_employees

@frappe.whitelist(allow_guest=True)
def get_next_60_days_company_holidays():
    start_date = today()
    end_date = add_days(today(), 60)

    holidays = frappe.get_all('Holiday List', filters={'is_default': 1}, fields=['name'])
    holiday_list = holidays[0].get('name') if holidays else None

    if holiday_list:
        company_holidays = frappe.get_all('Holiday', filters={'parent': holiday_list,
                                                              'holiday_date': ['between', [start_date, end_date]],
                                                              'weekly_off': ['=', 0]},
                                          fields=['holiday_date', 'description', 'weekly_off'],
                                          order_by='holiday_date')

        return company_holidays

    return []

@frappe.whitelist(allow_guest=True)
def get_today_birthdays():
    current_date = getdate(today())
    employees = frappe.get_all('Employee',
                              filters={'department': ['!=', 'Engineering - MISL'], 'status': 'Active'},
                              fields=['name', 'preferred_name', 'date_of_birth'])

    today_birthdays = []
    for emp in employees:
        if emp.date_of_birth:
            dob = getdate(emp.date_of_birth)
            if dob.month == current_date.month and dob.day == current_date.day:
                today_birthdays.append({
                    'preferred_name': emp.preferred_name
                })

    return today_birthdays

@frappe.whitelist(allow_guest=True)
def get_upcoming_birthdays():
    start_date = add_days(today(), 1)
    end_date = add_days(today(), 30)
    current_year = getdate(today()).year

    employees = frappe.get_all('Employee',
                              filters={'department': ['!=', 'Engineering - MISL'], 'status': 'Active'},
                              fields=['name', 'preferred_name', 'date_of_birth'])

    upcoming_birthdays = []
    for emp in employees:
        if emp.date_of_birth:
            dob = getdate(emp.date_of_birth)
            next_birthday = dob.replace(year=current_year)
            if next_birthday <= getdate(today()):
                next_birthday = next_birthday.replace(year=current_year + 1)
            if getdate(start_date) <= next_birthday <= getdate(end_date):
                upcoming_birthdays.append({
                    'preferred_name': emp.preferred_name,
                    'date_of_birth': next_birthday.strftime('%Y-%m-%d')
                })

    upcoming_birthdays.sort(key=lambda x: getdate(x['date_of_birth']))
    return upcoming_birthdays

@frappe.whitelist(allow_guest=True)
def get_today_anniversaries():
    current_date = getdate(today())
    employees = frappe.get_all('Employee',
                              filters={'department': ['!=', 'Engineering - MISL'], 'status': 'Active'},
                              fields=['name', 'preferred_name', 'date_of_joining'])

    today_anniversaries = []
    for emp in employees:
        if emp.date_of_joining:
            doj = getdate(emp.date_of_joining)
            if doj.month == current_date.month and doj.day == current_date.day:
                years_of_service = current_date.year - doj.year
                today_anniversaries.append({
                    'preferred_name': emp.preferred_name,
                    'years_of_service': years_of_service
                })

    return today_anniversaries

@frappe.whitelist(allow_guest=True)
def get_upcoming_anniversaries():
    start_date = add_days(today(), 1)
    end_date = add_days(today(), 30)
    current_year = getdate(today()).year

    employees = frappe.get_all('Employee',
                              filters={'department': ['!=', 'Engineering - MISL'], 'status': 'Active'},
                              fields=['name', 'preferred_name', 'date_of_joining'])

    upcoming_anniversaries = []
    for emp in employees:
        if emp.date_of_joining:
            doj = getdate(emp.date_of_joining)
            next_anniversary = doj.replace(year=current_year)
            if next_anniversary <= getdate(today()):
                next_anniversary = next_anniversary.replace(year=current_year + 1)
            if getdate(start_date) <= next_anniversary <= getdate(end_date):
                years_of_service = current_year - doj.year if next_anniversary >= getdate(start_date) else (current_year + 1) - doj.year
                upcoming_anniversaries.append({
                    'preferred_name': emp.preferred_name,
                    'date_of_joining': next_anniversary.strftime('%Y-%m-%d'),
                    'years_of_service': years_of_service
                })

    upcoming_anniversaries.sort(key=lambda x: getdate(x['date_of_joining']))
    return upcoming_anniversaries

@frappe.whitelist(allow_guest=True)
def get_present_employee_count():
    # Get total active employees excluding Engineering - MISL
    total_employees = frappe.get_all('Employee',
                                     filters={'department': ['!=', 'Engineering - MISL'], 'status': 'Active'},
                                     fields=['name'])
    total_count = len(total_employees)

    # Get employees on leave today
    leave_applications = frappe.get_all('Leave Application',
                                        filters={'from_date': ['<=', today()],
                                                 'to_date': ['>=', today()],
                                                 'status': ['not in', ('Cancelled', 'Rejected')],
                                                 'department': ['!=', 'Engineering - MISL']},
                                        fields=['employee'])

    employee_ids_on_leave = [la['employee'] for la in leave_applications]
    leave_count = len(set(employee_ids_on_leave))  # Use set to avoid duplicates

    # Calculate present employees
    present_count = total_count - leave_count

    # Calculate percentage
    percentage = (present_count / total_count * 100) if total_count > 0 else 0
    percentage = round(percentage, 1)  # Round to 1 decimal place

    return {
        'present_count': present_count,
        'total_count': total_count,
        'percentage': percentage
    }

def get_context(context):
    context.today = today()
    context.today_leave_employees = get_today_leave_employees()
    context.next_30_days_leave_employees = get_next_30_days_leave_employees()
    context.next_60_days_company_holidays = get_next_60_days_company_holidays()
    context.today_birthdays = get_today_birthdays()
    context.upcoming_birthdays = get_upcoming_birthdays()
    context.today_anniversaries = get_today_anniversaries()
    context.upcoming_anniversaries = get_upcoming_anniversaries()
    present_data = get_present_employee_count()
    context.present_employee_count = present_data['present_count']
    context.total_employee_count = present_data['total_count']
    context.present_employee_percentage = present_data['percentage']