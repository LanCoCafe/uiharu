from os import getenv

from disnake import Intents
from revChatGPT.ChatGPT import Chatbot

from src.bot import Bot
from src.conversations import ConversationManager


def main():
    conversation_manager = ConversationManager(
        Chatbot({"session_token": getenv("CHATGPT_TOKEN")}),
        load_brainwash(),
        prepare_amount=3
    )

    bot = Bot(conversation_manager=conversation_manager, intents=Intents.all())

    try:
        bot.run(getenv("DISCORD_TOKEN"))
    except KeyboardInterrupt:
        bot.close()

        conversation_manager.close()


def load_brainwash():
    with open("brainwash.txt", "r", encoding='utf-8') as f:
        return f.readlines()


if __name__ == "__main__":
    main()
