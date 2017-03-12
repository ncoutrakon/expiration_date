import calendar as cal
import pandas as pd

# DO NOT CHANGE COLUMN NAMES OR FORMAT WHEN UPDATING RAW FILES FOR NEW YEAR
rules = pd.read_csv("/users/ncoutrakon/PycharmProjects/expiration/rules.csv")
contracts = pd.read_csv("/users/ncoutrakon/PycharmProjects/expiration/contracts.csv")
holidays = pd.read_csv("/users/ncoutrakon/PycharmProjects/expiration/holidays.csv")
holidays["Holidays"] = pd.to_datetime(holidays["Holidays"], infer_datetime_format= True)

# reference dictionaries to convert between weekday/month names and numbers
month_dict = {v: k for k, v in enumerate(cal.month_abbr)}
weekday_dict = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3,
                "Fri": 4, "Sat": 5, "Sun": 6}

# sets defaults that are changed dynamically throughout the script
exp_month = 1
exp_yr = 17

# ONE PECULIARITY NEED TO MANUALLY CHANGE ASSET_ID = 39, EXP = FEBYY after
# after output is ran
###############################################################################
# get HOLIDAYS, CALENDAR, and BUSINESS DAYS
#
# filters holidays by asset_id, month and year
# returns numeric array of holiday dates for given month
def get_holidays(asset_id, year, month):
    asset_holiday = holidays["Holidays"][ (holidays['Asset ID'] == asset_id)
                & (holidays["Holidays"].dt.month == month)
                & (holidays["Holidays"].dt.year == year)
    ]

    return asset_holiday.dt.day.tolist()


# parses exp = ("MmmYY") and retrieves appropriate expiration month calendar
# returns calendar less weekends
def get_exp_cal(exp, months_before=0):
    global exp_month
    global exp_yr
    exp_month = month_dict[exp[:3]]
    exp_yr = int("20" + exp[3:5])

    if months_before == 1 and exp_month == 1:
        exp_month = 12
        exp_yr = int("20" + exp[3:5]) - 1
    elif months_before == 2 and exp_month == 1:
        exp_month = 11
        exp_yr = int("20" + exp[3:5]) - 1
    elif months_before == 2 and exp_month == 2:
        exp_month = 12
        exp_yr = int("20" + exp[3:5]) - 1
    else:
        exp_month = month_dict[exp[:3]] - months_before

    exp_cal = cal.monthcalendar(exp_yr, exp_month)
    week_cal = [day[0:5] for day in exp_cal]
    return week_cal


# flattens calendar into numeric array and returns final expiration date
def biz_days_before(exp_cal, days_before, num_day, succeed=False):
    exp_list = [day for week in exp_cal for day in week]
    if num_day == "last": num_day = exp_list[-1]
    num_day = int(num_day)
    if num_day in exp_list:
        idx = next(i for i, v in enumerate(exp_list)
                   if v == num_day) - days_before
    else:
        idx = next(i for i, v in enumerate(exp_list)
                   if v > num_day) - 1 - days_before + succeed
    return exp_list[idx]
###############################################################################


###############################################################################
# RELATIVE n FIXED n BUSINESS
#
# gets expiration date for relative expiry, i.e. 3rd Friday
def relative_exp_day(asset_id, exp, days_before, num_day, day,
                     months_before, succeed):
    num_day = int(num_day)
    exp_cal = get_exp_cal(exp, months_before)
    exp_yr = int("20" + exp[3:5])
    exp_month = month_dict[exp[:3]]
    day = weekday_dict[day]
    if exp_cal[0][day] == 0:
        num_day = exp_cal[num_day][day]
    else:
        num_day = exp_cal[num_day - 1][day]
    exp_holidays = get_holidays(asset_id, exp_yr, exp_month)
    for w in exp_cal:
        for h in exp_holidays:
            if h in w: w.remove(h)
    exp_date = biz_days_before(exp_cal, days_before, num_day, succeed)

    return exp_date


# n days before given date
# is_last_day overrides given date with last date in month
def fixed_exp_day(asset_id, exp, days_before, num_day, months_before, succeed):
    exp_cal = get_exp_cal(exp, months_before)
    while exp_cal[len(exp_cal) - 1][-1] == 0:
        exp_cal[len(exp_cal) - 1].pop()

    exp_holidays = get_holidays(asset_id, exp_yr, exp_month)
    for w in exp_cal:
        for h in exp_holidays:
            if h in w: w.remove(h)

    exp_date = biz_days_before(exp_cal, days_before,
                               num_day, succeed)

    return exp_date


# nth business day of month
def biz_exp_day(asset_id, exp, days_before, num_day, months_before):
    num_day = int(num_day)
    exp_cal = get_exp_cal(exp, months_before)
    exp_yr = int("20" + exp[3:5])
    exp_month = month_dict[exp[:3]]
    exp_holidays = get_holidays(asset_id, exp_yr, exp_month)
    for w in exp_cal:
        for h in exp_holidays:
            if h in w: w.remove(h)
    exp_list = [day for week in exp_cal for day in week]
    while 0 in exp_list: exp_list.remove(0)
    exp_date = exp_list[num_day - days_before - 1]

    return exp_date
###############################################################################


###############################################################################
def get_exp_date(asset_id, exp):
    try:
        asset_config = rules[rules.asset_id == asset_id]

        fn = asset_config.iloc[0]['function']
        days_before = asset_config.iloc[0]['days_before']
        num_day = asset_config.iloc[0]['num_day']
        months_before = asset_config.iloc[0]['months_before']
        day = asset_config.iloc[0]['day']
        succeed = asset_config.iloc[0]['succeed'] == 1

        exp_date = 0

        if fn == "fixed":
            exp_date = fixed_exp_day(asset_id, exp, days_before, num_day,
                                     months_before, succeed)
        elif fn == "relative":
            exp_date = relative_exp_day(asset_id, exp, days_before, num_day,
                                    day, months_before, succeed)
        elif fn == "biz":
            exp_date = biz_exp_day(asset_id, exp, days_before, num_day,
                                   months_before)

        return str(exp_month) + "/" + str(exp_date) + "/" + str(exp_yr)
    except IndexError:
        return "IndexError"


contracts['RealExpDate'] = \
    contracts.apply(lambda x: get_exp_date(x['Asset_id'], x['ExpDateNew']), axis=1)
contracts.to_csv("/users/ncoutrakon/PycharmProjects/expiration/RealExpDates.csv",
              index=False)

