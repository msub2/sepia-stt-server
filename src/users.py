"""Authenticate and handle users"""

import time
import asyncio

from fastapi import WebSocket

from socket_messages import SocketMessage, SocketPingMessage, SocketErrorMessage

# For now we just use a simple static token.
COMMON_TOKEN = "test123"

# Client timeout - kick fast
HEARTBEAT_DELAY = 10
TIMEOUT_SECONDS = 15

class SessionIds:
    """Generate session IDs"""
    last_session_id = 0

    @staticmethod
    def get_new_sesstion_id():
        """Generate new session ID"""
        SessionIds.last_session_id += 1
        if SessionIds.last_session_id > 9999:
            SessionIds.last_session_id = 1
        return f"{SessionIds.last_session_id}-{int(time.time())}"

class SocketUser:
    """Class representing a user with some basic info and auth. method"""
    def __init__(self, websocket: WebSocket):
        self.is_authenticated = False
        self.is_alive = True
        self.last_alive_sign = int(time.time())
        self.socket = websocket
        self.session_id = SessionIds.get_new_sesstion_id()
        self.task = self.create_heartbeat_loop_task()

    async def authenticate(self, client_id, token):
        """Check if user is valid"""
        # TODO: Replace with user list
        if client_id is not None and token == COMMON_TOKEN:
            self.is_authenticated = True

    async def send_message(self, message: SocketMessage):
        """Send socket message to user"""
        await self.socket.send_json(message.json)

    async def ping_client(self):
        """Send alive ping to client (and expect pong answer)"""
        ping_msg = SocketPingMessage(msg_id = None)
        await self.send_message(ping_msg)

    def on_client_activity(self, is_binary_or_welcome):
        """When message is received set last active time"""
        # NOTE: we count only data messages as life sign (why else would the client stay?)
        if is_binary_or_welcome:
            self.last_alive_sign = int(time.time())
    
    def on_closed(self):
        """Connection was closed"""
        self.is_alive = False

    async def heartbeat_loop(self):
        """Continous heart-beat check to make sure inactive
        clients are kicked fast"""
        while self.is_alive:
            await asyncio.sleep(HEARTBEAT_DELAY)
            if (int(time.time()) - self.last_alive_sign) > TIMEOUT_SECONDS:
                # We are kind and inform the user that he will be kicked :-p
                await self.send_message(SocketErrorMessage(408,
                    "TimeoutMessage", "Client was inactive for too long."))
                self.is_alive = False
                await self.socket.close(1013)
                #self.task.cancel()
            elif self.is_alive:
                await self.ping_client()

    def create_heartbeat_loop_task(self):
        """Create heart-beat loop task"""
        loop = asyncio.get_running_loop()
        return loop.create_task(self.heartbeat_loop())
