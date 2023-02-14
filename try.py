import gspread

ca = gspread.service_account(filename='service_account.json')
sh = ca.open('JobPortal_locations')
ws = sh.worksheet(title='JobPortal_public_locations_locations')

for location in ws.get_all_records():
    print(location)