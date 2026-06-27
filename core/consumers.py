import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            
            # Join room group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

            # Retrieve unread notification count and the latest 5 unread notifications
            unread_data = await self.get_unread_notifications(self.user)
            await self.send(text_data=json.dumps({
                "type": "sync_notifications",
                "unread_count": unread_data["count"],
                "latest_notifications": unread_data["latest"]
            }))
        else:
            await self.close()

    @database_sync_to_async
    def get_unread_notifications(self, user):
        unread = user.notifications.filter(is_read=False)
        count = unread.count()
        latest = []
        for n in unread[:5]:
            latest.append({
                "id": n.id,
                "message": n.message,
                "link": f"/portal/notifications/read/{n.id}/" if n.id else "",
                "created_at": "Just now"
            })
        return {"count": count, "latest": latest}

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        notification = event["notification"]
        # Send notification object to client WebSocket
        await self.send(text_data=json.dumps({
            "type": "new_notification",
            "id": notification["id"],
            "message": notification["message"],
            "link": notification["link"],
            "created_at": notification["created_at"]
        }))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")
            if action == "mark_all_read":
                await self.mark_notifications_read(self.user)
                # Broadcast status to all open tabs for this user
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "sync_read_status"
                    }
                )
        except Exception as e:
            print("Error parsing socket command:", e)

    @database_sync_to_async
    def mark_notifications_read(self, user):
        user.notifications.filter(is_read=False).update(is_read=True)

    async def sync_read_status(self, event):
        # Notify the client tab to reset unread counts to 0 and empty list
        await self.send(text_data=json.dumps({
            "type": "sync_notifications",
            "unread_count": 0,
            "latest_notifications": []
        }))
