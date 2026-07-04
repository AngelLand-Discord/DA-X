import discord

from moderation.actions import ModerationManager
from moderation.roles import RoleManager
from moderation.voice import VoiceManager


class ModerationHandler:

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, command, payload):

        command = command.upper()

        guild = self.bot.get_guild(
            int(payload["guild_id"])
        )

        if guild is None:
            raise ValueError("Guild not found.")

        # -----------------------------
        # Members
        # -----------------------------

        if command == "BAN":

            target = guild.get_member(
                int(payload["user_id"])
            )

            if target is None:
                raise ValueError("User not found.")

            return await ModerationManager.ban(
                guild,
                guild.me,
                target,
                reason=payload.get(
                    "reason",
                    "No reason."
                )
            )

        elif command == "KICK":

            target = guild.get_member(
                int(payload["user_id"])
            )

            if target is None:
                raise ValueError("User not found.")

            return await ModerationManager.kick(
                target,
                reason=payload.get(
                    "reason",
                    "No reason."
                )
            )

        elif command == "TIMEOUT":

            target = guild.get_member(
                int(payload["user_id"])
            )

            if target is None:
                raise ValueError("User not found.")

            return await ModerationManager.timeout(
                target,
                payload["duration"],
                reason=payload.get(
                    "reason",
                    "No reason."
                )
            )

        elif command == "UNTIMEOUT":

            target = guild.get_member(
                int(payload["user_id"])
            )

            if target is None:
                raise ValueError("User not found.")

            return await ModerationManager.remove_timeout(
                target
            )

        elif command == "NICKNAME":

            target = guild.get_member(
                int(payload["user_id"])
            )

            if target is None:
                raise ValueError("User not found.")

            return await ModerationManager.nickname(
                target,
                payload["nickname"]
            )

        # -----------------------------
        # Roles
        # -----------------------------

        elif command == "ADD_ROLE":

            member = guild.get_member(
                int(payload["user_id"])
            )

            role = guild.get_role(
                int(payload["role_id"])
            )

            return await RoleManager.add_role(
                member,
                role
            )

        elif command == "REMOVE_ROLE":

            member = guild.get_member(
                int(payload["user_id"])
            )

            role = guild.get_role(
                int(payload["role_id"])
            )

            return await RoleManager.remove_role(
                member,
                role
            )

        # -----------------------------
        # Voice
        # -----------------------------

        elif command == "DISCONNECT":

            member = guild.get_member(
                int(payload["user_id"])
            )

            return await VoiceManager.disconnect(
                member
            )

        elif command == "MOVE":

            member = guild.get_member(
                int(payload["user_id"])
            )

            channel = guild.get_channel(
                int(payload["channel_id"])
            )

            return await VoiceManager.move(
                member,
                channel
            )

        raise ValueError(
            f"Unknown moderation command: {command}"
        )
