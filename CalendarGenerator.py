from datetime import timedelta

from icalendar import Calendar, Event


class CalendarGenerator:
    def create_calendar(self, lista_uscite):
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        for uscita in lista_uscite:
            dtstart = uscita.data
            dtend = uscita.data + timedelta(days=1)
            event = Event()
            event.add('summary', uscita.title)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            # print(event)
            cal.add_component(event)
        return cal

    def exportCalendar(self, cal):
        pass
