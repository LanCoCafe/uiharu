import asyncio
import re
from asyncio import Future

from disnake import Message
from disnake.abc import Messageable
from disnake.ext.commands import Bot as OriginalBot

from .conversation import Conversation, ConversationStatus


async def typing_loop(channel: Messageable):
    while True:
        await channel.trigger_typing()
        await asyncio.sleep(9)


class Bot(OriginalBot):
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
            await self.conversation.prepare()

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

        prompt = re.sub(r'<@([0-9]+)>', "", message.content)

        future: Future = asyncio.ensure_future(typing_loop(message.channel))

        response = await self.conversation.ask(prompt)

        future.cancel()

        await message.reply(response)
