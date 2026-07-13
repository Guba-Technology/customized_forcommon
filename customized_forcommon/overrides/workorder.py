import json
import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate, date_diff, get_link_to_form
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder, get_serial_nos_for_job_card,create_job_card, validate_operation_data,split_qty_based_on_batch_size 

@frappe.whitelist()
def make_job_card(work_order, operations):
	if isinstance(operations, str):
		operations = json.loads(operations)

	work_order = frappe.get_doc("Work Order", work_order)
	for row in operations:
		row = frappe._dict(row)
		validate_operation_data(row)
		qty = row.get("qty")
		while qty > 0:
			qty = split_qty_based_on_batch_size(work_order, row, qty)
			if row.job_card_qty > 0:
				create_job_card(work_order, row, auto_create=True)


@frappe.whitelist()
def close_work_order(work_order, status):
	if not frappe.has_permission("Work Order", "write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	work_order = frappe.get_doc("Work Order", work_order)
	if work_order.get("operations"):
		job_cards = frappe.get_list(
			"Job Card",
			filters={"work_order": work_order.name, "status": "Work In Progress", "docstatus": 1},
			pluck="name",
		)

		if job_cards:
			job_cards = ", ".join(job_cards)
			frappe.throw(
				_("Can not close Work Order. Since {0} Job Cards are in Work In Progress state.").format(
					job_cards
				)
			)

	work_order.update_status(status)
	work_order.update_planned_qty()
	frappe.msgprint(_("Work Order has been {0}").format(status))
	work_order.notify_update()
	return work_order.status


class CustomWorkOrder(WorkOrder):
    def create_job_card(self, *args, **kwargs):
        """
        Polymorphic Entry Point.
        - When called with no arguments (core framework standard), it runs the operations loop.
        - When called with keywords (row=row), it processes individual machine initialization.
        """
        # --- PATH A: Inner Job Card Engine Execution (Triggered via prepare_data_for_job_card) ---
        if kwargs.get("row") or (args and isinstance(args[0], object)):
            row = kwargs.get("row") or args[0]
            enable_capacity_planning = kwargs.get("enable_capacity_planning", False)
            auto_create = kwargs.get("auto_create", False)
            
            parallel_workstations = []
            if row.get("operation"):
                parallel_workstations = frappe.get_all(
                    "Workstation Detail", 
                    filters={"parent": row.operation, "parenttype": "Operation"},
                    fields=["workstation"]
                )
                
            n = len(parallel_workstations)

            if n <= 1:
                target_workstation = parallel_workstations[0].workstation if n == 1 else row.get("workstation")
                base_qty = row.get("job_card_qty") or row.get("qty") or self.qty
                machines_to_process = [{"workstation": target_workstation, "target_qty": flt(base_qty)}]
            else:
                base_qty = row.get("job_card_qty") or row.get("qty") or self.qty
                total_qty = flt(base_qty)
                distributed_qty = flt(total_qty / n)
                machines_to_process = [{"workstation": d.workstation, "target_qty": distributed_qty} for d in parallel_workstations]

            last_doc = None

            for machine in machines_to_process:
                current_workstation = machine["workstation"]
                current_qty = machine["target_qty"]
                
                hourly_rate = flt(frappe.db.get_value("Workstation", current_workstation, "hour_rate"))

                doc = frappe.new_doc("Job Card")
                doc.update(
                    {
                        "work_order": self.name,
                        "workstation_type": row.get("workstation_type"),
                        "operation": row.get("operation"),
                        "workstation": current_workstation,
                        "posting_date": nowdate(),
                        "for_quantity": current_qty,
                        "operation_id": row.get("name"),
                        "bom_no": row.get("bom") or self.bom_no,
                        "project": self.project,
                        "company": self.company,
                        "sequence_id": row.get("sequence_id"),
                        "wip_warehouse": self.wip_warehouse or row.get("wip_warehouse")
                        if not self.skip_transfer or self.from_wip_warehouse
                        else self.source_warehouse or row.get("source_warehouse"),
                        "hour_rate": hourly_rate,
                        "serial_no": row.get("serial_no"),
                    }
                )

                if self.transfer_material_against == "Job Card" and not self.skip_transfer:
                    doc.get_required_items()

                if auto_create:
                    doc.flags.ignore_mandatory = True
                    if enable_capacity_planning:
                        doc.schedule_time_logs(row)

                    doc.insert()
                    frappe.msgprint(_("Job card {0} created for workstation {1}").format(get_link_to_form("Job Card", doc.name), current_workstation), alert=True)

                if enable_capacity_planning:
                    doc.db_set("status", "Open")
                    
                last_doc = doc

            return last_doc

        # --- PATH B: Standard Core Trigger Loop ---
        manufacturing_settings_doc = frappe.get_doc("Manufacturing Settings")
        enable_capacity_planning = not cint(manufacturing_settings_doc.disable_capacity_planning)
        plan_days = cint(manufacturing_settings_doc.capacity_planning_for_days) or 30

        for idx, row in enumerate(self.operations):
            qty = self.qty
            
            parallel_workstations = []
            if row.get("operation"):
                parallel_workstations = frappe.get_all(
                    "Workstation Detail", 
                    filters={"parent": row.operation, "parenttype": "Operation"},
                    fields=["workstation"]
                )
            
            n = len(parallel_workstations)
            if n > 1:
                self.prepare_data_for_job_card(row, idx, plan_days, enable_capacity_planning, total_machines=n)
            else:
                while qty > 0:
                    qty = self.split_qty_based_on_batch_size(row, qty)
                    if row.get("job_card_qty", 0) > 0:
                        self.prepare_data_for_job_card(row, idx, plan_days, enable_capacity_planning, total_machines=1)

        planned_end_date = self.operations and self.operations[-1].planned_end_time
        if planned_end_date:
            self.db_set("planned_end_date", planned_end_date)

    def prepare_data_for_job_card(self, row, idx, plan_days, enable_capacity_planning, total_machines=1):
        original_time = flt(row.time_in_mins)
        if total_machines > 1:
            row.time_in_mins = flt(original_time / total_machines)

        self.set_operation_start_end_time(row, idx)

        # Triggers our polymorphic route internally without method definition conflicts
        job_card_doc = self.create_job_card(row=row, enable_capacity_planning=enable_capacity_planning, auto_create=True)

        if enable_capacity_planning and job_card_doc:
            row.planned_start_time = job_card_doc.scheduled_time_logs[-1].from_time
            row.planned_end_time = job_card_doc.scheduled_time_logs[-1].to_time

            if date_diff(row.planned_end_time, self.planned_start_date) > plan_days:
                frappe.message_log.pop()
                frappe.throw(
                    _(
                        "Unable to find the time slot in the next {0} days for the operation {1}. Please increase the 'Capacity Planning For (Days)' in the {2}."
                    ).format(
                        plan_days,
                        row.operation,
                        get_link_to_form("Manufacturing Settings", "Manufacturing Settings"),
                    ),
                    frappe.CapacityError,
                )

            row.db_update()   
        
        row.time_in_mins = original_time

    def split_qty_based_on_batch_size(self, row, qty):
        if not cint(frappe.db.get_value("Operation", row.operation, "create_job_card_based_on_batch_size")):
            row.batch_size = row.get("qty") or self.qty
            
        parallel_workstations = []
        if row.get("operation"):
            parallel_workstations = frappe.get_all(
                "Workstation Detail", 
                filters={"parent": row.operation, "parenttype": "Operation"},
                fields=["workstation"]
            )
        
        n = len(parallel_workstations)
        
        if n > 1:
            distributed_batch_size = flt(row.batch_size / n)
            row.job_card_qty = distributed_batch_size
            if qty >= distributed_batch_size:
                qty -= distributed_batch_size
            elif qty > 0:
                row.job_card_qty = qty
                qty = 0
        else:
            row.job_card_qty = row.batch_size
            if qty >= row.batch_size:
                qty -= row.batch_size
            elif qty > 0:
                row.job_card_qty = qty
                qty = 0

        get_serial_nos_for_job_card(row, self)
        return qty
    
    def calculate_time(self):
        for d in self.get("operations"):
            parallel_workstations = []
            if d.get("operation"):
                parallel_workstations = frappe.get_all(
                    "Workstation Detail", 
                    filters={"parent": d.operation, "parenttype": "Operation"},
                    fields=["workstation"]
                )
            
            n = len(parallel_workstations)

            if not d.fixed_time:
                base_time = flt(d.time_in_mins) * (flt(self.qty) / flt(d.batch_size or 1))
                if n > 1:
                    d.time_in_mins = flt(base_time / n)
                else:
                    d.time_in_mins = base_time

        self.calculate_operating_cost()

    def calculate_operating_cost(self):
        self.planned_operating_cost, self.actual_operating_cost = 0.0, 0.0
        
        for d in self.get("operations"):
            parallel_workstations = []
            if d.get("operation"):
                parallel_workstations = frappe.get_all(
                    "Workstation Detail", 
                    filters={"parent": d.operation, "parenttype": "Operation"},
                    fields=["workstation"]
                )
            
            n = len(parallel_workstations)
            
            if n > 1:
                total_parallel_planned_cost = 0.0
                for machine in parallel_workstations:
                    machine_hour_rate = flt(frappe.db.get_value("Workstation", machine.workstation, "hour_rate"))
                    total_parallel_planned_cost += flt(machine_hour_rate * (flt(d.time_in_mins) / 60.0))
                
                d.planned_operating_cost = flt(total_parallel_planned_cost, d.precision("planned_operating_cost"))
            else:
                d.planned_operating_cost = flt(
                    flt(d.hour_rate) * (flt(d.time_in_mins) / 60.0), d.precision("planned_operating_cost")
                )

            if not d.actual_operating_cost and flt(d.actual_operation_time) > 0:
                if n > 1:
                    job_cards = frappe.get_all(
                        "Job Card",
                        filters={"work_order": self.name, "operation_id": d.name, "docstatus": 1},
                        fields=["total_time_in_mins", "workstation"]
                    )
                    total_actual_cost = 0.0
                    for jc in job_cards:
                        jc_rate = flt(frappe.db.get_value("Workstation", jc.workstation, "hour_rate"))
                        total_actual_cost += flt((flt(jc.total_time_in_mins) / 60.0) * jc_rate)
                    d.actual_operating_cost = flt(total_actual_cost, d.precision("actual_operating_cost"))
                else:
                    d.actual_operating_cost = flt(
                        flt(d.hour_rate) * (flt(d.actual_operation_time) / 60.0), d.precision("actual_operating_cost")
                    )
            else:
                d.actual_operating_cost = flt(d.actual_operating_cost, d.precision("actual_operating_cost"))

            self.planned_operating_cost += flt(d.planned_operating_cost)
            self.actual_operating_cost += flt(d.actual_operating_cost)

        variable_cost = (
            self.actual_operating_cost if self.actual_operating_cost else self.planned_operating_cost
        )

        self.total_operating_cost = (
            flt(self.additional_operating_cost) + flt(variable_cost) + flt(self.corrective_operation_cost)
        )