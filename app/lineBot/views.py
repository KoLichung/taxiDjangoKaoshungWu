# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage
import logging

logger = logging.getLogger(__file__)
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
 
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            logger.info(event)
            userId = event.source.user_id
            logger.info(f'line auto reply {userId}')

            profile = line_bot_api.get_profile(userId)

            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if event.message.text == "test":
                    message = TextSendMessage(text='this is for test！')
                    # message = ImageSendMessage(
                    #     original_content_url='https://i.imgur.com/vxQMxtm.png',
                    #     preview_image_url='https://i.imgur.com/vxQMxtm.png'
                    # )
                else:
                    message = TextSendMessage(text=f'{profile.display_name} 您好！\n 您沒有權限。或者輸入訊息無法辨別！')

                line_bot_api.reply_message(event.reply_token, message)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()