import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database.database import (
    initialize_database,
    get_tempbans,
    remove_tempban
)

# =========================
# ENVIRONMENT
# =========================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing.")

PREFIX = os.getenv("BOT_PREFIX", "a ")

OWNER_ID = int(
    os.getenv(
        "OWNER_ID",
        "1023468164304097381"
    )
)

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.guilds = True
intents.dm_messages = True

# =========================
# BOT
# =========================

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

bot.owner_id = OWNER_ID

# =========================
# TEMPBAN RESTORATION
# =========================

async def schedule_unban(user_id, unban_time):

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    delay = (
        datetime.fromisoformat(unban_time)
        - now
    ).total_seconds()

    if delay < 0:
        delay = 0

    await asyncio.sleep(delay)

    for guild in bot.guilds:

        try:
            await guild.unban(
                discord.Object(id=user_id),
                reason="Temporary ban expired"
            )

        except Exception:
            pass

    remove_tempban(user_id)

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"Logged in as {bot.user}")
    print(f"Guilds: {len(bot.guilds)}")
    print("=" * 50)

    try:
        synced = await bot.tree.sync()

        print(
            f"Synced {len(synced)} slash commands."
        )

    except Exception as e:
        print(
            f"Slash sync failed: {e}"
        )

    for row in get_tempbans():

        asyncio.create_task(
            schedule_unban(
                row["user_id"],
                row["unban_time"]
            )
        )


@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    if isinstance(
        error,
        commands.MissingPermissions
    ):
        await ctx.send(
            "You don't have permission to use that command."
        )
        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        await ctx.send(
            "Missing required arguments."
        )
        return

    print(error)


# =========================
# LOAD COGS
# =========================

COGS = [
    "cogs.moderation",
    "cogs.automod",
    "cogs.tickets",
    "cogs.announcements",
    "cogs.permissions",
    "cogs.logging",
    "cogs.dashboard_sync",
]


async def load_cogs():

    for cog in COGS:

        try:

            await bot.load_extension(cog)

            print(
                f"Loaded: {cog}"
            )

        except Exception as e:

            print(
                f"Failed to load {cog}"
            )

            print(e)


# =========================
# STARTUP
# =========================

async def main():

    initialize_database()

    async with bot:

        await load_cogs()

        await bot.start(TOKEN)


def start_bot():

    asyncio.run(main())


if __name__ == "__main__":

    start_bot()
