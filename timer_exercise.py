from datetime import datetime, timedelta

class Timer:
    def __init__(self):
            # 给定的时间段
        self.given_time_ranges = {
            0 :[("10:00", "12:00")],#周一
            1 :[("10:00", "12:00")],#周二
            2 :[("10:00", "12:00")],#周三
            3 :[("10:00", "12:00")],#周四
            4 :[("10:00", "12:00")],#周五
            5 :[("10:00", "12:00")],#周六
            6 :[("10:00", "12:00")]#周日
        }

    # 解析时间字符串
    def parse_datetime(self,time_str):
        return datetime.strptime(time_str, '%Y/%m/%d %H:%M')

    # 检查时间段是否重叠
    def is_overlap(self,time_range, dataset_range):
        start1, end1 = time_range
        start2, end2 = dataset_range
        return start1 < end2 and start2 < end1
    def check_time(self,dataset_time_range):
        start_str, end_str = dataset_time_range.split(' ~ ')
        dataset_start = self.parse_datetime(start_str)
        dataset_end = self.parse_datetime(end_str)
        date = datetime(dataset_start.year, dataset_start.month, dataset_start.day)
        active_weekday = date.weekday()

        # 将给定的时间段转换为日期时间对象
        given_time_ranges_dt = [(datetime.strptime(start, '%H:%M').time(), datetime.strptime(end, '%H:%M').time()) for start, end in self.given_time_ranges[active_weekday]]

        # 检查是否与任何给定的时间段重叠
        if any(self.is_overlap((start, end), (dataset_start.time(), dataset_end.time())) for start, end in given_time_ranges_dt):
            return False

# 数据集中的时间段
dataset_time_range = "2024/04/24 10:00 ~ 2024/04/24 12:00"
timer = Timer()

if timer.check_time(dataset_time_range):
    print("数据集中的时间段与给定时间段重叠")
else:
    print("数据集中的时间段不与任何给定时间段重叠")
