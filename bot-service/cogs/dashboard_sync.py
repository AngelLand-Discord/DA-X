import sqlite3
from pathlib import Path

import discord
from discord.ext import commands, tasks

DB_PATH = Path(__file__).resolve().parents[1] / "bot.db"


class DashboardSync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sync_status.start()

    def cog_unload(self):
        self.sync_status.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Dashboard Sync Loaded")

    @tasks.loop(seconds=30)
    async def sync_status(self):

        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        cur = db.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_status(
                id INTEGER PRIMARY KEY,
                online INTEGER NOT NULL,
                latency REAL NOT NULL,
                guilds INTEGER NOT NULL,
                users INTEGER NOT NULL,
                uptime TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )

        guild_count = len(self.bot.guilds)

        user_count = sum(
            guild.member_count or 0
            for guild in self.bot.guilds
        )

        latency = round(self.bot.latency * 1000, 2)

        cur.execute(
            """
            INSERT INTO bot_status
            (
                id,
                online,
                latency,
                guilds,
                users,
                uptime,
                updated_at
            )
            VALUES
            (
                1,
                1,
                ?,
                ?,
                ?,
                datetime('now'),
                datetime('now')
            )
            ON CONFLICT(id)
            DO UPDATE SET
                online=excluded.online,
                latency=excluded.latency,
                guilds=excluded.guilds,
                users=excluded.users,
                updated_at=datetime('now')
            """,
            (
                latency,
                guild_count,
                user_count,
            ),
        )

        db.commit()
        db.close()

    @sync_status.before_loop
    async def before_sync(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):

        embed = discord.Embed(
            title="DA-X Guilds",
            colour=discord.Colour.blurple()
        )

        for guild in self.bot.guilds:

            embed.add_field(
                name=guild.name,
                value=(
                    f"ID: `{guild.id}`\n"
                    f"Members: `{guild.member_count}`"
                ),
                inline=False,
            )

        embed.set_footer(
            text=f"{len(self.bot.guilds)} guild(s)"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DashboardSync(bot))
