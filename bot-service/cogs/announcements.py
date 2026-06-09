import asyncio

import discord
from discord.ext import commands

from database.database import CUR


class Announcements(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # DM USER
    # =========================

    @commands.command()
    @commands.has_permissions(
        manage_guild=True
    )
    async def dm(
        self,
        ctx,
        member: discord.Member,
        *,
        message: str
    ):

        try:

            await member.send(
                message
            )

            await ctx.send(
                f"✅ DM sent to {member.mention}"
            )

        except Exception as e:

            await ctx.send(
                f"❌ Failed: {e}"
            )

    # =========================
    # SEND MESSAGE TO CHANNEL
    # =========================

    @commands.command()
    @commands.has_permissions(
        manage_messages=True
    )
    async def msg(
        self,
        ctx,
        channel: discord.TextChannel,
        *,
        message: str
    ):

        try:

            await channel.send(
                message
            )

            await ctx.send(
                f"✅ Sent to {channel.mention}"
            )

        except Exception as e:

            await ctx.send(
                f"❌ Failed: {e}"
            )

    # =========================
    # ANNOUNCE TO ROLE
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def announce(
        self,
        ctx,
        role: discord.Role,
        *,
        message: str
    ):

        success = 0
        failed = 0

        status = await ctx.send(
            f"📢 Sending to {role.name}..."
        )

        for member in role.members:

            if member.bot:
                continue

            try:

                await member.send(
                    message
                )

                success += 1

                await asyncio.sleep(
                    0.75
                )

            except:

                failed += 1

        await status.edit(
            content=
            f"✅ Announcement Complete\n\n"
            f"Delivered: {success}\n"
            f"Failed: {failed}"
        )

    # =========================
    # BROADCAST TO SERVER
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def broadcast(
        self,
        ctx,
        *,
        message: str
    ):

        guild = ctx.guild

        success = 0
        failed = 0

        await ctx.send(
            "📡 Starting broadcast..."
        )

        for member in guild.members:

            if member.bot:
                continue

            try:

                await member.send(
                    message
                )

                success += 1

                await asyncio.sleep(
                    1
                )

            except:

                failed += 1

        await ctx.send(
            f"Broadcast finished.\n"
            f"Delivered: {success}\n"
            f"Failed: {failed}"
        )

    # =========================
    # SET ANNOUNCEMENT CHANNEL
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def setannouncechannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        CUR.execute(
            """
            INSERT INTO settings
            (
                guild_id,
                announcement_channel
            )
            VALUES (?, ?)

            ON CONFLICT(guild_id)
            DO UPDATE SET
            announcement_channel=excluded.announcement_channel
            """,
            (
                ctx.guild.id,
                channel.id
            )
        )

        await ctx.send(
            f"✅ Announcement channel set to {channel.mention}"
        )

    # =========================
    # ANNOUNCE IN SAVED CHANNEL
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def serverannounce(
        self,
        ctx,
        *,
        message: str
    ):

        CUR.execute(
            """
            SELECT announcement_channel
            FROM settings
            WHERE guild_id=?
            """,
            (ctx.guild.id,)
        )

        row = CUR.fetchone()

        if not row:

            await ctx.send(
                "No announcement channel configured."
            )

            return

        if not row["announcement_channel"]:

            await ctx.send(
                "No announcement channel configured."
            )

            return

        channel = ctx.guild.get_channel(
            int(row["announcement_channel"])
        )

        if not channel:

            await ctx.send(
                "Configured channel not found."
            )

            return

        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.gold()
        )

        embed.set_footer(
            text=f"Sent by {ctx.author}"
        )

        await channel.send(
            embed=embed
        )

        await ctx.send(
            "✅ Announcement posted."
        )

    # =========================
    # DM LOGGING
    # =========================

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        if message.author.bot:
            return

        if not isinstance(
            message.channel,
            discord.DMChannel
        ):
            return

        for guild in self.bot.guilds:

            CUR.execute(
                """
                SELECT log_channel
                FROM settings
                WHERE guild_id=?
                """,
                (guild.id,)
            )

            row = CUR.fetchone()

            if not row:
                continue

            if not row["log_channel"]:
                continue

            channel = guild.get_channel(
                int(row["log_channel"])
            )

            if not channel:
                continue

            embed = discord.Embed(
                title="📩 DM RECEIVED",
                color=discord.Color.orange()
            )

            embed.add_field(
                name="User",
                value=f"{message.author} ({message.author.id})",
                inline=False
            )

            embed.add_field(
                name="Message",
                value=message.content[:1000]
                if message.content
                else "[No Text]",
                inline=False
            )

            try:
                await channel.send(
                    embed=embed
                )
            except:
                pass


async def setup(bot):

    await bot.add_cog(
        Announcements(bot)
    )
