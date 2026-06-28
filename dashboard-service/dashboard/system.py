from dashboard.queue import add_command


class SystemManager:

    @staticmethod
    def announce(
        guild_id,
        user_id,
        channel_id,
        message
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "ANNOUNCE",
            {
                "channel_id": channel_id,
                "message": message
            }
        )

    @staticmethod
    def say(
        guild_id,
        user_id,
        channel_id,
        message
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "SAY",
            {
                "channel_id": channel_id,
                "message": message
            }
        )

    @staticmethod
    def embed(
        guild_id,
        user_id,
        channel_id,
        title,
        description,
        colour="#5865F2"
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "EMBED",
            {
                "channel_id": channel_id,
                "title": title,
                "description": description,
                "colour": colour
            }
        )

    @staticmethod
    def dm(
        guild_id,
        user_id,
        target_id,
        message
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "DM",
            {
                "target_id": target_id,
                "message": message
            }
        )

    @staticmethod
    def purge(
        guild_id,
        user_id,
        channel_id,
        amount
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "PURGE",
            {
                "channel_id": channel_id,
                "amount": amount
            }
        )

    @staticmethod
    def slowmode(
        guild_id,
        user_id,
        channel_id,
        seconds
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "SLOWMODE",
            {
                "channel_id": channel_id,
                "seconds": seconds
            }
        )

    @staticmethod
    def nickname(
        guild_id,
        user_id,
        member_id,
        nickname
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "NICKNAME",
            {
                "member_id": member_id,
                "nickname": nickname
            }
        )

    @staticmethod
    def lockdown(
        guild_id,
        user_id,
        channel_id
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "LOCKDOWN",
            {
                "channel_id": channel_id
            }
        )

    @staticmethod
    def unlock(
        guild_id,
        user_id,
        channel_id
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "UNLOCK",
            {
                "channel_id": channel_id
            }
        )

    @staticmethod
    def create_role(
        guild_id,
        user_id,
        name,
        colour="#5865F2",
        hoist=False,
        mentionable=False
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "CREATE_ROLE",
            {
                "name": name,
                "colour": colour,
                "hoist": hoist,
                "mentionable": mentionable
            }
        )

    @staticmethod
    def delete_role(
        guild_id,
        user_id,
        role_id
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "DELETE_ROLE",
            {
                "role_id": role_id
            }
        )

    @staticmethod
    def create_channel(
        guild_id,
        user_id,
        name,
        channel_type="text"
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "CREATE_CHANNEL",
            {
                "name": name,
                "type": channel_type
            }
        )

    @staticmethod
    def delete_channel(
        guild_id,
        user_id,
        channel_id
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "DELETE_CHANNEL",
            {
                "channel_id": channel_id
            }
        )

    @staticmethod
    def rename_channel(
        guild_id,
        user_id,
        channel_id,
        name
    ):

        return add_command(
            guild_id,
            user_id,
            "SYSTEM",
            "RENAME_CHANNEL",
            {
                "channel_id": channel_id,
                "name": name
            }
        )
