import discord

from discord.ext import commands


BAD_WORDS = [

    "badword1",
    "badword2",
    "badword3"

]


class AutoMod(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        if message.author.bot:

            return

        content = message.content.lower()

        # Anti Bad Word

        for word in BAD_WORDS:

            if word in content:

                await message.delete()

                await message.channel.send(

                    f"{message.author.mention} "

                    "watch your language."

                )

                return

        # Anti Spam

        if len(
            message.content
        ) > 1500:

            await message.delete()

            return

        # Anti Invite

        if (
            "discord.gg/"
            in content
        ):

            await message.delete()

            await message.channel.send(

                f"{message.author.mention} "

                "invite links are blocked."

            )

            return


async def setup(
    bot
):

    await bot.add_cog(
        AutoMod(bot)
    )
