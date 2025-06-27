import discord
from discord.ext import commands
from discord import app_commands

MOD_LOG_CHANNEL_NAME = "mod-logs"

def is_mod():
    def predicate(interaction: discord.Interaction):
        perms = interaction.user.guild_permissions
        return perms.kick_members or perms.ban_members or perms.manage_messages
    return app_commands.check(predicate)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild: discord.Guild, message: str):
        log_channel = discord.utils.get(guild.text_channels, name=MOD_LOG_CHANNEL_NAME)
        if log_channel:
            await log_channel.send(message)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @is_mod()
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await user.ban(reason=reason)
        await interaction.response.send_message(f"{user.mention} has been banned. Reason: {reason}")
        await self.send_log(interaction.guild, f"🔨 {user.mention} was **banned** by {interaction.user.mention}. Reason: {reason}")

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @is_mod()
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        await user.kick(reason=reason)
        await interaction.response.send_message(f"{user.mention} has been kicked. Reason: {reason}")
        await self.send_log(interaction.guild, f"🥾 {user.mention} was **kicked** by {interaction.user.mention}. Reason: {reason}")

    @app_commands.command(name="purge", description="Delete messages.")
    @is_mod()
    async def purge(self, interaction: discord.Interaction, amount: int):
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
        await self.send_log(interaction.guild, f"🧹 {interaction.user.mention} purged {len(deleted)} messages in {interaction.channel.mention}.")

    @app_commands.command(name="role_add", description="Add a role to a user.")
    @is_mod()
    async def role_add(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        await user.add_roles(role)
        await interaction.response.send_message(f"✅ Added {role.name} to {user.mention}")
        await self.send_log(interaction.guild, f"🛡️ {interaction.user.mention} gave {role.name} to {user.mention}")

    @app_commands.command(name="role_remove", description="Remove a role from a user.")
    @is_mod()
    async def role_remove(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        await user.remove_roles(role)
        await interaction.response.send_message(f"❌ Removed {role.name} from {user.mention}")
        await self.send_log(interaction.guild, f"🗑️ {interaction.user.mention} removed {role.name} from {user.mention}")

    @app_commands.command(name="embed", description="Create a custom embed message.")
    @is_mod()
    async def embed(self, interaction: discord.Interaction, title: str, description: str, color: str = "0x2f3136", image_url: str = None, field_name: str = None, field_value: str = None):
        try:
            color = int(color, 16)
            embed = discord.Embed(title=title, description=description, color=color)
            embed.set_footer(text="Sent by The Enforcer")
            if image_url:
                embed.set_image(url=image_url)
            if field_name and field_value:
                embed.add_field(name=field_name, value=field_value, inline=False)
            await interaction.channel.send(embed=embed)
            await interaction.response.send_message("📢 Embed sent.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid hex color. Use format like `0x7289da`.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
