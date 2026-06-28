from discord import Member
from discord.ext import commands


class ModerationManager:

    @staticmethod
    async def ban(
        guild,
        moderator: Member,
        target: Member,
        *,
        reason="No reason provided.",
        delete_days=0
    ):

        await guild.ban(
            target,
            reason=reason,
            delete_message_days=delete_days
        )

        return {
            "success": True,
            "action": "BAN",
            "target": target.id,
            "moderator": moderator.id,
            "reason": reason
        }

    @staticmethod
    async def unban(
        guild,
        user,
        *,
        reason="No reason provided."
    ):

        await guild.unban(
            user,
            reason=reason
        )

        return {
            "success": True,
            "action": "UNBAN",
            "target": user.id,
            "reason": reason
        }

    @staticmethod
    async def kick(
        target: Member,
        *,
        reason="No reason provided."
    ):

        await target.kick(
            reason=reason
        )

        return {
            "success": True,
            "action": "KICK",
            "target": target.id,
            "reason": reason
        }

    @staticmethod
    async def timeout(
        target: Member,
        duration,
        *,
        reason="No reason provided."
    ):

        await target.timeout(
            duration,
            reason=reason
        )

        return {
            "success": True,
            "action": "TIMEOUT",
            "target": target.id,
            "reason": reason
        }

    @staticmethod
    async def remove_timeout(
        target: Member
    ):

        await target.timeout(
            None
        )

        return {
            "success": True,
            "action": "UNTIMEOUT",
            "target": target.id
        }

    @staticmethod
    async def warn(
        database,
        guild_id,
        moderator_id,
        target_id,
        reason
    ):

        database.execute(
            """
            INSERT INTO warnings
            (
                guild_id,
                user_id,
                moderator_id,
                reason,
                created_at
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                CURRENT_TIMESTAMP
            )
            """,
            (
                guild_id,
                target_id,
                moderator_id,
                reason
            )
        )

        database.commit()

        return {
            "success": True,
            "action": "WARN",
            "target": target_id,
            "reason": reason
        }

    @staticmethod
    async def purge(
        channel,
        amount
    ):

        deleted = await channel.purge(
            limit=amount
        )

        return {
            "success": True,
            "action": "PURGE",
            "deleted": len(deleted)
        }

    @staticmethod
    async def nickname(
        target: Member,
        nickname
    ):

        await target.edit(
            nick=nickname
        )

        return {
            "success": True,
            "action": "NICKNAME",
            "target": target.id
        }
