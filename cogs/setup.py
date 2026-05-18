# ══════════════════════════════════════════════════════
#  cogs/setup.py  —  Server setup command (!setup)
# ══════════════════════════════════════════════════════

import discord
from discord.ext import commands

from config import SETUP_CATEGORY, SETUP_CHANNELS, TIER_ROLES


class Setup(commands.Cog):
    """One-time server setup: creates a category, channels, and hoisted tier roles."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── !setup ─────────────────────────────────────────

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setup_server(self, ctx: commands.Context) -> None:
        """
        Set up the server with a dedicated category, channels, and tier roles.
        Only server administrators can run this.
        Tier roles are hoisted so they appear as separate groups in the member list.
        """
        working_msg = await ctx.reply(
            "⚙️ Running server setup… this may take a few seconds."
        )

        guild = ctx.guild
        created_channels:  list[str] = []
        skipped_channels:  list[str] = []
        created_roles:     list[str] = []
        skipped_roles:     list[str] = []
        category_created = False

        # ── 1. Get or create the category ─────────────

        category = discord.utils.get(guild.categories, name=SETUP_CATEGORY)
        if category is None:
            try:
                category = await guild.create_category(
                    name=SETUP_CATEGORY,
                    reason="!setup: creating bot category",
                )
                category_created = True
                print(f"[Setup] [OK] Created category '{SETUP_CATEGORY}' in {guild.name}")
            except discord.Forbidden:
                await working_msg.edit(
                    content=(
                        "❌ I don't have permission to create channels/categories. "
                        "Please grant me **Manage Channels** and try again."
                    )
                )
                return
            except discord.HTTPException as e:
                await working_msg.edit(
                    content=f"❌ Failed to create category `{SETUP_CATEGORY}`: {e}"
                )
                return
        else:
            print(f"[Setup] Category '{SETUP_CATEGORY}' already exists, skipping.")

        # ── 2. Create channels inside the category ────

        for channel_name in SETUP_CHANNELS:
            existing = discord.utils.get(category.channels, name=channel_name)
            if existing is not None:
                skipped_channels.append(channel_name)
                print(f"[Setup] Skipped channel '#{channel_name}' (already in category)")
                continue

            try:
                await guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    reason="!setup: creating required channel",
                )
                created_channels.append(channel_name)
                print(f"[Setup] [OK] Created channel '#{channel_name}' in '{SETUP_CATEGORY}'")
            except discord.Forbidden:
                await working_msg.edit(
                    content=(
                        "❌ I don't have permission to create channels. "
                        "Please grant me **Manage Channels** and try again."
                    )
                )
                return
            except discord.HTTPException as e:
                await working_msg.edit(
                    content=f"❌ Failed to create channel `#{channel_name}`: {e}"
                )
                return

        # ── 3. Create tier roles ──────────────────────
        #
        # We create roles in REVERSE order (Legend first → Beginner last).
        # Discord inserts new roles at position 1 (above @everyone), so each
        # newly created role pushes the previous ones up. The net effect is:
        #   Legend ends up highest → appears at the top of the member list
        #   Beginner ends up lowest → appears at the bottom
        #
        # hoist=True makes each role show as its own group in the sidebar.

        newly_created_roles: list[discord.Role] = []

        for tier in reversed(TIER_ROLES):   # Legend → Elite → … → Beginner
            existing = discord.utils.get(guild.roles, name=tier["name"])
            if existing is not None:
                skipped_roles.append(tier["name"])
                print(f"[Setup] Skipped role '{tier['name']}' (already exists)")
                continue

            try:
                role = await guild.create_role(
                    name=tier["name"],
                    color=discord.Color(tier["color"]),
                    permissions=discord.Permissions(**tier["perms"]),
                    hoist=True,          # ← shows as separate group in member list
                    mentionable=True,
                    reason="!setup: creating tier role",
                )
                created_roles.append(tier["name"])
                newly_created_roles.append(role)
                print(f"[Setup] [OK] Created hoisted role '{tier['name']}' (#{tier['color']:06X})")
            except discord.Forbidden:
                await working_msg.edit(
                    content=(
                        "❌ I don't have permission to create roles. "
                        "Please grant me **Manage Roles** and try again."
                    )
                )
                return
            except discord.HTTPException as e:
                await working_msg.edit(
                    content=f"❌ Failed to create role `{tier['name']}`: {e}"
                )
                return

        # ── 4. Role hierarchy check ───────────────────
        #
        # Warn if the bot's own role isn't above all tier roles.

        bot_member = guild.get_member(self.bot.user.id)
        bot_top_role = bot_member.top_role if bot_member else None
        all_tier_names = {t["name"] for t in TIER_ROLES}
        problem_roles = [
            r for r in guild.roles
            if r.name in all_tier_names
            and bot_top_role is not None
            and r >= bot_top_role
        ]

        # ── 5. Build summary embed ────────────────────

        embed = discord.Embed(
            title="✅ Server Setup Complete!",
            color=discord.Color.from_rgb(46, 204, 113),
        )

        # Category
        cat_status = "✅ Created" if category_created else "⏭️ Already existed"
        embed.add_field(
            name="📂 Category",
            value=f"{cat_status}: **{SETUP_CATEGORY}**",
            inline=False,
        )

        # Channels
        ch_lines: list[str] = []
        for name in created_channels:
            ch_lines.append(f"✅ Created `#{name}`")
        for name in skipped_channels:
            ch_lines.append(f"⏭️ Skipped `#{name}` (already exists)")
        if ch_lines:
            embed.add_field(
                name=f"📁 Channels ({len(created_channels)} created, {len(skipped_channels)} skipped)",
                value="\n".join(ch_lines),
                inline=False,
            )

        # Roles
        role_lines: list[str] = []
        for name in created_roles:
            tier_cfg = next(t for t in TIER_ROLES if t["name"] == name)
            role_lines.append(f"✅ Created **{name}** `#{tier_cfg['color']:06X}` *(hoisted)*")
        for name in skipped_roles:
            role_lines.append(f"⏭️ Skipped **{name}** (already exists)")
        if role_lines:
            embed.add_field(
                name=f"🎭 Tier Roles ({len(created_roles)} created, {len(skipped_roles)} skipped)",
                value="\n".join(role_lines),
                inline=False,
            )

        # Tier guide
        embed.add_field(
            name="🗺️ Tier Progression (visible in member list)",
            value=(
                "👑 **Legend** → Day 30+ *(top of list)*\n"
                "🟠 **Elite** → Day 25–29\n"
                "🟣 **Grinder** → Day 20–24\n"
                "🔵 **Dedicated** → Day 15–19\n"
                "🟢 **Consistent** → Day 10–14\n"
                "⚪ **Beginner** → Day 1–9 *(bottom of list)*"
            ),
            inline=False,
        )

        # Warning if hierarchy is wrong
        if problem_roles:
            names = ", ".join(f"**{r.name}**" for r in problem_roles)
            embed.add_field(
                name="⚠️ Action Required — Role Hierarchy",
                value=(
                    f"The bot's role (`{bot_top_role.name}`) is **below** {names}.\n"
                    "Discord won't let the bot assign those roles until you fix this:\n"
                    "**Server Settings → Roles → drag the bot's role above all tier roles**"
                ),
                inline=False,
            )
            embed.color = discord.Color.orange()

        embed.set_footer(
            text=(
                f"Created {len(created_roles)} role(s), "
                f"{len(created_channels)} channel(s)"
                + (", 1 category" if category_created else "")
                + f" | Skipped {len(skipped_roles) + len(skipped_channels)} existing"
            )
        )

        await working_msg.edit(content=None, embed=embed)

    # ── Error handler ──────────────────────────────────

    @setup_server.error
    async def setup_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You need **Administrator** permission to run `!setup`."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.reply("❌ `!setup` can only be used inside a server.")
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
