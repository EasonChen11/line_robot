from linebot import LineBotApi
from linebot.models import FlexSendMessage
from linebot.models import TextSendMessage
channel_access_token = 'yOkdTSG1hnXURevERb5vOr6XtpD5XB0DDtFFgNm15iip+wyDHBMSSMopPf9N9/64hahzVouW76IuPxXThQixR2NlSAMZ8XpzuW/hXC0TCvarYj05OPzOSKirOVYQu+Zye/ftDFPirj0ND85Yllne5AdB04t89/1O/w1cDnyilFU='
user_id = 'U60918c5473c3e542f9f77173baf01c3e'

line_bot_api = LineBotApi(channel_access_token)

flex_content = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "心理系微學分學習活動",
        "weight": "bold",
        "size": "md"
      },
      {
        "type": "text",
        "text": "活動主題：Network properties and cognitive functions of the human thalamus.",
        "margin": "md"
      },
      {
        "type": "text",
        "text": "活動時間：2024/03/15 13:00 ~ 2024/03/15 14:00 (周五)",
        "margin": "md"
      },
      {
        "type": "text",
        "text": "報名時間：2024/02/19 21:00 ~ 2024/03/12 23:59",
        "margin": "md"
      },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "活動連結",
          "uri": "https://events.lib.ccu.edu.tw//event/detail/list/1233/"
        },
        "style": "primary",
        "margin": "md"
      }
    ]
  }
}

# 發送Flex消息
line_bot_api.push_message(user_id, FlexSendMessage(alt_text="心理系微學分學習活動", contents=flex_content))
# 格式化報表內容
report_content = """
【心理系微學分學習活動】
活動主題：Network properties and cognitive functions of the human thalamus.
活動時間：2024/03/15 13:00 ~ 2024/03/15 14:00 (周五)
報名時間：2024/02/19 21:00 ~ 2024/03/12 23:59
活動連結：https://events.lib.ccu.edu.tw//event/detail/list/1233/
"""
line_bot_api.push_message(user_id, TextSendMessage(text=report_content))
