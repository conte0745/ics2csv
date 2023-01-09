from glob import glob
from datetime import datetime, timedelta, timezone
from icalendar import Calendar
import os
import csv

jst = timezone(timedelta(hours=9), 'JST')

ICS_FILE_NAME = '*.ics'
CSV_FILE_NAME = './time.csv'
from_dt = datetime(year=2022, month=12, day=15, tzinfo=jst)
to_dt = datetime(year=2023, month=1, day=16, tzinfo=jst)

if os.path.exists(CSV_FILE_NAME):
    os.remove(CSV_FILE_NAME)
folder = glob(ICS_FILE_NAME)
ics_file = open(folder[0], encoding='utf-8')
calendars = Calendar.from_ical(ics_file.read())

time_list = list()
sum_time = 0
cnt = 0
for calendar in calendars.walk():
    if calendar.name == 'VEVENT':
        start_dt = calendar.decoded('DTSTART')
        end_dt = calendar.decoded('DTEND')
        summary = calendar.decoded('SUMMARY').decode('utf-8')

        if not type(start_dt) is datetime:
            continue

        if (start_dt > from_dt) and (end_dt < to_dt):
            time_ = end_dt - start_dt
            str_start_dt = "{0:%Y-%m-%d %H:%M}".format(start_dt)
            str_end_dt = "{0:%Y-%m-%d %H:%M}".format(end_dt)
            str_time = str(time_//3600)
            time_list.append([summary, str_start_dt, str_end_dt, str_time])
            sum_time += time_.seconds
            cnt += 1

time_list.sort()
csv_file = open(CSV_FILE_NAME, mode='x')
writer = csv.writer(csv_file, lineterminator='\n')
writer.writerows(time_list)
print(f'{cnt} days, SUM, {sum_time // 3600}', file=csv_file)

csv_file.close()
ics_file.close()
print('Done')


