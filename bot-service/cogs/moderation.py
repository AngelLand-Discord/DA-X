import discord

from discord.ext import commands


class Moderation(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    @commands.command()
    @commands.has_permissions(
        kick_members=True
    )
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided"
    ):

        await member.kick(
            reason=reason
        )

        await ctx.send(
            f"✅ Kicked {member}"
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
        reason="No reason provided"
    ):

        await member.ban(
            reason=reason
        )

        await ctx.send(
            f"🔨 Banned {member}"
        )


    @commands.command()
    @commands.has_permissions(
        ban_members=True
    )
    async def unban(
        self,
        ctx,
        user_id: int
    ):

        user = await self.bot.fetch_user(
            user_id
        )

        await ctx.guild.unban(
            user
        )

        await ctx.send(
            f"✅ Unbanned {user}"
        )


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
        reason="No reason provided"
    ):

        from datetime import timedelta

        await member.timeout(
            timedelta(
                minutes=minutes
            ),
            reason=reason
        )

        await ctx.send(
            f"⏰ Timed out {member}"
        )


    @commands.command()
    @commands.has_permissions(
        moderate_members=True
    )
    async def untimeout(
        self,
        ctx,
        member: discord.Member
    ):

        await member.timeout(
            None
        )

        await ctx.send(
            f"✅ Removed timeout from {member}"
        )


    @commands.command()
    @commands.has_permissions(
        manage_messages=True
    )
    async def purge(
        self,
        ctx,
        amount: int
    ):

        await ctx.channel.purge(
            limit=amount + 1
        )

        msg = await ctx.send(
            f"🧹 Deleted {amount} messages"
        )

        await msg.delete(
            delay=5
        )


async def setup(
    bot
):

    await bot.add_cog(
        Moderation(bot)
    )
