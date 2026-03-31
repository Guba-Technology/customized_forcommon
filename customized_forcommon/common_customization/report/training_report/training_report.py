# Copyright (c) 2026, Guba Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    filters = frappe._dict(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {
            "label": _("Training Plan"),
            "fieldtype": "Link",
            "fieldname": "training_plan",
            "options": "Training Plan",
            "width": 180,
        },
        {"label": _("Plan Status"), "fieldtype": "Data", "fieldname": "plan_status", "width": 100},
        {"label": _("Training Cost"), "fieldtype": "Currency", "fieldname": "training_cost", "width": 120},
        {
            "label": _("Training Program"),
            "fieldtype": "Link",
            "fieldname": "training_program",
            "options": "Training Program",
            "width": 180,
        },
        {
            "label": _("Training Event"),
            "fieldtype": "Link",
            "fieldname": "training_event",
            "options": "Training Event",
            "width": 180,
        },
        {"label": _("Event Status"), "fieldtype": "Data", "fieldname": "event_status", "width": 100},
        {"label": _("Start Time"), "fieldtype": "Datetime", "fieldname": "start_time", "width": 140},
        {"label": _("End Time"), "fieldtype": "Datetime", "fieldname": "end_time", "width": 140},
        {
            "label": _("Employee"),
            "fieldtype": "Link",
            "fieldname": "employee",
            "options": "Employee",
            "width": 150,
        },
        {"label": _("Employee Name"), "fieldtype": "Data", "fieldname": "employee_name", "width": 150},
        {"label": _("Department"), "fieldtype": "Link", "fieldname": "department", "options": "Department", "width": 140},
        {"label": _("Attendance"), "fieldtype": "Data", "fieldname": "attendance", "width": 100},
        {"label": _("Trainee Status"), "fieldtype": "Data", "fieldname": "trainee_status", "width": 100},
        {"label": _("Hours"), "fieldtype": "Float", "fieldname": "hours", "width": 80},
        {"label": _("Grade"), "fieldtype": "Data", "fieldname": "grade", "width": 80},
        {"label": _("Comments"), "fieldtype": "Data", "fieldname": "comments", "width": 200},
        {
            "label": _("Evaluation"),
            "fieldtype": "Link",
            "fieldname": "evaluation",
            "options": "Training Evaluation",
            "width": 150,
        },
    ]

def get_data(filters):
    data = []
    
    plans = get_training_plans(filters)
    if not plans:
        return []

    plan_names = [p.name for p in plans]
    prog_plan_map, prog_list = get_training_programs(plan_names, filters)
    event_prog_map, event_list = get_training_events(prog_list, filters)
    
    emp_event_map = get_event_employees(event_list, filters)
    eval_event_map = get_training_evaluations(event_list)
    result_emp_map = get_training_results()
    plan_dept_map = get_plan_departments(plan_names)

    for plan in plans:
        if filters.get("training_plan") and plan.name != filters.get("training_plan"):
            continue

        plan_added = False
        plan_row = {
            "training_plan": plan.name,
            "plan_status": plan.status,
            "training_cost": plan.training_cost,
            "department": ", ".join(plan_dept_map.get(plan.name, []))
        }

        if plan.name in prog_plan_map:
            for prog in prog_plan_map[plan.name]:
                if filters.get("training_program") and prog.name != filters.get("training_program"):
                    continue

                if not plan_added:
                    data.append(plan_row)
                    plan_added = True

                prog_added = False
                prog_row = {
                    "indent": 1,
                    "training_program": prog.name,
                }

                if prog.name in event_prog_map:
                    for ev in event_prog_map[prog.name]:
                        if filters.get("training_event") and ev.name != filters.get("training_event"):
                            continue

                        valid_employees = emp_event_map.get(ev.name, [])
                        if filters.get("employee"):
                            valid_employees = [emp for emp in valid_employees if emp.employee == filters.get("employee")]
                            if not valid_employees:
                                continue

                        if not prog_added:
                            data.append(prog_row)
                            prog_added = True

                        evaluation = eval_event_map.get(ev.name)

                        ev_row = {
                            "indent": 2,
                            "training_event": ev.name,
                            "event_status": ev.event_status,
                            "start_time": ev.start_time,
                            "end_time": ev.end_time,
                            "evaluation": evaluation.name if evaluation else None
                        }
                        data.append(ev_row)

                        for emp in valid_employees:
                            emp_result = result_emp_map.get(emp.employee, {})
                            
                            emp_row = {
                                "indent": 3,
                                "employee": emp.employee,
                                "employee_name": emp.employee_name,
                                "department": emp.department,
                                "trainee_status": emp.status,
                                "attendance": emp.attendance,
                                "hours": emp_result.get("hours", 0),
                                "grade": emp_result.get("grade", ""),
                                "comments": emp_result.get("comments", "")
                            }
                            data.append(emp_row)

        if not plan_added and not filters.get("training_program") and not filters.get("training_event") and not filters.get("employee"):
            data.append(plan_row)

    return data

def get_training_plans(filters):
    plan_filters = {}
    
    return frappe.get_all(
        "Training Plan",
        filters=plan_filters,
        fields=["name", "status", "training_cost", "trainer"]
    )

def get_plan_departments(plan_list):
    dept_map = {}
    if not plan_list:
        return dept_map

    depts = frappe.get_all(
        "Department for Training Plan",
        filters={"parent": ("in", plan_list)},
        fields=["parent", "department"]
    )
    for d in depts:
        dept_map.setdefault(d.parent, []).append(d.department)
        
    return dept_map

def get_training_programs(plan_list, filters):
    prog_plan_map = {}
    prog_list = []

    programs = frappe.get_all(
        "Training Program",
        filters={"custom_training_plan": ("in", plan_list)},
        fields=["name", "custom_training_plan", "trainer_name", "status"]
    )

    for prog in programs:
        prog_plan_map.setdefault(prog.custom_training_plan, []).append(prog)
        prog_list.append(prog.name)

    return prog_plan_map, prog_list

def get_training_events(prog_list, filters):
    event_prog_map = {}
    event_list = []
    
    event_filters = {"training_program": ("in", prog_list)}
    if filters.get("company"):
        event_filters["company"] = filters.get("company")

    events = frappe.get_all(
        "Training Event",
        filters=event_filters,
        fields=["name", "training_program", "event_status", "start_time", "end_time"]
    )

    for ev in events:
        event_prog_map.setdefault(ev.training_program, []).append(ev)
        event_list.append(ev.name)

    return event_prog_map, event_list

def get_event_employees(event_list, filters):
    emp_event_map = {}
    if not event_list:
        return emp_event_map

    try:
        employees = frappe.get_all(
            "Training Event Employee",
            filters={"parent": ("in", event_list)},
            fields=["parent", "employee", "employee_name", "department", "status", "attendance", "is_mandatory"]
        )
        for emp in employees:
            emp_event_map.setdefault(emp.parent, []).append(emp)
    except Exception:
        pass 

    return emp_event_map

def get_training_evaluations(event_list):
    eval_event_map = {}
    if not event_list:
        return eval_event_map

    evals = frappe.get_all(
        "Training Evaluation",
        filters={"training_event": ("in", event_list)},
        fields=["name", "training_event"]
    )

    for e in evals:
        eval_event_map[e.training_event] = e

    return eval_event_map

def get_training_results():
    result_map = {}
    try:
        results = frappe.get_all(
            "Training Result Employee",
            fields=["employee", "hours", "grade", "comments", "parent"]
        )
        for r in results:
            result_map[r.employee] = r
    except Exception:
        pass
        
    return result_map