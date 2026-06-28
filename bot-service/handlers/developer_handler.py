import os
import discord


DEV_ID = int(os.getenv("DEV_ID", "0"))


class DeveloperHandler:

    def __init__(self, bot):
        self.bot = bot

    def check_dev(self, user_id: int):

        if int(user_id) != DEV_ID:
            raise PermissionError(
                "Only the developer can execute developer commands."
            )

    async def execute(
        self,
        command,
        payload,
        requested_by
    ):

        self.check_dev(requested_by)

        command = command.upper()

        if command == "LEAVE":
            return await self.leave(payload)

        elif command == "SYNC":
            return await self.sync()

        elif command == "RELOAD":
            return await self.reload()

        elif command == "BROADCAST":
            return await self.broadcast(payload)

        elif command == "STOP":
            return await self.stop()

        raise ValueError(
            f"Unknown developer command: {command}"
        )

    async def leave(self, payload):

        guild = self.bot.get_guild(
            int(payload["guild_id"])
        )

        if guild is None:
            raise ValueError("Guild not found.")

        await guild.leave()

    async def sync(self):

        synced = await self.bot.tree.sync()

        print(
            f"[Developer] Synced {len(synced)} commands."
        )

    async def reload(self):

        count = 0

        for extension in list(self.bot.extensions):

            try:

                await self.bot.reload_extension(
                    extension
                )

                count += 1

            except Exception as e:

                print(
                    f"Reload failed: {extension}"
                )

                print(e)

        print(
            f"[Developer] Reloaded {count} extensions."
        )

    async def broadcast(self, payload):

        message = payload["message"]

        embed = discord.Embed(
            title="📢 DA-X Announcement",
            description=message,
            colour=discord.Colour.blurple()
        )

        sent = 0

        for guild in self.bot.guilds:

            for channel in guild.text_channels:

                permissions = channel.permissions_for(
                    guild.me
                )

                if permissions.send_messages:

                    try:

                        await channel.send(
                            embed=embed
                        )

                        sent += 1

                        break

                    except Exception:
                        continue

        print(
            f"[Developer] Broadcast sent to {sent} guilds."
        )

    async def stop(self):

        print(
            "[Developer] Shutdown requested."
        )

        await self.bot.close()
