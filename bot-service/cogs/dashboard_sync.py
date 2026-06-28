import discord
from discord.ext import commands, tasks
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "bot.db"


class DashboardSync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sync_status.start()

    def cog_unload(self):
        self.sync_status.cancel()

    @tasks.loop(seconds=30)
    async def sync_status(self):
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS bot_status(
                id INTEGER PRIMARY KEY,
                online INTEGER,
                latency REAL,
                guilds INTEGER,
                users INTEGER,
                updated_at TEXT
            )
        """)

        guilds = len(self.bot.guilds)

        users = sum(
            guild.member_count or 0
            for guild in self.bot.guilds
        )

        latency = round(self.bot.latency * 1000, 2)

        cur.execute(
            """
            INSERT OR REPLACE INTO bot_status
            (
                id,
                online,
                latency,
                guilds,
                users,
                updated_at
            )
            VALUES
            (
                1,
                1,
                ?,
                ?,
                ?,
                datetime('now')
            )
            """,
            (
                latency,
                guilds,
                users
            )
        )

        db.commit()
        db.close()

    @sync_status.before_loop
    async def before_sync(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Dashboard Sync Ready")

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
                    f"ID: {guild.id}\n"
                    f"Members: {guild.member_count}"
                ),
                inline=False
            )

        embed.set_footer(
            text=f"Total Guilds: {len(self.bot.guilds)}"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DashboardSync(bot))
