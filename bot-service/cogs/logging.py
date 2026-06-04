import discord
from discord.ext import commands

from database.database import CUR


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # GET LOG CHANNEL
    # =========================

    def get_log_channel(self, guild):

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
            return None

        return guild.get_channel(
            row["log_channel"]
        )

    # =========================
    # SET LOG CHANNEL
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def setlogchannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        CUR.execute(
            """
            INSERT INTO settings
            (
                guild_id,
                log_channel
            )
            VALUES (?, ?)

            ON CONFLICT(guild_id)
            DO UPDATE SET
            log_channel=excluded.log_channel
            """,
            (
                ctx.guild.id,
                channel.id
            )
        )

        await ctx.send(
            f"✅ Log channel set to {channel.mention}"
        )

    # =========================
    # MEMBER JOIN
    # =========================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        channel = self.get_log_channel(
            member.guild
        )

        if not channel:
            return

        embed = discord.Embed(
            title="📥 Member Joined",
            color=discord.Color.green()
        )

        embed.add_field(
            name="User",
            value=f"{member} ({member.id})",
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await channel.send(
            embed=embed
        )

    # =========================
    # MEMBER LEAVE
    # =========================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):

        channel = self.get_log_channel(
            member.guild
        )

        if not channel:
            return

        embed = discord.Embed(
            title="📤 Member Left",
            color=discord.Color.red()
        )

        embed.add_field(
            name="User",
            value=f"{member} ({member.id})",
            inline=False
        )

        await channel.send(
            embed=embed
        )

    # =========================
    # MESSAGE DELETE
    # =========================

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message
    ):

        if message.author.bot:
            return

        if not message.guild:
            return

        channel = self.get_log_channel(
            message.guild
        )

        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Author",
            value=f"{message.author} ({message.author.id})",
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Content",
            value=message.content[:1000]
            if message.content
            else "[No Content]",
            inline=False
        )

        await channel.send(
            embed=embed
        )

    # =========================
    # MESSAGE EDIT
    # =========================

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before,
        after
    ):

        if before.author.bot:
            return

        if not before.guild:
            return

        if before.content == after.content:
            return

        channel = self.get_log_channel(
            before.guild
        )

        if not channel:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Author",
            value=f"{before.author} ({before.author.id})",
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Before",
            value=before.content[:1000]
            if before.content
            else "[Empty]",
            inline=False
        )

        embed.add_field(
            name="After",
            value=after.content[:1000]
            if after.content
            else "[Empty]",
            inline=False
        )

        await channel.send(
            embed=embed
        )

    # =========================
    # ROLE CHANGES
    # =========================

    @commands.Cog.listener()
    async def on_member_update(
        self,
        before,
        after
    ):

        if before.roles == after.roles:
            return

        channel = self.get_log_channel(
            after.guild
        )

        if not channel:
            return

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        gained = after_roles - before_roles
        lost = before_roles - after_roles

        embed = discord.Embed(
            title="🎭 Role Update",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="User",
            value=f"{after} ({after.id})",
            inline=False
        )

        if gained:

            embed.add_field(
                name="Added",
                value="\n".join(
                    role.name
                    for role in gained
                )[:1000],
                inline=False
            )

        if lost:

            embed.add_field(
                name="Removed",
                value="\n".join(
                    role.name
                    for role in lost
                )[:1000],
                inline=False
            )

        await channel.send(
            embed=embed
        )

    # =========================
    # CHANNEL CREATE
    # =========================

    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        created_channel
    ):

        channel = self.get_log_channel(
            created_channel.guild
        )

        if not channel:
            return

        embed = discord.Embed(
            title="📁 Channel Created",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Channel",
            value=created_channel.name,
            inline=False
        )

        await channel.send(
            embed=embed
        )

    # =========================
    # CHANNEL DELETE
    # =========================

    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        deleted_channel
    ):

        channel = self.get_log_channel(
            deleted_channel.guild
        )

        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ Channel Deleted",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Channel",
            value=deleted_channel.name,
            inline=False
        )

        await channel.send(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        Logging(bot)
    )