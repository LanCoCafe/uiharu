import asyncio
import time
from collections import deque
from enum import Enum
from typing import Union

from revChatGPT.ChatGPT import Chatbot


# Exceptions
class NotPrepared(Exception):
    pass


# Enums
class ConversationStatus(Enum):
    IDLE = 0
    PREPARING = 1
    PREPARED = 2


# Classes
class Conversation:
    def __init__(self, chatbot: Chatbot, brainwash: list[str]):
        """
        Initials a conversation
        :param chatbot: Chatbot instance
        :param brainwash: A list of message to brainwash ChatGPT
        """
        self.chatbot = chatbot
        self.status = ConversationStatus.IDLE

        self.brainwash = brainwash

        self.conversation_id: Union[str, None] = None  # This will be generated after first message is sent

        self.last_message_time: int = 0
        self.last_brainwash_time: int = 0
        self.last_messages = deque(maxlen=5)
        self.working = False

    async def wash_brain(self):
        for message in self.brainwash:
            await self.ask(message, should_prepared=False, record=False)

        self.last_brainwash_time = time.time()

        asyncio.get_event_loop().create_task(self.brain_washing())

        return

    async def prepare(self) -> None:
        """
        Prepare a conversation with specified brainwashing messages
        :return: None
        """
        self.status = ConversationStatus.PREPARING

        print("Preparing a new conversation")

        await self.wash_brain()

        self.status = ConversationStatus.PREPARED

        print(f"Conversation {self.conversation_id} prepared")

    async def ask(self, message: str, should_prepared: bool = True, record: bool = True) -> str:
        """
        Asks chatgpt a question in this conversation
        :param message: Message to ask
        :param should_prepared: Should this conversation in a prepared status
        :param record: Should this message be recorded
        :return: Response message
        :raise: Not Prepared if should_prepared is True and conversation isn't prepared
        """
        if not self.status == ConversationStatus.PREPARED and should_prepared:
            raise NotPrepared("should_prepared is True but the Conversation isn't prepared yet.")

        # Response will be like this:
        # {
        #     "message": str,
        #     "conversation_id": str,
        #     "parent_id": str,
        # }

        print(f"{self.conversation_id or 'Not assigned'}: {message}")

        self.working = True
        while True:
            # noinspection PyBroadException
            try:
                response = self.chatbot.ask(message, self.conversation_id)

                break
            except Exception:  # This has a high chance to be 429, so sleep for half a minute
                await asyncio.sleep(30)

                continue

        await asyncio.sleep(2)
        self.working = False

        if record:
            self.last_messages.append(message)
            self.last_message_time = time.time()

        self.conversation_id = response['conversation_id']

        print(f"{response['conversation_id'][:23]}... / ChatGPT: {response['message']}")

        return response['message']

    async def brain_washing(self):
        while True:
            if self.status == ConversationStatus.PREPARED \
                    and (time.time() - self.last_message_time) > 120 \
                    and (time.time() - self.last_brainwash_time) > 120 \
                    and len(self.last_messages) == 5:
                await self.wash_brain()

                self.last_messages.clear()

            await asyncio.sleep(20)

    def close(self):
        self.chatbot.delete_conversation(self.conversation_id)

        return
