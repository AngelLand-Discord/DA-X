import discord


class SystemHandler:

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, command, payload):

        command = command.upper()

        if command == "ANNOUNCE":
            return await self.announce(payload)

        elif command == "SAY":
            return await self.say(payload)

        elif command == "EMBED":
            return await self.embed(payload)

        elif command == "PURGE":
            return await self.purge(payload)

        elif command == "LOCKDOWN":
            return await self.lockdown(payload)

        elif command == "UNLOCK":
            return await self.unlock(payload)

        elif command == "SLOWMODE":
            return await self.slowmode(payload)

        raise ValueError(f"Unknown System Command: {command}")

    async def announce(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        embed = discord.Embed(
            title="📢 Announcement",
            description=payload["message"],
            colour=discord.Colour.blurple()
        )

        await channel.send(embed=embed)

    async def say(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        await channel.send(
            payload["message"]
        )

    async def embed(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        embed = discord.Embed(
            title=payload["title"],
            description=payload["description"],
            colour=discord.Colour.from_str(
                payload.get(
                    "colour",
                    "#5865F2"
                )
            )
        )

        await channel.send(
            embed=embed
        )

    async def purge(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        await channel.purge(
            limit=int(payload["amount"])
        )

    async def lockdown(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        overwrite = channel.overwrites_for(
            channel.guild.default_role
        )

        overwrite.send_messages = False

        await channel.set_permissions(
            channel.guild.default_role,
            overwrite=overwrite
        )

    async def unlock(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        overwrite = channel.overwrites_for(
            channel.guild.default_role
        )

        overwrite.send_messages = None

        await channel.set_permissions(
            channel.guild.default_role,
            overwrite=overwrite
        )

    async def slowmode(self, payload):

        channel = self.bot.get_channel(
            int(payload["channel_id"])
        )

        if channel is None:
            raise ValueError("Channel not found.")

        await channel.edit(
            slowmode_delay=int(payload["seconds"])
        )