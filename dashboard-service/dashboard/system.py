from .queue import Queue


class SystemService:

    @staticmethod
    def announce(
        guild_id,
        channel_id,
        message,
        footer=None,
        thumbnail=None,
        image=None,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "ANNOUNCE",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "message": message,

                "footer": footer,

                "thumbnail": thumbnail,

                "image": image,

            },

        )

    @staticmethod
    def say(
        guild_id,
        channel_id,
        message,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "SAY",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "message": message,

            },

        )

    @staticmethod
    def embed(
        guild_id,
        channel_id,
        title,
        description,
        colour="#5865F2",
        footer=None,
        thumbnail=None,
        image=None,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "EMBED",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "title": title,

                "description": description,

                "colour": colour,

                "footer": footer,

                "thumbnail": thumbnail,

                "image": image,

            },

        )

    @staticmethod
    def lockdown(
        guild_id,
        channel_id,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "LOCKDOWN",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

            },

        )

    @staticmethod
    def unlock(
        guild_id,
        channel_id,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "UNLOCK",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

            },

        )

    @staticmethod
    def slowmode(
        guild_id,
        channel_id,
        seconds,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "SLOWMODE",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "seconds": seconds,

            },

        )

    @staticmethod
    def purge(
        guild_id,
        channel_id,
        amount,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "PURGE",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "amount": amount,

            },

        )
