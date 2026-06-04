from datetime import datetime, timezone, timedelta
import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from database.database import (
    CUR,
    log_action,
    save_tempban,
    save_judgement,
    get_judgements,
    clear_judgements,
    add_invite,
    get_mod_history
)

# =========================
# HELPERS
# =========================

def now():
    return datetime.now(timezone.utc)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # LOGGING
    # =========================

    async def send_modlog(
        self,
        guild,
        title,
        target,
        moderator,
        reason,
        duration=None
    ):

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
            return

        channel = guild.get_channel(
            row["log_channel"]
        )

        if not channel:
            return

        embed = discord.Embed(
            title=title,
            color=discord.Color.dark_red(),
            timestamp=now()
        )

        embed.add_field(
            name="Target",
            value=f"{target} (`{target.id}`)",
            inline=False
        )

        embed.add_field(
            name="Moderator",
            value=f"{moderator} (`{moderator.id}`)",
            inline=False
        )

        if duration:
            embed.add_field(
                name="Duration",
                value=duration,
                inline=False
            )

        embed.add_field(
            name="Reason",
            value=reason or "No reason provided",
            inline=False
        )

        await channel.send(embed=embed)

    # =========================
    # JUDGEMENT
    # =========================

    async def judgement_core(
        self,
        guild,
        moderator,
        member,
        reason
    ):

        roles = [
            r
            for r in member.roles
            if r != guild.default_role
        ]

        if not roles:
            return False

        for role in roles:
            save_judgement(
                member.id,
                role.id
            )

        await member.remove_roles(
            *roles,
            reason=reason
        )

        log_action(
            "judgement",
            member.id,
            moderator.id,
            reason
        )

        await self.send_modlog(
            guild,
            "⚖️ JUDGEMENT EXECUTED",
            member,
            moderator,
            reason
        )

        return True

    # =========================
    # PREFIX COMMANDS
    # =========================

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def judgement(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="Judgement passed"
    ):

        success = await self.judgement_core(
            ctx.guild,
            ctx.author,
            member,
            reason
        )

        if success:
            await ctx.send(
                f"⚖️ {member.mention} judged."
            )
        else:
            await ctx.send(
                "User has no roles."
            )

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def restore(
        self,
        ctx,
        member: discord.Member
    ):

        rows = get_judgements(
            member.id
        )

        if not rows:
            await ctx.send(
                "Nothing to restore."
            )
            return

        roles = []

        for row in rows:

            role = ctx.guild.get_role(
                row["role_id"]
            )

            if role:
                roles.append(role)

        if roles:
            await member.add_roles(
                *roles
            )

        clear_judgements(
            member.id
        )

        log_action(
            "restore",
            member.id,
            ctx.author.id,
            "Roles restored"
        )

        await ctx.send(
            f"♻️ Restored roles for {member.mention}"
        )

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def mute(
        self,
        ctx,
        member: discord.Member,
        minutes: int = 10,
        *,
        reason="Muted"
    ):

        until = (
            now()
            + timedelta(minutes=minutes)
        )

        await member.timeout(
            until,
            reason=reason
        )

        log_action(
            "mute",
            member.id,
            ctx.author.id,
            reason
        )

        await self.send_modlog(
            ctx.guild,
            "🔇 USER MUTED",
            member,
            ctx.author,
            reason,
            f"{minutes} minutes"
        )

        await ctx.send(
            f"🔇 {member.mention} muted."
        )

    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def unmute(
        self,
        ctx,
        member: discord.Member
    ):

        await member.timeout(None)

        log_action(
            "unmute",
            member.id,
            ctx.author.id,
            "Manual unmute"
        )

        await ctx.send(
            f"🔊 {member.mention} unmuted."
        )

    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="Banned"
    ):

        await member.ban(
            reason=reason
        )

        log_action(
            "ban",
            member.id,
            ctx.author.id,
            reason
        )

        await ctx.send(
            f"🚫 {member} banned."
        )

    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def unban(
        self,
        ctx,
        user_id: int,
        *,
        reason="Unbanned"
    ):

        user = discord.Object(
            id=user_id
        )

        await ctx.guild.unban(
            user,
            reason=reason
        )

        log_action(
            "unban",
            user_id,
            ctx.author.id,
            reason
        )

        await ctx.send(
            f"✅ User `{user_id}` unbanned."
        )

    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def tempban(
        self,
        ctx,
        member: discord.Member,
        minutes: int,
        *,
        reason="Tempban"
    ):

        until = (
            now()
            + timedelta(minutes=minutes)
        )

        await member.ban(
            reason=reason
        )

        save_tempban(
            member.id,
            until
        )

        log_action(
            "tempban",
            member.id,
            ctx.author.id,
            reason
        )

        await ctx.send(
            f"⏳ {member} tempbanned."
        )

    @commands.command()
    async def userinfo(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        history = get_mod_history(
            member.id
        )

        history_text = "\n".join(
            f"{r['action']} : {r['count']}"
            for r in history
        )

        if not history_text:
            history_text = "Clean record"

        embed = discord.Embed(
            title="User Information",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="User",
            value=f"{member} ({member.id})",
            inline=False
        )

        embed.add_field(
            name="History",
            value=history_text,
            inline=False
        )

        await ctx.send(
            embed=embed
        )

    # =========================
    # INVITE TRACKING
    # =========================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        add_invite(
            member.guild.id,
            member.id
        )

    # =========================
    # SLASH COMMANDS
    # =========================

    @app_commands.command(
        name="ban",
        description="Ban a member"
    )
    async def slash_ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Banned"
    ):

        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "No permission.",
                ephemeral=True
            )
            return

        await member.ban(
            reason=reason
        )

        await interaction.response.send_message(
            f"{member} banned.",
            ephemeral=True
        )

    @app_commands.command(
        name="mute",
        description="Mute a member"
    )
    async def slash_mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: int = 10,
        reason: str = "Muted"
    ):

        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(
                "No permission.",
                ephemeral=True
            )
            return

        until = (
            now()
            + timedelta(minutes=minutes)
        )

        await member.timeout(
            until,
            reason=reason
        )

        await interaction.response.send_message(
            "User muted.",
            ephemeral=True
        )


async def setup(bot):

    await bot.add_cog(
        Moderation(bot)
    )