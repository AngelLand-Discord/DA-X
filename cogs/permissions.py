import discord
from discord.ext import commands


class Permissions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # LOCK CHANNEL
    # =========================

    @commands.command()
    @commands.has_permissions(
        manage_channels=True
    )
    async def lock(
        self,
        ctx,
        channel: discord.TextChannel = None
    ):

        channel = channel or ctx.channel

        try:

            everyone = ctx.guild.default_role

            overwrite = channel.overwrites_for(
                everyone
            )

            overwrite.send_messages = False

            await channel.set_permissions(
                everyone,
                overwrite=overwrite
            )

            await ctx.send(
                f"🔒 {channel.mention} locked."
            )

        except Exception as e:

            await ctx.send(
                f"Failed: {e}"
            )

    # =========================
    # UNLOCK CHANNEL
    # =========================

    @commands.command()
    @commands.has_permissions(
        manage_channels=True
    )
    async def unlock(
        self,
        ctx,
        channel: discord.TextChannel = None
    ):

        channel = channel or ctx.channel

        try:

            everyone = ctx.guild.default_role

            overwrite = channel.overwrites_for(
                everyone
            )

            overwrite.send_messages = None

            await channel.set_permissions(
                everyone,
                overwrite=overwrite
            )

            await ctx.send(
                f"🔓 {channel.mention} unlocked."
            )

        except Exception as e:

            await ctx.send(
                f"Failed: {e}"
            )

    # =========================
    # GIVE ROLE PERMISSION
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def giveperm(
        self,
        ctx,
        role: discord.Role,
        permission: str
    ):

        perms = role.permissions

        if not hasattr(
            perms,
            permission
        ):

            await ctx.send(
                "Invalid permission."
            )

            return

        try:

            setattr(
                perms,
                permission,
                True
            )

            await role.edit(
                permissions=perms
            )

            await ctx.send(
                f"✅ Granted `{permission}` to {role.mention}"
            )

        except Exception as e:

            await ctx.send(
                f"Failed: {e}"
            )

    # =========================
    # REMOVE ROLE PERMISSION
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def remroleperm(
        self,
        ctx,
        role: discord.Role,
        permission: str
    ):

        perms = role.permissions

        if not hasattr(
            perms,
            permission
        ):

            await ctx.send(
                "Invalid permission."
            )

            return

        try:

            setattr(
                perms,
                permission,
                False
            )

            await role.edit(
                permissions=perms
            )

            await ctx.send(
                f"✅ Removed `{permission}` from {role.mention}"
            )

        except Exception as e:

            await ctx.send(
                f"Failed: {e}"
            )

    # =========================
    # REMOVE PERMISSION FROM ALL ROLES
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def remallperm(
        self,
        ctx,
        permission: str
    ):

        updated = 0

        for role in ctx.guild.roles:

            if role.is_default():
                continue

            perms = role.permissions

            if not hasattr(
                perms,
                permission
            ):
                continue

            if getattr(
                perms,
                permission
            ):

                try:

                    setattr(
                        perms,
                        permission,
                        False
                    )

                    await role.edit(
                        permissions=perms
                    )

                    updated += 1

                except:
                    pass

        await ctx.send(
            f"✅ Removed `{permission}` from {updated} roles."
        )

    # =========================
    # DENY PERMISSION TO MEMBER
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def removeperm(
        self,
        ctx,
        member: discord.Member,
        permission: str
    ):

        guild = ctx.guild

        if not hasattr(
            discord.Permissions,
            permission
        ):

            await ctx.send(
                "Invalid permission."
            )

            return

        role_name = (
            f"deny_{permission}"
        )

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )

        try:

            if role is None:

                role = await guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions.none(),
                    reason="Permission override role"
                )

            for channel in guild.channels:

                try:

                    overwrite = (
                        channel.overwrites_for(role)
                    )

                    setattr(
                        overwrite,
                        permission,
                        False
                    )

                    await channel.set_permissions(
                        role,
                        overwrite=overwrite
                    )

                except:
                    pass

            await member.add_roles(
                role
            )

            await ctx.send(
                f"🚫 {member.mention} denied `{permission}`."
            )

        except Exception as e:

            await ctx.send(
                f"Failed: {e}"
            )

    # =========================
    # RESTORE MEMBER PERMISSION
    # =========================

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def restoreperm(
        self,
        ctx,
        member: discord.Member,
        permission: str
    ):

        guild = ctx.guild

        role_name = (
            f"deny_{permission}"
        )

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )

        if role is None:

            await ctx.send(
                "No deny role found."
            )

            return

        try:

            if role in member.roles:

                await member.remove_roles(
                    role
                )

            for channel in guild.channels:

                try:

                    overwrite = (
                        channel.overwrites_for(role)
                    )

                    setattr(
                        overwrite,
                        permission,
                        None
                    )

                    await channel.set_permissions(
                        role,
                        overwrite=overwrite
                    )

                except:
                    pass

            if len(role.members) == 0:

                await role.delete(
                    reason="Unused deny role"
                )

            await ctx.send(
                f"✅ Restored `{permission}` for {member.mention}"
            )

        except Exception as e:

            await ctx.send(
                f"Failed: {e}"
            )

    # =========================
    # LIST VALID PERMISSIONS
    # =========================

    @commands.command()
    async def permissionslist(
        self,
        ctx
    ):

        perms = []

        for perm in discord.Permissions.VALID_FLAGS:

            perms.append(
                f"`{perm}`"
            )

        chunks = []

        current = ""

        for perm in perms:

            if len(current) + len(perm) > 1800:

                chunks.append(
                    current
                )

                current = ""

            current += perm + "\n"

        chunks.append(
            current
        )

        for chunk in chunks:

            await ctx.send(
                chunk
            )


async def setup(bot):

    await bot.add_cog(
        Permissions(bot)
    )