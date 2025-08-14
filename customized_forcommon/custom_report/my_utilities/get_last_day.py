import calendar
from datetime import datetime

class GetLastDay:
    def __init__(self, month_input=None, year=None):
        self.month_input = month_input or datetime.today().month
        self.year = year or datetime.today().year

    def get_last_day(self):
        """Returns the last day of the given month and year."""
        if isinstance(self.month_input, str):
            try:
                month = datetime.strptime(self.month_input, "%B").month  # Full name
            except ValueError:
                try:
                    month = datetime.strptime(self.month_input, "%b").month  # Short name
                except ValueError:
                    month = int(self.month_input)  # Assume numeric string
        else:
            month = int(self.month_input)

        last_day = calendar.monthrange(self.year, month)[1]
        return last_day
