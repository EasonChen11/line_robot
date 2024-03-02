# 導入Discord.py模組
import re
import discord
import requests
import os
from bs4 import BeautifulSoup
import threading
import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime,timedelta

class Reptile:
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
            self.load_csv()

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

    def load_csv(self):
        df = pd.read_csv(self.file_path)
        self.all_class = df.values.tolist()

    def save_csv(self):
        # sort by Active Time
        self.all_class.sort(key=lambda x: datetime.strptime(x[2].split(" ")[0], '%Y/%m/%d'))
        df = pd.DataFrame(self.all_class, columns = ['label','Title', 'Active Time', 'Sign Up Time', 'URL'])
        df.to_csv(self.file_path, index=False, encoding='utf-8-sig')

class Timer:
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
    def check_weekday(self,dataset_time_range,limit):
        dataset_time_range, weekday = dataset_time_range.split(" (")
        dataset_start, dataset_end = self.dataset_time_range_parse(dataset_time_range)
        date = datetime(dataset_start.year, dataset_start.month, dataset_start.day)
        active_weekday = date.weekday()
        return active_weekday in limit

class DiscordBot(Reptile):
    def __init__(self):
        super().__init__(start_page=1)
        self.intents = discord.Intents.default()
        self.token = "MTIxMzM4MjMyODE3NzY2NDAwMA.GeIvJT.vGLEKLs3GwQu33oI4d8m7DFMNFlrzmfCkokj9Q"
        self.intents.message_content = True
        self.client = discord.Client(intents = self.intents)
            # 在初始化過程中綁定事件處理器
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        # use markdown to make the introduction more beautiful
        self.introduction = """
歡迎使用本機器人，本機器人是用來查詢國立中正大學的活動資訊，請輸入指令`! introduction`以獲得更多資訊。
本機器人支援的指令如下：
* `! introduction`: 獲得機器人的簡介
* `! event`: 查詢所有活動
* `! event [1-7] [1-7] ...`: 查詢指定星期的活動，例如`! event 1 3 5`可以查詢周一、周三和周五的活動
使用愉快！
        """
    async def on_ready(self):
        print(f"目前登入身份 --> {self.client.user}")
        # send introduction
    
    async def on_message(self, message):
            if message.author == self.client.user:
                return
            # user input introduction send markdown introduction
            if message.content == "! introduction":
                await message.channel.send(self.introduction)
                if self.is_update_needed(hours=12):
                    print("Running the crawler to update course.csv...")
                    self.determine_page_count_and_crawl()
                    self.save_csv()
                else:
                    print("Using the existing course.csv...")
                    self.load_csv()
                return
# 假設當收到特定訊息時，發送嵌入的資訊
            embeds = []

            # 使用正则表达式匹配命令和参数
            # 这个正则表达式支持指令前后有一个或多个空格，以及可选的数字参数
            cmd_pattern = re.compile(r"^!\sevent(?:\s+([1-7](?:\s+[1-7]){0,6}))?$")
            match = cmd_pattern.match(message.content)
            if match:
                # 如果存在参数，则将参数字符串分割为列表，否则为空列表
                args_str = match.group(1)
                args = args_str.split() if args_str else []
                args = [int(i)-1 for i in args]# 輸入是周一到周日，但是程式是0到6
                args= set(args)
                print(args)
                if len(args) == 0:
                    embeds = self.package_message([0,1,2,3,4,5,6])
                else:
                    embeds = self.package_message(args)
            else:
                await message.channel.send("請輸入正確指令")
                return
            total_event = 0
            for information in embeds:
                await message.channel.send(embed=information)
                total_event += 1
            await message.channel.send("總共有"+str(total_event)+"筆資料")

    def package_message(self,limit):
        embeds = []
        messages = [i for i in self.all_class if self.timer_operation.check_weekday(i[2],limit)]
        for i in messages:
            embed = discord.Embed(
                title=i[0]+i[1],
                url=i[4],
                color=0x5dade2  # 可以選擇一個顏色
            )
            embed.add_field(name="活動時間", value=i[2], inline=False)
            embed.add_field(name="報名時間", value=i[3], inline=False)
            embeds.append(embed)
        return embeds
    def run(self):
        self.client.run(self.token)


if __name__ == "__main__":
    # reptile = Reptile(start_page=1)
    discord_bot = DiscordBot()
    discord_bot.run()