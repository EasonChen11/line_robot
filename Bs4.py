import requests
import os
from bs4 import BeautifulSoup
import threading
import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime,timedelta
from linebot import LineBotApi
from linebot.models import FlexSendMessage
from linebot.models import TextSendMessage



class Reptile():
    def __init__(self, start_page):
        self.all_class = []
        self.url = "https://events.lib.ccu.edu.tw/"
        self.main_page = "event/search/?time=join"
        self.start_page = start_page
        self.end_page_check = 0
        self.file_path = 'course.csv'
        self.timer_operation = Timer()
        if self.is_update_needed(hours=12):
            print("Running the crawler to update course.csv...")
            self.determine_page_count_and_crawl()
            self.save_csv()
        else:
            print("Using the existing course.csv...")
            self.load_data()

    def determine_page_count_and_crawl(self):
        page = self.start_page
        threads = []
        while True:
            response = requests.get(f"{self.url}{self.main_page}&page={page}")
            if response.status_code != 200:
                break  # 没有更多页面
            t=threading.Thread(target=self.process_page, args=(page,response))
            t.start()
            threads.append(t)
            time.sleep(0.5)  # 添加适当的延时
            page += 1
        for thread in threads:
            thread.join()

    def process_page(self, page,response):
        try:
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.get_class_list(soup)
                self.get_class_name()
            else:
                print(f"Error fetching page {page}: Status code {response.status_code}")
        except Exception as e:
            print(f"Exception occurred while fetching page {page}: {e}")

    def get_class_list(self,soup):
        ul_elements = soup.find_all('ul', class_='list_dotline list_marginM mt-2 uk-list uk-list-line')  # Update the class name if necessary
        # 首先找到所有类名为'list-dotline'的'ul'元素
        # 然后遍历这些ul元素，收集它们的'li'子元素
        self.class_list = []
        for ul in ul_elements:
            self.class_list.extend(ul.find_all('li'))

    def get_class_name(self):
        for item in tqdm(self.class_list):
            one_class = []
            # find h3 class="fontSizeH3 color_secondary font-weight-bold uk-margin-small" and get text
            title = item.find('h3', class_='fontSizeH3 color_secondary font-weight-bold uk-margin-small').text.strip()
            active_time = item.find('h4').text.strip()
            if self.timer_operation.check_time(active_time):
                continue
            if "】" in title:
                label,title = title.split("】")
                one_class.append(label+"】")
            else:
                one_class.append("【無分類】")
            one_class.append(title)
            weekday = self.timer_operation.weekday_dict[self.timer_operation.dataset_time_range_parse(active_time)[0].weekday()]
            one_class.append(active_time+" ("+str(weekday)+")")
            sign_up_time, class_url = self.get_class_sign_up_time(item.find('a',class_='remove_underline bg_hover_blackOpacity05 w-100')['href'])
            if sign_up_time == None and class_url == None:
                continue
            one_class.append(sign_up_time)
            one_class.append(class_url)
            self.all_class.append(one_class)
    
    def get_class_sign_up_time(self, class_url_suffix):
        try:
            class_url = self.url + class_url_suffix
            response = requests.get(class_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            sign_up_time_and_people_number= soup.find_all('h4', class_='fontSizeH5 font-weight-bold uk-margin-small')  # Update the class if necessary
            if self.full_people(sign_up_time_and_people_number[1]):
                return None, None
            elif sign_up_time_and_people_number[0]:
                return sign_up_time_and_people_number[0].span.text, class_url
            else:
                return "無報名時間", class_url
        except Exception:
            return None, None

    def full_people(self, soup):
        number_lists = [i.text for i in soup.find_all('span')]
        return number_lists[0] == number_lists[1]
    
    def get_title_length(self):
        return len(self.all_class)
    
    def is_update_needed(self,hours=12):
        """检查文件是否需要更新。
        
        参数:
        - file_path: 文件路径
        - hours: 更新间隔小时数，默认为12小时
        
        返回:
        - True 如果文件不存在或者更新时间超过12小时
        - False 如果更新时间少于12小时
        """
        if not os.path.exists(self.file_path):
            return True
        last_modified_time = datetime.fromtimestamp(os.path.getmtime(self.file_path))
        if datetime.now() - last_modified_time > timedelta(hours=hours):
            return True
        return False

    def load_data(self):
        df = pd.read_csv(self.file_path)
        self.all_class = df.values.tolist()

    def save_csv(self):
        df = pd.DataFrame(self.all_class, columns = ['label','Title', 'Active Time', 'Sign Up Time', 'URL'])
        df.to_csv(self.file_path, index=False, encoding='utf-8-sig')

class Timer():
    def __init__(self):
            # 给定的时间段
        self.given_time_ranges = {
            0 :[("7:00", "12:00"),("16:45","22:00")],#周一
            1 :[("7:00", "14:30")],#周二
            2 :[("7:00", "16:00")],#周三
            3 :[("7:00", "14:30")],#周四
            4 :[("7:00", "12:50")],#周五
            5 :[],#周六
            6 :[]#周日
        }
        self.weekday_dict = {
            0: "周一",
            1: "周二",
            2: "周三",
            3: "周四",
            4: "周五",
            5: "周六",
            6: "周日"
        }

    # 解析时间字符串
    def parse_datetime(self,time_str):
        return datetime.strptime(time_str, '%Y/%m/%d %H:%M')

    # 检查时间段是否重叠
    def is_overlap(self,time_range, dataset_range):
        start1, end1 = time_range
        start2, end2 = dataset_range
        return start1 < end2 and start2 < end1
    
    def dataset_time_range_parse(self,dataset_time_range):
        start_str, end_str = dataset_time_range.split(' ~ ')
        dataset_start = self.parse_datetime(start_str)
        dataset_end = self.parse_datetime(end_str)
        return dataset_start, dataset_end
    
    def check_time(self,dataset_time_range):
        dataset_start, dataset_end = self.dataset_time_range_parse(dataset_time_range)
        date = datetime(dataset_start.year, dataset_start.month, dataset_start.day)
        active_weekday = date.weekday()

        # 将给定的时间段转换为日期时间对象
        given_time_ranges_dt = [(datetime.strptime(start, '%H:%M').time(), datetime.strptime(end, '%H:%M').time()) for start, end in self.given_time_ranges[active_weekday]]

        # 检查是否与任何给定的时间段重叠
        if any(self.is_overlap((start, end), (dataset_start.time(), dataset_end.time())) for start, end in given_time_ranges_dt):
            return True


class LINE(Reptile):
    def __init__(self, start_page):
        super().__init__(start_page)
        self.channel_access_token='yOkdTSG1hnXURevERb5vOr6XtpD5XB0DDtFFgNm15iip+wyDHBMSSMopPf9N9/64hahzVouW76IuPxXThQixR2NlSAMZ8XpzuW/hXC0TCvarYj05OPzOSKirOVYQu+Zye/ftDFPirj0ND85Yllne5AdB04t89/1O/w1cDnyilFU='
        self.user_id='U60918c5473c3e542f9f77173baf01c3e'
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.send_message()
    
    def send_message(self):
        time_message ="美好的一天"+ datetime.now().strftime("%Y/%m/%d %H:%M")+"以下是可以報名的活動："
        self.line_bot_api.push_message(self.user_id, TextSendMessage(time_message))

        for i in self.all_class:
            flex_content = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": i[0] + i[1],
                            "weight": "bold",
                            "size": "md",
                            "wrap": True  # 啟用自動換行
                        },
                        {
                            "type": "text",
                            "text": "活動主題：" + i[1],
                            "margin": "md",
                            "wrap": True  # 啟用自動換行
                        },
                        {
                            "type": "text",
                            "text": "活動時間：" + i[2],
                            "margin": "md",
                            "wrap": True  # 啟用自動換行
                        },
                        {
                            "type": "text",
                            "text": "報名時間：" + i[3],
                            "margin": "md",
                            "wrap": True  # 啟用自動換行
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "活動連結",
                                "uri": i[4]
                            },
                            "style": "primary",
                            "margin": "md"
                        }
                    ]
                }
            }
            self.line_bot_api.push_message(self.user_id, FlexSendMessage(alt_text=i[0] + i[1], contents=flex_content))
        self.line_bot_api.push_message(self.user_id, TextSendMessage(text="總共有"+str(self.get_title_length())+"個活動可以報名"))

            # report_content = """
            # 【"""+i[0]+i[1]+"""】
            # 活動主題："""+i[1]+"""
            # 活動時間："""+i[2]+"""
            # 報名時間："""+i[3]+"""
            # 活動連結："""+i[4]+"""
            # """
            # self.line_bot_api.push_message(self.user_id, TextSendMessage(text=report_content))

line = LINE(start_page=1)
