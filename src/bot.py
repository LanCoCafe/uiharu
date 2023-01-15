import re

from disnake import Message, Game, Status
from disnake.ext.commands import InteractionBot

from .conversation import Conversation, ConversationStatus


class Bot(InteractionBot):
    def __init__(self, conversation: Conversation, *args, **kwargs):
        """
        :param conversation: Conversation instance
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(*args, **kwargs)

        self.conversation = conversation

    async def on_ready(self):
        if self.conversation.status != ConversationStatus.PREPARED:
            await self.change_presence(activity=Game("準備中"), status=Status.dnd)

            await self.conversation.prepare()

            await self.change_presence(activity=Game("待命中"), status=Status.online)

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.author.id == self.user.id:
            return

        if self.user not in message.mentions:  # This part is suck, I will find a way to improve it.
            if not message.reference.cached_message:
                return
            
            if not message.reference.cached_message.author.id == self.user.id:
                return

        prompt = re.sub(r'<@([0-9]+)>', "", message.content)

        await message.channel.trigger_typing()

        response = await self.conversation.ask(prompt)

        await message.reply(response)
