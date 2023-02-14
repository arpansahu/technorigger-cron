from locations.models import Locations
from django.core.management.base import BaseCommand
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('----------------------------Started Location Creations--------------------------------')
        df = pd.read_csv('worldcities.csv')
        df = df.filter(items=['city_ascii', 'country', 'iso2', 'iso3', 'admin_name'])
        for index, row in df.iterrows():
            try:
                print(f"--------Location no: {index}-----")
                print(row)
                Locations.objects.create(
                    city=row.values[0],
                    country=row.values[1],
                    country_code_iso2=row.values[2],
                    country_code_iso3=row.values[3],
                    state=row.values[4]
                )
                print("Created New Location Object")
            except Exception as e:
                print(f"Creation of New location Failed: Error is {e}")

        print('----------------------------Ended Location Creations--------------------------------')
