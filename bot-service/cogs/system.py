import discord
from discord.ext import commands


class System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="announce")
    @commands.has_permissions(administrator=True)
    async def announce(
        self,
        ctx,
        channel: discord.TextChannel,
        *,
        message
    ):

        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            colour=discord.Colour.blurple()
        )

        embed.set_footer(
            text=f"Sent by {ctx.author}"
        )

        await channel.send(embed=embed)

        await ctx.send("✅ Announcement sent.")

    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def say(
        self,
        ctx,
        channel: discord.TextChannel,
        *,
        message
    ):

        await channel.send(message)

        await ctx.message.delete()

    @commands.command(name="embed")
    @commands.has_permissions(administrator=True)
    async def embed(
        self,
        ctx,
        channel: discord.TextChannel,
        title,
        *,
        description
    ):

        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Colour.blurple()
        )

        embed.set_footer(
            text=f"Created by {ctx.author}"
        )

        await channel.send(embed=embed)

        await ctx.send(
            "✅ Embed sent."
        )

    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self,
        ctx,
        amount: int
    ):

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

        await ctx.send(
            f"🗑 Deleted {len(deleted)-1} messages.",
            delete_after=5
        )

    @commands.command(name="lockdown")
    @commands.has_permissions(manage_channels=True)
    async def lockdown(
        self,
        ctx,
        channel: discord.TextChannel = None
    ):

        channel = channel or ctx.channel

        overwrite = channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = False

        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            f"🔒 {channel.mention} locked."
        )

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(
        self,
        ctx,
        channel: discord.TextChannel = None
    ):

        channel = channel or ctx.channel

        overwrite = channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = None

        await channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            f"🔓 {channel.mention} unlocked."
        )

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx,
        seconds: int
    ):

        await ctx.channel.edit(
            slowmode_delay=seconds
        )

        await ctx.send(
            f"🐢 Slowmode set to {seconds} seconds."
        )


async def setup(bot):

    await bot.add_cog(
        System(bot)
    )
