import asyncio
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
    def __init__(self, chatbot: Chatbot):
        """
        Initials a conversation
        :param chatbot: Chatbot instance
        """
        self.chatbot = chatbot
        self.status = ConversationStatus.IDLE

        self.conversation_id: Union[str, None] = None  # This will be generated after first message is sent

    async def prepare(self, brainwash: list[str]) -> None:
        """
        Prepare a conversation with specified brainwashing messages
        :param brainwash: A list of message to brainwash ChatGPT
        :return: None
        """
        self.status = ConversationStatus.PREPARING

        print("Preparing a new conversation")

        for message in brainwash:
            await self.ask(message, should_prepared=False)

        self.status = ConversationStatus.PREPARED

        print(f"Conversation {self.conversation_id} prepared")

    async def ask(self, message: str, should_prepared: bool = True) -> str:
        """
        Asks chatgpt a question in this conversation
        :param message: Message to ask
        :param should_prepared: Should this conversation in a prepared status
        :return: Response message
        :raise: Not Prepared if should_prepared is True and conversation isn't prepared
        """
        if not self.conversation_id and should_prepared:
            raise NotPrepared("should_prepared is True but the Conversation isn't prepared yet.")

        # Response will be like this:
        # {
        #     "message": str,
        #     "conversation_id": str,
        #     "parent_id": str,
        # }

        print(f"{self.conversation_id or 'Not assigned'}: {message}")

        while True:
            # noinspection PyBroadException
            try:
                response = self.chatbot.ask(message, self.conversation_id)

                break
            except Exception:  # This has a high chance to be 429, so sleep for half a minute
                await asyncio.sleep(30)

                continue

        self.conversation_id = response['conversation_id']

        print(f"{response['conversation_id'][:23]}... / ChatGPT: {response['message']}")

        return response['message']


class ConversationManager:
    def __init__(self, chatbot: Chatbot, brainwash: list[str], prepare_amount: int = 1):
        """
        :param chatbot: Chatbot instance
        :param prepare_amount: Amount of conversation to be prepared for future using
        """
        self.chatbot = chatbot
        self.conversations: dict[int, Conversation] = {}

        self.prepare_amount = prepare_amount
        self.conversation_pool: list[Conversation] = []

        self.brainwash = brainwash

        self.event_loop = asyncio.get_event_loop()
        self.event_loop.create_task(self.check_conversation())

    async def get_conversation(self, user_id: int, generate: bool = True) -> Conversation:
        """
        Get conversation id from user id
        :param user_id: User ID for this conversation
        :param generate: Whether to create a new conversation when user doesn't have one
        :return: Conversation id, None if not found and generate is False
        """
        result = self.conversations.get(user_id)

        if not result and generate:  # User doesn't have a conversation
            result = await self.new_conversation()

            self.conversations[user_id] = result  # Assign conversation to user

        return result

    async def new_conversation(self) -> Conversation:
        """
        Get a new conversation from pool, Wait for a new one if not found
        :return: Conversation
        """
        while self.usable_conversation_amount() < 1:  # Blocks until pool isn't empty
            await asyncio.sleep(5)

        return self.conversation_pool.pop(0)

    async def remove_conversation(self, user_id: int) -> None:
        """
        Removes conversation for specified user id from this manager

        Note: Nothing will happen if user doesn't have a conversation
        :param user_id: The user id for the conversation
        :return: None
        """
        try:
            conversation = self.conversations.pop(user_id)

            if conversation:
                self.chatbot.delete_conversation(conversation.conversation_id)

        except IndexError:
            pass

    def usable_conversation_amount(self):
        return sum(
            1 for c in self.conversation_pool if c.status == ConversationStatus.PREPARED
        )

    async def check_conversation(self):
        """
        Keep check the conversation pool to make it always contentful
        :return:
        """
        while True:
            if self.usable_conversation_amount() < self.prepare_amount:
                new_conversation = Conversation(self.chatbot)

                self.conversation_pool.append(new_conversation)

                await new_conversation.prepare(self.brainwash)

            await asyncio.sleep(30)
            continue
