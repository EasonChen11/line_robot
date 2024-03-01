import os
from datetime import datetime, timedelta
import pandas as pd

def is_update_needed(file_path, hours=0):
    """检查文件是否需要更新。
    
    参数:
    - file_path: 文件路径
    - hours: 更新间隔小时数，默认为12小时
    
    返回:
    - True 如果文件不存在或者更新时间超过12小时
    - False 如果更新时间少于12小时
    """
    if not os.path.exists(file_path):
        return True
    last_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    if datetime.now() - last_modified_time > timedelta(hours=hours):
        return True
    return False

def update_course_csv():
    """更新 course.csv 文件的示例函数"""
    print("Running the crawler to update course.csv...")
    # 这里放置您的爬虫代码，用于生成或更新 course.csv
    # ...

def use_existing_course_csv():
    """使用现有的 course.csv 文件的示例函数"""
    print("Using the existing course.csv...")
    # 这里放置读取和使用 course.csv 文件的代码
    # 例如，读取文件并打印内容
    df = pd.read_csv('course.csv')
    print(df)

# 主逻辑
file_path = 'course.csv'
if is_update_needed(file_path, 12):
    update_course_csv()
else:
    use_existing_course_csv()
