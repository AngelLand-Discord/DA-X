import discord

from .base_handler import BaseHandler


class DeveloperHandler(BaseHandler):

    async def execute(
        self,
        command,
        payload,
        requested_by
    ):

        self.require_dev(requested_by)

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

        elif command == "STATUS":
            return await self.status()

        raise ValueError(
            f"Unknown developer command: {command}"
        )

    async def leave(self, payload):

        guild = self.guild(
            payload["guild_id"]
        )

        name = guild.name

        await guild.leave()

        self.log(
            f"Left guild: {name}"
        )

        return self.success(
            action="LEAVE",
            guild=name
        )

    async def sync(self):

        synced = await self.bot.tree.sync()

        self.log(
            f"Synced {len(synced)} commands."
        )

        return self.success(
            action="SYNC",
            commands=len(synced)
        )

    async def reload(self):

        success = []
        failed = []

        for extension in list(self.bot.extensions):

            try:

                await self.bot.reload_extension(
                    extension
                )

                success.append(extension)

            except Exception as e:

                failed.append(
                    {
                        "extension": extension,
                        "error": str(e)
                    }
                )

        self.log(
            f"Reloaded {len(success)} extension(s)."
        )

        return self.success(
            action="RELOAD",
            reloaded=success,
            failed=failed
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

                perms = channel.permissions_for(
                    guild.me
                )

                if not perms.send_messages:
                    continue

                try:

                    await channel.send(
                        embed=embed
                    )

                    sent += 1
                    break

                except Exception:
                    continue

        self.log(
            f"Broadcast sent to {sent} guild(s)."
        )

        return self.success(
            action="BROADCAST",
            guilds=sent
        )

    async def stop(self):

        self.log(
            "Shutdown requested."
        )

        await self.bot.close()

        return self.success(
            action="STOP"
        )

    async def status(self):

        users = sum(
            guild.member_count or 0
            for guild in self.bot.guilds
        )

        return self.success(
            action="STATUS",
            guilds=len(self.bot.guilds),
            users=users,
            latency=round(
                self.bot.latency * 1000,
                2
            ),
            cogs=len(self.bot.cogs)
        )
