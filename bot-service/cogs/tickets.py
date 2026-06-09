import discord
from discord.ext import commands

from database.database import (
    add_ticket_message,
    create_ticket,
    get_open_ticket_for_user,
    set_ticket_status,
)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def ticket_id_from_topic(self, channel):
        topic = channel.topic or ""
        if topic.startswith("DA-X Ticket #"):
            value = topic.replace("DA-X Ticket #", "").split()[0]
            if value.isdigit():
                return int(value)
        return None

    @commands.command()
    async def ticket(self, ctx, *, subject="Support Ticket"):
        existing = get_open_ticket_for_user(ctx.guild.id, ctx.author.id)
        if existing:
            await ctx.send(f"You already have an open ticket: #{existing['id']}.")
            return

        ticket_id = create_ticket(ctx.guild.id, ctx.author.id, str(ctx.author), subject, "Ticket opened from Discord.")
        category = discord.utils.get(ctx.guild.categories, name="Tickets")
        if category is None:
            category = await ctx.guild.create_category("Tickets")

        channel = await ctx.guild.create_text_channel(
            name=f"ticket-{ticket_id}",
            category=category,
            topic=f"DA-X Ticket #{ticket_id}",
        )
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await channel.set_permissions(ctx.author, view_channel=True, send_messages=True, read_message_history=True)

        for role in ctx.guild.roles:
            if role.permissions.manage_messages or role.permissions.moderate_members:
                try:
                    await channel.set_permissions(role, view_channel=True, send_messages=True, read_message_history=True)
                except Exception:
                    pass

        await channel.send(f"{ctx.author.mention} support ticket #{ticket_id} created.\nSubject: {subject}")
        await ctx.send(f"Ticket created: {channel.mention}")

    @commands.command()
    async def close(self, ctx):
        ticket_id = self.ticket_id_from_topic(ctx.channel)
        if not ticket_id:
            await ctx.send("This command can only be used in a DA-X ticket channel.")
            return
        set_ticket_status(ticket_id, ctx.guild.id, "Closed")
        await ctx.send("Closing ticket in 5 seconds...")
        await ctx.channel.delete(delay=5)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        ticket_id = self.ticket_id_from_topic(message.channel)
        if not ticket_id:
            return
        add_ticket_message(ticket_id, message.guild.id, message.author.id, str(message.author), message.content or "[attachment/embed]")


async def setup(bot):
    await bot.add_cog(Tickets(bot))
