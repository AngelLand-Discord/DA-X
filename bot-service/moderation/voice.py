import discord


class VoiceManager:

    @staticmethod
    async def disconnect(member: discord.Member):

        if member.voice is None:
            raise ValueError("Member is not connected to a voice channel.")

        await member.move_to(None)

        return {
            "success": True,
            "action": "VOICE_DISCONNECT",
            "member": member.id,
        }

    @staticmethod
    async def move(
        member: discord.Member,
        channel: discord.VoiceChannel
    ):

        await member.move_to(channel)

        return {
            "success": True,
            "action": "VOICE_MOVE",
            "member": member.id,
            "channel": channel.id,
        }

    @staticmethod
    async def mute(member: discord.Member):

        await member.edit(
            mute=True
        )

        return {
            "success": True,
            "action": "VOICE_MUTE",
            "member": member.id,
        }

    @staticmethod
    async def unmute(member: discord.Member):

        await member.edit(
            mute=False
        )

        return {
            "success": True,
            "action": "VOICE_UNMUTE",
            "member": member.id,
        }

    @staticmethod
    async def deafen(member: discord.Member):

        await member.edit(
            deafen=True
        )

        return {
            "success": True,
            "action": "VOICE_DEAFEN",
            "member": member.id,
        }

    @staticmethod
    async def undeafen(member: discord.Member):

        await member.edit(
            deafen=False
        )

        return {
            "success": True,
            "action": "VOICE_UNDEAFEN",
            "member": member.id,
        }

    @staticmethod
    async def move_all(
        source: discord.VoiceChannel,
        destination: discord.VoiceChannel
    ):

        moved = 0

        for member in source.members:

            await member.move_to(destination)

            moved += 1

        return {
            "success": True,
            "action": "VOICE_MOVE_ALL",
            "moved": moved,
            "from": source.id,
            "to": destination.id,
        }

    @staticmethod
    async def disconnect_all(
        channel: discord.VoiceChannel
    ):

        disconnected = 0

        for member in channel.members:

            await member.move_to(None)

            disconnected += 1

        return {
            "success": True,
            "action": "VOICE_DISCONNECT_ALL",
            "count": disconnected,
            "channel": channel.id,
        }
