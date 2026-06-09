import re
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from discord.ext import commands

from database.database import get_automod_rules, log_action

INVITE_RE = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_times = defaultdict(lambda: deque(maxlen=8))

    def split_config(self, config):
        return [item.strip().lower() for item in (config or "").replace("\n", ",").split(",") if item.strip()]

    def int_config(self, value, default):
        try:
            return int(value or default)
        except (TypeError, ValueError):
            return default

    async def punish(self, message, reason):
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await message.channel.send(
                f"{message.author.mention} {reason}",
                delete_after=8,
                allowed_mentions=None,
            )
        except Exception:
            pass
        log_action(message.guild.id, "AUTOMOD", message.author.id, self.bot.user.id, reason)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        rules = get_automod_rules(message.guild.id)
        if not rules:
            return

        content = message.content or ""
        lower = content.lower()

        bad_words = self.split_config(rules.get("bad_words"))
        if bad_words and any(word in lower for word in bad_words):
            await self.punish(message, "your message was removed for blocked language.")
            return

        if "invite_links" in rules and INVITE_RE.search(content):
            await self.punish(message, "Discord invite links are blocked here.")
            return

        if "caps_spam" in rules:
            letters = [char for char in content if char.isalpha()]
            uppercase = [char for char in letters if char.isupper()]
            threshold = self.int_config(rules["caps_spam"], 70)
            if len(letters) >= 12 and (len(uppercase) / len(letters)) * 100 >= threshold:
                await self.punish(message, "please avoid caps spam.")
                return

        if "mass_mentions" in rules:
            limit = self.int_config(rules["mass_mentions"], 5)
            if len(message.mentions) + len(message.role_mentions) >= limit:
                await self.punish(message, "mass mentions are blocked.")
                return

        if "spam" in rules:
            limit = self.int_config(rules["spam"], 5)
            key = (message.guild.id, message.author.id)
            now = datetime.now(timezone.utc)
            self.message_times[key].append(now)
            recent = [stamp for stamp in self.message_times[key] if now - stamp <= timedelta(seconds=8)]
            if len(recent) >= limit:
                await self.punish(message, "please slow down.")


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
