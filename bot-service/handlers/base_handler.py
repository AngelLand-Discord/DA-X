import os

import discord


DEV_ID = int(os.getenv("DEV_ID", "0"))


class BaseHandler:

    def __init__(self, bot):
        self.bot = bot

    # --------------------------
    # Lookups
    # --------------------------

    def guild(self, guild_id):

        guild = self.bot.get_guild(int(guild_id))

        if guild is None:
            raise ValueError("Guild not found.")

        return guild

    def member(self, guild, member_id):

        member = guild.get_member(int(member_id))

        if member is None:
            raise ValueError("Member not found.")

        return member

    def role(self, guild, role_id):

        role = guild.get_role(int(role_id))

        if role is None:
            raise ValueError("Role not found.")

        return role

    def channel(self, guild, channel_id):

        channel = guild.get_channel(int(channel_id))

        if channel is None:
            raise ValueError("Channel not found.")

        return channel

    # --------------------------
    # Permissions
    # --------------------------

    def require_dev(self, user_id):

        if int(user_id) != DEV_ID:
            raise PermissionError(
                "Only the developer can use this command."
            )

    # --------------------------
    # Response Helpers
    # --------------------------

    def success(self, **kwargs):

        data = {
            "success": True
        }

        data.update(kwargs)

        return data

    def failure(self, message):

        return {
            "success": False,
            "error": str(message)
        }

    # --------------------------
    # Logging
    # --------------------------

    def log(self, *args):

        print("[Handler]", *args)
