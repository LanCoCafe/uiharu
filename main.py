import asyncio
from os import getenv

from disnake import Intents
from revChatGPT.ChatGPT import Chatbot

from src.bot import Bot
from src.conversation import Conversation, Question


def main():
    conversation = Conversation(
        Chatbot({"session_token": getenv("CHATGPT_TOKEN")}),
        load_brainwash()
    )

    bot = Bot(conversation, intents=Intents.all())

    try:
        bot.run(getenv("DISCORD_TOKEN"))
    except KeyboardInterrupt:
        conversation.close()

        asyncio.get_event_loop().close()


def load_brainwash() -> list[Question]:
    """
    Load brainwash messages from brainwash.txt
    :return: A list of Question
    """
    with open("/home/twmccreeper/文件/uiharu/brainwash.txt", "r", encoding='utf-8') as f:
        return [Question(line) for line in f.readlines()]


if __name__ == "__main__":
    main()
