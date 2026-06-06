import discord

from discord.ext import commands


class Tickets(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    @commands.command()
    async def ticket(
        self,
        ctx
    ):

        category = discord.utils.get(
            ctx.guild.categories,
            name="Tickets"
        )

        if category is None:

            category = await ctx.guild.create_category(
                "Tickets"
            )

        channel = await ctx.guild.create_text_channel(
            name=f"ticket-{ctx.author.name}",
            category=category
        )

        await channel.set_permissions(
            ctx.guild.default_role,
            view_channel=False
        )

        await channel.set_permissions(
            ctx.author,
            view_channel=True,
            send_messages=True
        )

        await channel.send(

            f"{ctx.author.mention}\n"

            "Support ticket created."

        )

        await ctx.send(

            f"✅ Ticket created: {channel.mention}"

        )


    @commands.command()
    async def close(
        self,
        ctx
    ):

        if not ctx.channel.name.startswith(
            "ticket-"
        ):

            return

        await ctx.send(

            "🔒 Closing ticket in 5 seconds..."

        )

        await ctx.channel.delete(
            delay=5
        )


async def setup(
    bot
):

    await bot.add_cog(
        Tickets(bot)
    )
