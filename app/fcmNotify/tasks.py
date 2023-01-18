from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice

def sendTest():
    message = Message(
        notification= Notification(title="title", body="text"),
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
    message = Message(
        notification= Notification(title="新任務來囉！", body="回 app 接單~"),
    )
    devices = FCMDevice.objects.filter(user=user)
    devices.send_message(message)
    print("send fcm")
