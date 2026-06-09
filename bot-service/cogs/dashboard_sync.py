import discord
from discord.ext import commands


class DashboardSync(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        print(
            "Dashboard Sync Loaded"
        )

    @commands.command()
    @commands.is_owner()
    async def guilds(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="DA-X Guilds"
        )

        for guild in self.bot.guilds:

            embed.add_field(
                name=guild.name,
                value=guild.id,
                inline=False
            )

        await ctx.send(
            embed=embed
        )


async def setup(
    bot
):

    await bot.add_cog(
        DashboardSync(bot)
    )
