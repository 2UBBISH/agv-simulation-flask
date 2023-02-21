import sys
import re
from datetime import datetime, date, timedelta
import time
from operator import itemgetter
from itertools import groupby

# def emptyStr(value):
#     if value is None:
#         return ""
#     else:
#         return str(value)
#
# def handleEmptyStr(value):
#     if value is None:
#         return None
#     elif value == "":
#         return None
#     else:
#         return value
#
# def getBirthyear(birthday):
#     if birthday is None or len(birthday) == 0:
#         return
#
#     year = datetime.strptime("%s 00:00:00" % (birthday), "%Y-%m-%d %H:%M:%S").year
#     return year
#
# def getYesterDayStr():
#     return (datetime.now() - timedelta(days=1)).strftime("%F")
#
def getTodayStr():
    return datetime.now().strftime("%F")

# def getDayBegin(day_or_time):
#     if day_or_time is None:
#         return
#     if type(day_or_time) == str and len(day_or_time) > 10:
#         day_or_time = day_or_time[0:10]
#     elif type(day_or_time) == datetime or type(day_or_time) == date:
#         day_or_time = day_or_time.strftime("%F") #年月日
#     return "%s 00:00:00" % (day_or_time)
#
# def getNextDayBegin(day_or_time):
#     if day_or_time is None or len(day_or_time) == 0:
#         return
#     _theDayBegin = getDayBegin(day_or_time)
#     _nextDayBegin = datetime.strptime(_theDayBegin, '%Y-%m-%d %H:%M:%S') + timedelta(days = 1)
#     return _nextDayBegin.strftime('%Y-%m-%d %H:%M:%S')
#
#
def getDateTime(day_or_time):
    if day_or_time is None or len(day_or_time) == 0:
        return

    if type(day_or_time) == datetime:
        return day_or_time
    elif type(day_or_time) == str:
        if len(day_or_time) > 10:
            return datetime.strptime(day_or_time, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.strptime(day_or_time + " 00:00:00", '%Y-%m-%d %H:%M:%S')

def getDateTimeStr(day_or_time):
    if day_or_time is None:
        return
    return getDateTime(day_or_time).strftime("%Y-%m-%d %H:%M:%S")

# def getNextDayDateTime(day_or_time):
#     if day_or_time is None:
#         return
#     return getDateTime(day_or_time) + timedelta(days=1)
#
#
# def getNextDayDateTimeStr(day_or_time):
#     if day_or_time is None:
#         return
#     return getNextDayDateTime(day_or_time).strftime("%Y-%m-%d %H:%M:%S")
#
# def timeStampToDateTime(timeStamp):
#     if timeStamp is None:
#         return
#     dateArray = datetime.fromtimestamp(timeStamp)
#     dateTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
#     return dateTime
#
# def dateTimeTotimeStamp(dateTime):
#     if dateTime is None:
#         return
#     if ':' in dateTime:
#         timeArray = time.strptime(dateTime, "%Y-%m-%d %H:%M:%S")
#     else:
#         timeArray = time.strptime(dateTime, "%Y-%m-%d %H-%M-%S")
#
#     timeStamp = int(time.mktime(timeArray))
#     return timeStamp
#
# def getClientIp(forwardedFor, realIp):
#     ip = None
#     if forwardedFor is not None:
#         for i in forwardedFor.split(','):
#             if i is not None:
#                 ip = i.strip()
#                 break
#     elif realIp is not None:
#         ip = realIp.strip()
#     ipCompile = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
#     if ipCompile.match(str(ip)):
#         return ip
#     return None
#
#
# def getJsonNode(map_dict, key_path, separator = ".", default_value=None):
#     if key_path is None or map_dict is None or not isinstance(map_dict, dict):
#         return default_value
#
#     keyArr = key_path.split(separator)
#     while(len(keyArr) > 0 and keyArr[0] is not None and map_dict is not None and isinstance(map_dict, dict)):
#         map_dict = map_dict.get(keyArr[0], None)
#         keyArr = keyArr[1:]
#
#     return map_dict
#
#
# def _cal_today_0_timeStamp():
#     timeStamp = int(time.time())
#     # print (timeStamp);
#     timeArray = time.localtime(timeStamp)
#     print(timeArray);
#
#     # 获取当天0点时间
#     tss2 = str(timeArray.tm_year) + '-' + str(timeArray.tm_mon) + '-' + str(timeArray.tm_mday) + " 00:00:00";
#     print(tss2);
#     timeArray0 = time.strptime(tss2, "%Y-%m-%d %H:%M:%S")
#     print(timeArray0);
#     timeStamp = int(time.mktime(timeArray0))
#     return timeStamp;
#
# def getNextMonth(year, month):
#     month = int(month)
#     year = int(year)
#     if(month == 12):
#         return (year+ 1, 1)
#     return (year, month + 1)
#
# def groupBy(lst, key):
#     lstg = groupby(lst, itemgetter(key))
#     result = dict()
#     for key, group in lstg:
#         result[key] = group
#     return result
#
# def groupByAndSum(lst, key, sumField):
#     lstg = groupby(lst, itemgetter(key))
#     result = dict()
#     for key, group in lstg:
#         sum = 0
#         for g in group:  # group是一个迭代器，包含了所有的分组列表
#             sum += g[sumField]
#         result[key] = sum
#     return result
#
# def sortBy(lst, key=None, reverse=False):
#     return sorted(lst, key=key, reverse=reverse)
#
# def dictToList(srcDict):
#     lst = []
#
#     list_values = [i for i in srcDict.values()]
#     list_keys = [i for i in srcDict.keys()]
#     for i in range(len(list_keys)):
#         lst.append({
#             "name": list_keys[i],
#             "value": list_values[i],
#         })
#     return lst
#     # aggrDict["provinces_grouped_sorted"] = util.sortBy(lst, key=takeSecond, reverse=True)[0:10]

if __name__ == "__main__":
    pass
