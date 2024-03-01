import requests
import bs4
from lxml import html as lh

class Reptile:
    def __init__(self,start_page):
        self.all_class = []
        self.url = "https://events.lib.ccu.edu.tw/event/search/?time=join"
        self.page = start_page
        self.get_class_information()

    def get_class_information(self):
        while True:
            if self.get_html_content():
                break
            self.get_class_list()
            self.get_class_name()
            self.page += 1


    def get_html_content(self):
        try:
            self.html_content = requests.get(f"{self.url}/?page={self.page}").text
            self.doc = lh.fromstring(self.html_content)
            return False
        except Exception as e:
            print(e)
            print("共爬取", self.get_title_length(), "筆資料")
            return True

    def get_class_list(self):
        self.class_list = self.doc.xpath('//ul[contains(@class, "list_dotline")]/li')

    def get_class_name(self):
        for item in self.class_list:
            one_class = []
            one_class.append(item.xpath('.//a/div/div/h3/text()')[0].strip())
            one_class.append(item.xpath('.//a/div/div/h4/text()')[0].strip())
            sign_up_time, class_url = self.get_class_sign_up_time(item.xpath('.//a/@href'))
            one_class.append(sign_up_time)
            one_class.append(class_url)
            print(one_class)
            self.all_class.append(one_class)
    
    def get_class_sign_up_time(self, class_url):
        class_url = self.url + class_url[0]

        class_html_content = requests.get(class_url).text
        class_doc = lh.fromstring(class_html_content)
        sign_up_time = class_doc.xpath('//h4[contains(@class, "fontSizeH5 font-weight-bold uk-margin-small")]/span/text()')
        if len(sign_up_time) == 0:
            return "無報名時間", class_url
        return sign_up_time[0], class_url# 第一筆是報名時間
    
    def get_title_length(self):
        return len(self.all_class)

course = Reptile(start_page=1)
print(course.all_class, sep='\n')


