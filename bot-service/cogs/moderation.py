from datetime import timedelta

import discord
from discord.ext import commands

from database.database import (
    add_warning,
    log_action,
)

from moderation.actions import ModerationManager


class Moderation(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    async def confirm(self, ctx, message):

        await ctx.send(
            message,
            allowed_mentions=discord.AllowedMentions.none()
        )

    # --------------------------------------------------
    # WARN
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def warn(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided."
    ):

        add_warning(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            reason
        )

        await self.confirm(
            ctx,
            f"⚠ Warned **{member}**."
        )

    # --------------------------------------------------
    # KICK
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        kick_members=True
    )
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided."
    ):

        await ModerationManager.kick(
            member,
            reason=reason
        )

        log_action(
            ctx.guild.id,
            "KICK",
            member.id,
            ctx.author.id,
            reason
        )

        await self.confirm(
            ctx,
            f"👢 Kicked **{member}**."
        )

    # --------------------------------------------------
    # BAN
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided."
    ):

        await ModerationManager.ban(
            ctx.guild,
            ctx.author,
            member,
            reason=reason
        )

        log_action(
            ctx.guild.id,
            "BAN",
            member.id,
            ctx.author.id,
            reason
        )

        await self.confirm(
            ctx,
            f"🔨 Banned **{member}**."
        )

    # --------------------------------------------------
    # UNBAN
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def unban(
        self,
        ctx,
        user_id: int,
        *,
        reason="No reason provided."
    ):

        user = await self.bot.fetch_user(
            user_id
        )

        await ModerationManager.unban(
            ctx.guild,
            user,
            reason=reason
        )

        log_action(
            ctx.guild.id,
            "UNBAN",
            user_id,
            ctx.author.id,
            reason
        )

        await self.confirm(
            ctx,
            f"✅ Unbanned **{user}**."
        )

    # --------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def timeout(
        self,
        ctx,
        member: discord.Member,
        minutes: int,
        *,
        reason="No reason provided."
    ):

        if minutes < 1 or minutes > 40320:

            await ctx.send(
                "Timeout must be between **1** and **40320** minutes."
            )

            return

        await ModerationManager.timeout(
            member,
            timedelta(minutes=minutes),
            reason=reason
        )

        log_action(
            ctx.guild.id,
            "TIMEOUT",
            member.id,
            ctx.author.id,
            f"{minutes}m | {reason}"
        )

        await self.confirm(
            ctx,
            f"⏳ Timed out **{member}** for **{minutes} minutes**."
        )

    # --------------------------------------------------
    # UNTIMEOUT
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def untimeout(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided."
    ):

        await ModerationManager.remove_timeout(
            member
        )

        log_action(
            ctx.guild.id,
            "UNTIMEOUT",
            member.id,
            ctx.author.id,
            reason
        )

        await self.confirm(
            ctx,
            f"✅ Removed timeout from **{member}**."
        )

    # --------------------------------------------------
    # PURGE
    # --------------------------------------------------

    @commands.command()
    @commands.has_permissions(
        manage_messages=True
    )
    async def purge(
        self,
        ctx,
        amount: int
    ):

        if amount < 1 or amount > 100:

            await ctx.send(
                "Purge amount must be between **1** and **100**."
            )

            return

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

        log_action(
            ctx.guild.id,
            "PURGE",
            ctx.channel.id,
            ctx.author.id,
            f"{len(deleted)-1} messages"
        )

        msg = await ctx.send(
            f"🗑 Deleted **{len(deleted)-1}** messages."
        )

        await msg.delete(
            delay=5
        )


async def setup(bot):

    await bot.add_cog(
        Moderation(bot)
    )
