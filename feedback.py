from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('yOkdTSG1hnXURevERb5vOr6XtpD5XB0DDtFFgNm15iip+wyDHBMSSMopPf9N9/64hahzVouW76IuPxXThQixR2NlSAMZ8XpzuW/hXC0TCvarYj05OPzOSKirOVYQu+Zye/ftDFPirj0ND85Yllne5AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('753b5996c0b878c70f7de2601b55cb03')

@app.route("/callback", methods=['POST'])
def callback():
    # 從請求中獲取X-Line-Signature頭部用於驗證
    signature = request.headers['X-Line-Signature']
    # 從請求中獲取主體作為文本（用於驗證）
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 用戶發送的消息文本
    user_message = event.message.text
    
    # 基於用戶消息進行資料查找的邏輯
    # 假設這裡直接回覆了相同的消息
    reply_message = "你查詢的關鍵字是：" + user_message
    
    # 回覆消息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    app.run()
