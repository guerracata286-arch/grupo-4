from django.core.management.base import BaseCommand
from datetime import datetime, time
import holidays
from booking.models import Blackout

class Command(BaseCommand):
    help = "Carga feriados de Chile como blackouts globales para un año"

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, required=True)

    def handle(self, *args, **opts):
        year = opts["year"]
        cl_holidays = holidays.country_holidays("CL", years=[year])
        created = 0
        for day, name in cl_holidays.items():
            start_dt = datetime.combine(day, time(0,0))
            end_dt = datetime.combine(day, time(23,59))
            obj, was_created = Blackout.objects.get_or_create(
                room=None,
                start_datetime=start_dt,
                end_datetime=end_dt,
                defaults={"reason": f"Feriado: {name}"}
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Blackouts creados: {created}"))
