import discord

from .base_handler import BaseHandler


class SystemHandler(BaseHandler):

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

        raise ValueError(f"Unknown system command: {command}")

    async def announce(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        embed = discord.Embed(
            title="📢 Announcement",
            description=payload["message"],
            colour=discord.Colour.blurple()
        )

        if payload.get("footer"):
            embed.set_footer(text=payload["footer"])

        if payload.get("thumbnail"):
            embed.set_thumbnail(url=payload["thumbnail"])

        if payload.get("image"):
            embed.set_image(url=payload["image"])

        await channel.send(embed=embed)

        return self.success(action="ANNOUNCE")

    async def say(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        await channel.send(payload["message"])

        return self.success(action="SAY")

    async def embed(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        embed = discord.Embed(
            title=payload["title"],
            description=payload["description"],
            colour=discord.Colour.from_str(
                payload.get("colour", "#5865F2")
            )
        )

        if payload.get("footer"):
            embed.set_footer(text=payload["footer"])

        if payload.get("thumbnail"):
            embed.set_thumbnail(url=payload["thumbnail"])

        if payload.get("image"):
            embed.set_image(url=payload["image"])

        await channel.send(embed=embed)

        return self.success(action="EMBED")

    async def purge(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        deleted = await channel.purge(
            limit=int(payload["amount"])
        )

        return self.success(
            action="PURGE",
            deleted=len(deleted)
        )

    async def lockdown(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        overwrite = channel.overwrites_for(
            guild.default_role
        )

        overwrite.send_messages = False

        await channel.set_permissions(
            guild.default_role,
            overwrite=overwrite
        )

        return self.success(action="LOCKDOWN")

    async def unlock(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        overwrite = channel.overwrites_for(
            guild.default_role
        )

        overwrite.send_messages = None

        await channel.set_permissions(
            guild.default_role,
            overwrite=overwrite
        )

        return self.success(action="UNLOCK")

    async def slowmode(self, payload):

        guild = self.guild(payload["guild_id"])
        channel = self.channel(guild, payload["channel_id"])

        await channel.edit(
            slowmode_delay=int(payload["seconds"])
        )

        return self.success(action="SLOWMODE")
