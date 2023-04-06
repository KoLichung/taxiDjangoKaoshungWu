from firebase_admin.messaging import Message, Notification, APNSConfig, APNSPayload, Aps
from fcm_django.models import FCMDevice

import logging
logger = logging.getLogger(__file__)

def sendTest():
    message = Message(
        notification= Notification(title="title", body="text"),
        apns=APNSConfig(
            payload=APNSPayload(
                aps=Aps(
                    sound="default",
                )
            )
        ),
        # data={
        #     "Nick" : "Mario",
        #     "body" : "great match!",
        #     "Room" : "PortugalVSDenmark"
        # }
    )
    devices = FCMDevice.objects.all()
    # for device in devices:
    #     print(device.name)
    devices.send_message(message)

def sendTaskMessage(user):
    num_of_badge = 99 # your badge

    message = Message(
        data="message.data",
        notification= Notification(title="新任務來囉！", body="回 app 接單~"),
        apns=APNSConfig(
            payload=APNSPayload(
                aps=Aps(
                    badge=num_of_badge,
                    sound="default",
                )
            )
        ),
    )

    logger.info('message')
    logger.info(message)

    devices = FCMDevice.objects.filter(user=user)
    devices.send_message(message)
    print("send fcm")
