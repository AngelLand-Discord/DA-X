import discord


class RoleManager:

    @staticmethod
    async def add_role(member: discord.Member, role: discord.Role):

        await member.add_roles(role)

        return {
            "success": True,
            "action": "ADD_ROLE",
            "member": member.id,
            "role": role.id,
        }

    @staticmethod
    async def remove_role(member: discord.Member, role: discord.Role):

        await member.remove_roles(role)

        return {
            "success": True,
            "action": "REMOVE_ROLE",
            "member": member.id,
            "role": role.id,
        }

    @staticmethod
    async def create_role(
        guild: discord.Guild,
        *,
        name: str,
        colour: str = "#5865F2",
        hoist=False,
        mentionable=False,
    ):

        colour = discord.Colour.from_str(colour)

        role = await guild.create_role(
            name=name,
            colour=colour,
            hoist=hoist,
            mentionable=mentionable,
        )

        return {
            "success": True,
            "action": "CREATE_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def delete_role(role: discord.Role):

        await role.delete()

        return {
            "success": True,
            "action": "DELETE_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def rename_role(
        role: discord.Role,
        name: str,
    ):

        await role.edit(
            name=name
        )

        return {
            "success": True,
            "action": "RENAME_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def recolour_role(
        role: discord.Role,
        colour: str,
    ):

        await role.edit(
            colour=discord.Colour.from_str(colour)
        )

        return {
            "success": True,
            "action": "RECOLOUR_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def move_role(
        role: discord.Role,
        position: int,
    ):

        await role.edit(
            position=position
        )

        return {
            "success": True,
            "action": "MOVE_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def hoist_role(
        role: discord.Role,
        value: bool,
    ):

        await role.edit(
            hoist=value
        )

        return {
            "success": True,
            "action": "HOIST_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def mentionable_role(
        role: discord.Role,
        value: bool,
    ):

        await role.edit(
            mentionable=value
        )

        return {
            "success": True,
            "action": "MENTIONABLE_ROLE",
            "role": role.id,
        }

    @staticmethod
    async def permissions_role(
        role: discord.Role,
        permissions: discord.Permissions,
    ):

        await role.edit(
            permissions=permissions
        )

        return {
            "success": True,
            "action": "PERMISSIONS_ROLE",
            "role": role.id,
        }
