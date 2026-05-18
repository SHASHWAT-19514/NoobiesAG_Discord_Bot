# ══════════════════════════════════════════════════════
#  cogs/admin.py  —  Admin-only utility commands
# ══════════════════════════════════════════════════════

import discord
from discord.ext import commands

import database as db
from config import DAY_ROLES, TIER_ROLES


_TIER_NAMES: set[str] = {t["name"] for t in TIER_ROLES}
_DAY_ROLE_NAMES: set[str] = set(DAY_ROLES.values())


class Admin(commands.Cog):
    """Admin-only commands for server management."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="resetprogress")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset_progress(
        self, ctx: commands.Context, member: discord.Member = None
    ) -> None:
        """Reset a user's progress back to Day 0. Usage: !resetprogress @user"""
        if member is None:
            await ctx.reply(
                "❌ Usage: `!resetprogress @user`\n"
                "Example: `!resetprogress @saurav`"
            )
            return

        # Confirm current progress before wiping
        row = db.get_progress(member.id)
        if row is None:
            await ctx.reply(
                f"ℹ️ **{member.display_name}** has no progress data to reset."
            )
            return

        current_day = row["current_day"]

        # Remove Day-N and Tier roles from Discord
        roles_to_remove = [
            r for r in member.roles
            if r.name in _DAY_ROLE_NAMES or r.name in _TIER_NAMES
        ]
        if roles_to_remove:
            try:
                await member.remove_roles(
                    *roles_to_remove,
                    reason=f"Admin reset by {ctx.author}",
                )
                print(f"[Admin] Removed {len(roles_to_remove)} role(s) from {member}")
            except discord.Forbidden:
                await ctx.reply(
                    "⚠️ Could not remove roles — check bot role hierarchy. "
                    "Progress data was **not** cleared."
                )
                return

        # Wipe the database row
        db.reset_progress(member.id)
        print(f"[Admin] {ctx.author} reset progress for {member} (was Day {current_day})")

        embed = discord.Embed(
            title="🔄 Progress Reset",
            description=(
                f"**{member.mention}** has been reset.\n\n"
                f"```\n"
                f"Previous day : {current_day}\n"
                f"New day      : 0\n"
                f"Roles cleared: {len(roles_to_remove)}\n"
                f"Reset by     : {ctx.author}\n"
                f"```"
            ),
            color=0xE74C3C,
        )
        await ctx.reply(embed=embed)

    @reset_progress.error
    async def reset_progress_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ You need **Administrator** permission to use this command.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.reply("❌ Member not found. Mention them with @.")
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
