import asyncio
from enum import Enum
from typing import Union

from revChatGPT.V1 import Chatbot


# Exceptions
class NotPrepared(Exception):
    pass


# Enums
class ConversationStatus(Enum):
    IDLE = 0
    PREPARING = 1
    PREPARED = 2


# Classes
class Question:
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.response = ""

    def __str__(self):
        return self.response

    def is_responded(self):
        """
        Check if question has been responded.
        """
        return self.response != ""

    def assign_response(self, response: dict):
        """
        Assign response to question.
        :param response: Response dict from Chatbot.ask()
        """
        # Response will be like this:
        # {
        #     "message": str,
        #     "conversation_id": str,
        #     "parent_id": str,
        # }
        
        prev_text = ""
        for i in response:
            self.response = i["message"][len(prev_text) :]
            print(self.response, end="", flush=True)
            prev_text = i["message"]



class Conversation:
    def __init__(self, chatbot: Chatbot, brainwash: list[Question]):
        """
        Initials a conversation
        :param chatbot: Chatbot instance
        :param brainwash: A list of message to brainwash ChatGPT
        """
        self.chatbot = chatbot
        self.status = ConversationStatus.IDLE

        self.brainwash = brainwash

        self.conversation_id: Union[str, None] = None  # This will be generated after first message is sent

        self.question_queue = []

        self.dirtiness = 0

    async def wash_brain(self, wait: bool = False):
        """
        Wash brain with brainwash messages
        :return:
        """
        for message in self.brainwash:
            await self.ask(message, should_prepared=False, wait=wait)

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

    async def ask(self, message: Question, should_prepared: bool = True, wait: bool = True) -> str:
        """
        Asks chatgpt a question in this conversation
        :param message: Message to ask
        :param should_prepared: Should this conversation in a prepared status
        :param wait: Should this function wait for response, if False, no response will be returned
        :return: Response message as str
        :raise: Not Prepared if should_prepared is True and conversation isn't prepared
        """
        if not self.status == ConversationStatus.PREPARED and should_prepared:
            raise NotPrepared("should_prepared is True but the Conversation isn't prepared yet.")

        self.question_queue.append(message)

        if wait:
            while not message.is_responded():
                await asyncio.sleep(1)

            return message.response

        return ""

    def start_asking_loop(self, loop: asyncio.AbstractEventLoop):
        """
        Start a loop to ask questions in queue.
        This must be called before any question is asked, or no response will be returned.
        :param loop:
        :return:
        """
        loop.create_task(self.__asking_loop(loop))

    async def __asking_loop(self, loop: asyncio.AbstractEventLoop):
        while True:
            if self.dirtiness >= 3:  # TODO: Load dirtiness cap from env instead
                await self.wash_brain(wait=False)

                self.dirtiness = 0

            if self.question_queue:
                question = self.question_queue.pop(0)

                print(f"Start asking question {question.prompt}")

                await asyncio.sleep(0.1 * len(question.prompt))  # Simulate typing

                try:
                    response = await loop.run_in_executor(
                        None, self.chatbot.ask, question.prompt, self.conversation_id
                    )

                    if not response:
                        raise Exception("Response is empty")

                except Exception as error:
                    question.assign_response(
                        {
                            "conversation_id": self.conversation_id,
                            "message": f"發生了一些錯誤 \n```py\n{error}```",
                        }
                    )

                    continue


                self.conversation_id = next(response)["conversation_id"]

                question.assign_response(response)

                self.dirtiness += 1

            await asyncio.sleep(1)

    def close(self):
        self.chatbot.delete_conversation(self.conversation_id)

        return
