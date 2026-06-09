from datetime import timedelta

import discord
from discord.ext import commands

from database.database import add_warning, log_action


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def confirm(self, ctx, message):
        await ctx.send(message, allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        await self.confirm(ctx, f"Warned {member} for: {reason}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        log_action(ctx.guild.id, "KICK", member.id, ctx.author.id, reason)
        await self.confirm(ctx, f"Kicked {member}.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        log_action(ctx.guild.id, "BAN", member.id, ctx.author.id, reason)
        await self.confirm(ctx, f"Banned {member}.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No reason provided"):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(discord.Object(id=user_id), reason=reason)
        log_action(ctx.guild.id, "UNBAN", user_id, ctx.author.id, reason)
        await self.confirm(ctx, f"Unbanned {user}.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        if minutes < 1 or minutes > 40320:
            await ctx.send("Timeout minutes must be between 1 and 40320.")
            return
        await member.timeout(timedelta(minutes=minutes), reason=reason)
        log_action(ctx.guild.id, "TIMEOUT", member.id, ctx.author.id, f"{minutes}m: {reason}")
        await self.confirm(ctx, f"Timed out {member} for {minutes} minutes.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.timeout(None, reason=reason)
        log_action(ctx.guild.id, "UNTIMEOUT", member.id, ctx.author.id, reason)
        await self.confirm(ctx, f"Removed timeout from {member}.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            await ctx.send("Purge amount must be between 1 and 100.")
            return
        deleted = await ctx.channel.purge(limit=amount + 1)
        log_action(ctx.guild.id, "PURGE", ctx.channel.id, ctx.author.id, f"Deleted {max(len(deleted) - 1, 0)} messages")
        msg = await ctx.send(f"Deleted {max(len(deleted) - 1, 0)} messages.")
        await msg.delete(delay=5)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
