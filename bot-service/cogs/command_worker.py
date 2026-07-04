import json

from discord.ext import commands, tasks

from database.database import (
    get_next_command,
    start_command,
    finish_command,
    fail_command,
)

from handlers.system_handler import SystemHandler
from handlers.developer_handler import DeveloperHandler
from handlers.moderation_handler import ModerationHandler


class CommandWorker(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.system = SystemHandler(bot)
        self.developer = DeveloperHandler(bot)
        self.moderation = ModerationHandler(bot)

        self.worker.start()

    def cog_unload(self):

        self.worker.cancel()

    @tasks.loop(seconds=1)
    async def worker(self):

        row = get_next_command()

        if row is None:
            return

        command_id = row["id"]

        try:

            start_command(command_id)

            payload = json.loads(row["payload"])

            command_type = row["command_type"].upper()
            command_name = row["command_name"].upper()

            if command_type == "SYSTEM":

                await self.system.execute(
                    command_name,
                    payload
                )

            elif command_type == "DEVELOPER":

                await self.developer.execute(
                    command_name,
                    payload,
                    row["requested_by"]
                )

            elif command_type == "MODERATION":

                await self.moderation.execute(
                    command_name,
                    payload
                )

            else:

                raise ValueError(
                    f"Unknown command type: {command_type}"
                )

            finish_command(command_id)

        except Exception as e:

            fail_command(
                command_id,
                str(e)
            )

            print(
                f"[Command Worker] {e}"
            )

    @worker.before_loop
    async def before_worker(self):

        await self.bot.wait_until_ready()


async def setup(bot):

    await bot.add_cog(
        CommandWorker(bot)
    )
