from glob import glob
from datetime import datetime, timedelta, timezone, timedelta
from dateutil.rrule import *
from icalendar import Calendar
import os
import csv
import re

jst = timezone(timedelta(hours=9), 'JST')
MAX_REPEAT = 100

# 入力ファイル
ICS_FILE_NAME = '*.ics'

# 出力ファイル
CSV_FILE_NAME = './time.csv'

# カウントする日付 (1/16 ~ 2/15)
from_dt = datetime(year=2023, month=1, day=16, tzinfo=jst)
to_dt = datetime(year=2023, month=2, day=15, tzinfo=jst)

# 以下コード
if os.path.exists(CSV_FILE_NAME):
    os.remove(CSV_FILE_NAME)
folder = glob(ICS_FILE_NAME)
ics_file = open(folder[0], encoding='utf-8')
calendars = Calendar.from_ical(ics_file.read())

exdate = set()
exdate.add(datetime.strptime('19700101T000000', '%Y%m%dT%H%M%S'))

recurrence_dict = dict()
time_dict = dict()
time_list = list()
sum_time = 0
all_cnt = 0
cnt_event = 0

for calendar in calendars.walk('VEVENT'):
    cnt_event += 1
    start_dt = calendar.decoded('DTSTART')
    end_dt = calendar.decoded('DTEND')
    summary = calendar.decoded('SUMMARY').decode('utf-8')
    uid = calendar.decoded('UID').decode('utf-8')

    if not type(start_dt) is datetime:
    # 開始時刻と終了時刻が終日の設定の場合はカウントしない
        continue

    if (start_dt > from_dt) and (end_dt < to_dt):
        time_ = end_dt - start_dt
        str_start_dt = "{0:%Y-%m-%d %H:%M}".format(start_dt)
        str_end_dt = "{0:%Y-%m-%d %H:%M}".format(end_dt)
        str_time = str(time_//3600)
        time_dict[uid + '-R00000'] = [summary, str_start_dt, str_end_dt, str_time]
        sum_time += time_.seconds
        all_cnt += 1

    if ('RECURRENCE-ID' in calendar) and (start_dt > from_dt) and (end_dt < to_dt):
        dt = datetime.strptime(calendar['RECURRENCE-ID'].to_ical().decode('utf-8'), '%Y%m%dT%H%M%S')
        recurrence_dict[uid + '-REMOVE'] = dt
        
    if 'RRULE' not in calendar:
        continue

    freq_day = 0
    if calendar['RRULE']['FREQ'][0] == 'DAILY':
        freq_day = 1
    if calendar['RRULE']['FREQ'][0] == 'WEEKLY':
        freq_day = 7

    freq_end_dt = calendar['RRULE']['UNTIL'][0]
    repeat_cnt = 1

    if 'EXDATE' in calendar:
        if type(calendar.decoded('EXDATE')) is list: 
            for exdate_tmp in calendar.decoded('EXDATE'):
                str_exdate = exdate_tmp.to_ical().decode('utf-8')
                exdate.add(datetime.strptime(str_exdate, '%Y%m%dT%H%M%S'))
        else:
            str_exdate = calendar.decoded('EXDATE').to_ical().decode('utf-8')
            exdate.add(datetime.strptime(str_exdate, '%Y%m%dT%H%M%S'))

    while True:
        time_ = end_dt - start_dt
        start_dt = start_dt + timedelta(days=freq_day)
        end_dt = end_dt + timedelta(days=freq_day)
        str_start_dt = "{0:%Y-%m-%d %H:%M}".format(start_dt)
        str_end_dt = "{0:%Y-%m-%d %H:%M}".format(end_dt)
        str_time = str(time_//3600)

        if (start_dt > from_dt) and (end_dt < to_dt) and (start_dt not in exdate):
            time_dict[uid + '-R' + str(repeat_cnt).zfill(5)] = [summary, str_start_dt, str_end_dt, str_time]
            sum_time += time_.seconds
            all_cnt += 1
            repeat_cnt += 1

        if to_dt > freq_end_dt:
            tmp_dt = freq_end_dt
        else:
            tmp_dt = to_dt

        if end_dt > tmp_dt:
            break

for r_key in recurrence_dict.keys():
    for i in range(MAX_REPEAT):
        if r_key[:-7] + '-R' + str(i).zfill(5) in time_dict:
            x = time_dict.pop(r_key[:-7] + '-R' + str(i).zfill(5))
            print(r_key[:-7] + '-R' + str(i).zfill(5))


for v in time_dict.values():
    print(v)
    time_list.append(v)
time_list.sort()
csv_file = open(CSV_FILE_NAME, mode='x')
writer = csv.writer(csv_file, lineterminator='\n')
writer.writerows(time_list)

print(f'{len(time_dict)} days, SUM, {sum_time // 3600}', file=csv_file)
print(len(time_dict))

csv_file.close()
ics_file.close()
print('Done')


