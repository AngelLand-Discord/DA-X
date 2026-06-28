import os

import discord
from discord.ext import commands

DEV_ID = int(os.getenv("DEV_ID", "0"))


class Developer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------
    # Checks
    # --------------------------------------------------

    def is_dev(self, user_id: int) -> bool:
        return user_id == DEV_ID

    # --------------------------------------------------
    # DevCmd
    # --------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if not self.is_dev(message.author.id):
            return

        content = message.content.strip()

        if not content.lower().startswith("dax devcmd"):
            return

        args = content.split()

        if len(args) < 3:
            await message.reply(
                "Usage: `Dax Devcmd <command>`"
            )
            return

        command = args[2].lower()

        # ----------------------------------------
        # Ping
        # ----------------------------------------

        if command == "ping":

            await message.reply(
                f"Pong! `{round(self.bot.latency*1000)}ms`"
            )

        # ----------------------------------------
        # Leave
        # ----------------------------------------

        elif command == "leave":

            guild = message.guild

            await message.reply(
                f"Leaving **{guild.name}**..."
            )

            await guild.leave()

        # ----------------------------------------
        # Sync
        # ----------------------------------------

        elif command == "sync":

            synced = await self.bot.tree.sync()

            await message.reply(
                f"Synced **{len(synced)}** commands."
            )

        # ----------------------------------------
        # Reload
        # ----------------------------------------

        elif command == "reload":

            loaded = 0

            for extension in list(self.bot.extensions):

                try:
                    await self.bot.reload_extension(
                        extension
                    )

                    loaded += 1

                except Exception:
                    pass

            await message.reply(
                f"Reloaded **{loaded}** cogs."
            )

        # ----------------------------------------
        # Guilds
        # ----------------------------------------

        elif command == "guilds":

            text = ""

            for guild in self.bot.guilds:

                text += (
                    f"• {guild.name}"
                    f" ({guild.id})\n"
                )

            if not text:
                text = "No guilds."

            await message.reply(text)

        # ----------------------------------------
        # Unknown
        # ----------------------------------------

        else:

            await message.reply(
                "Unknown Dev Command."
            )


async def setup(bot):

    await bot.add_cog(
        Developer(bot)
    )
