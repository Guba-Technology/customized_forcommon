import frappe
from erpnext.setup.doctype.employee.employee import Employee
from frappe.utils import add_years, getdate, nowdate

class CustomEmployee(Employee):
    def validate(self):
        super().validate()
        # frappe.msgprint("CustomEmployee.validate triggered for CTC setting")
        self.set_ctc_from_grade()
<<<<<<< HEAD
=======
        self.set_retirement_age_based_on_salutation_and_employee_group()
>>>>>>> db946fbe976e32f1896014bfd7a0de9e1e4f68f4
        self.validate_18_years_old()

    def set_ctc_from_grade(self):
        """Set CTC from Employee Grade if available."""
        # Check if the grade is set and fetch the CTC from Employee Grade
        if self.grade:
            frappe.msgprint(f"Grade selected: {self.grade}")
            try:
                # Fetch the Employee Grade document
                grade_doc = frappe.get_doc("Employee Grade", self.grade)
                # Check if the custom default salary is set and assign it to CTC
                if grade_doc.custom_default_salary:
                    self.ctc = grade_doc.custom_default_salary
                    frappe.msgprint(f"CTC set to {self.ctc} from Grade {self.grade}")
            except Exception as e:
                frappe.msgprint(f"Error fetching grade: {e}")
<<<<<<< HEAD
    
=======
    
    def set_retirement_age_based_on_salutation_and_employee_group(self):

        salutation_ranks = {
            "ፊልድ ማርሻል": 1,
            "ጀነራል": 2,
            "ሌተናል ጀነራል": 3,
            "ሜጀር ጀነራል": 4,
            "ብርጋዴር ጀነራል": 5,
            "ኮሎኔል": 6,
            "ሌተናል ኮሎኔል": 7,
            "ሻለቃ": 8,
            "ሻምበል": 9,
            "መቶ አለቃ": 10,
            "ምክትል መቶ አለቃ": 11,
            "ችፍ ዋራንት ኦፊሰር": 12,
            "ማስተር ዋራንት ኦፊሰር": 13,
            "ሲኔር ዋራንት ኦፊሰር": 14,
            "ጁኔር ዋራንት ኦፊሰር": 15,
            "ሻለቃ ባሻ	ማስተር ቴክኒሻን": 16,
            "ሻለቃ መጋቢ ባሻ": 17,
            "ሊዲንግ ቴክኒሻን": 17,
            "ሻምበል ባሻ": 18,
            "ሲኔር ቴክኒሻን": 18,
            "መጋቢ ሃምሳ አለቃ": 19,
            "ጁኔር ቴክኒሻን": 19,
            "ሃምሳ አለቃ": 20,
            "ሊ/ኤክ/ማን": 20,
            "አስር አለቃ": 21,
            "ሲ/ኤክ/ማን": 21,
            "ምክትል አስር አለቃ": 22,
            "ጁ/ኤክ/ማን": 22,
            "መስመራዊ ወታደር": 23
        }
        if self.date_of_birth and self.salutation and self.employee_group:
            if self.employee_group == "Military":
                if self.salutation in salutation_ranks:
                    if salutation_ranks[self.salutation] > 8:
                        retirement_age = 48
                        self.date_of_retirement = add_years(self.date_of_birth, retirement_age)
                    elif salutation_ranks[self.salutation] <= 8:
                        retirement_age = 52
                        self.date_of_retirement = add_years(self.date_of_birth, retirement_age)
                else:
                    frappe.msgprint(f"Salutation '{self.salutation}' not recognized for retirement age calculation.")
            elif self.employee_group == "Civil":
                retirement_age = 60
                self.date_of_retirement = add_years(self.date_of_birth, retirement_age)
            else:
                frappe.msgprint(f"Employee group '{self.employee_group}' not recognized for retirement age calculation.")

    def validate_18_years_old(self):
        """Validate if the employee is at least 18 years old."""
        if self.date_of_birth:
            todate = getdate(nowdate())
            dob = getdate(self.date_of_birth if self.date_of_birth else nowdate()) #
            age = (todate - dob).days // 365  # Calculate age in years
            if age < 18:
                frappe.throw(
                    frappe._("Employee must be at least 18 years old. Current age: {} years").format(age),
                )
>>>>>>> db946fbe976e32f1896014bfd7a0de9e1e4f68f4
