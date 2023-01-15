from disnake import Message
from disnake.ext.commands import Bot as OriginalBot

from .conversations import ConversationManager


class Bot(OriginalBot):
    def __init__(self, conversation_manager: ConversationManager, *args, **kwargs):
        """
        :param conversation_manager: SessionManager instance
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(*args, **kwargs)

        self.conversation_manager = conversation_manager

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.author.id == self.user.id:
            return

        if self.user not in message.mentions:  # This part is suck, I will find a way to improve it.
            try:
                if message.reference.cached_message.author.id == self.user.id:
                    pass
            except AttributeError:
                return

        if message.content == "?exit":
            await self.conversation_manager.remove_conversation(message.author.id)

            await message.reply("✅ Conversation ended.")

            return

        await message.channel.trigger_typing()

        conversation = await self.conversation_manager.get_conversation(message.author.id)

        await message.reply(await conversation.ask(message.content))
