import json

from channels.generic.websocket import AsyncWebsocketConsumer


class PoJsonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connect")
        await self.channel_layer.group_add("ws", self.channel_name)

        await self.accept()

    # Receive message from room group
    async def process(self, event):
        print("***")
        print(event)
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
