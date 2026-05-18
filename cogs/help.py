# ══════════════════════════════════════════════════════
#  cogs/help.py  —  Custom paginated, interactive CP help
# ══════════════════════════════════════════════════════

import discord
from discord.ext import commands

# ── Detailed Command Documentation ────────────────────
COMMAND_HELP = {
    # ── Progress ──
    "progress": {
        "description": "View your current day, rank tier, phase milestones, and progress statistics.",
        "usage": "!progress",
        "example": "!progress",
        "cooldown": "5 seconds"
    },
    "leaderboard": {
        "description": "See the top 10 grinders on the server ranked by their current day.",
        "usage": "!leaderboard",
        "example": "!leaderboard",
        "cooldown": "5 seconds"
    },
    "freeze": {
        "description": "Activate streak freeze to protect consistency for 1 day. Resets Sunday midnight.",
        "usage": "!freeze",
        "example": "!freeze",
        "cooldown": "10 seconds"
    },
    "setcf": {
        "description": "Link your Codeforces handle/username to your Discord account. Performs API validation.",
        "usage": "!setcf <handle>",
        "example": "!setcf tourist",
        "cooldown": "5 seconds"
    },
    "unsetcf": {
        "description": "Unlink your Codeforces handle from your Discord account.",
        "usage": "!unsetcf",
        "example": "!unsetcf",
        "cooldown": "5 seconds"
    },
    "cfstats": {
        "description": "Show rich Codeforces profile metrics, tier rank, total solves, and last 5 accepted problems.",
        "usage": "!cfstats [handle]",
        "example": "!cfstats tourist",
        "cooldown": "5 seconds"
    },

    # ── Codeforces ──
    "giveproblem": {
        "description": "Suggest a random unsolved Codeforces problem matching a specific difficulty rating.",
        "usage": "!giveproblem <rating>",
        "example": "!giveproblem 1400",
        "cooldown": "5 seconds"
    },
    "virtualduel": {
        "description": "Start a 2-hour virtual duel over an unsolved average-rated problem with another member.",
        "usage": "!virtualduel @user",
        "example": "!virtualduel @tourist",
        "cooldown": "10 seconds"
    },
    "compare": {
        "description": "Compare Codeforces statistics and solving profiles side-by-side in 5 categories.",
        "usage": "!compare @user1 @user2",
        "example": "!compare @tourist @Benq",
        "cooldown": "5 seconds"
    },

    # ── Contests ──
    "contests": {
        "description": "Display the next 5 upcoming scheduled contests on Codeforces.",
        "usage": "!contests",
        "example": "!contests",
        "cooldown": "5 seconds"
    },
    "weeklyresults": {
        "description": "View live standings, problems, and solves for the active weekly mini-contest.",
        "usage": "!weeklyresults",
        "example": "!weeklyresults",
        "cooldown": "5 seconds"
    },

    # ── Social ──
    "findpartner": {
        "description": "Find practice partners on the server within 200 rating points of target rating.",
        "usage": "!findpartner <rating>",
        "example": "!findpartner 1500",
        "cooldown": "5 seconds"
    },
    "creategroup": {
        "description": "Create a co-working study group of up to 5 members with a unique name.",
        "usage": "!creategroup <group_name>",
        "example": "!creategroup dynamic_programming",
        "cooldown": "5 seconds"
    },
    "joingroup": {
        "description": "Join an existing active study group on the server.",
        "usage": "!joingroup <group_name>",
        "example": "!joingroup dynamic_programming",
        "cooldown": "5 seconds"
    },
    "leavegroup": {
        "description": "Leave your current study group.",
        "usage": "!leavegroup",
        "example": "!leavegroup",
        "cooldown": "5 seconds"
    },
    "groupstats": {
        "description": "View aggregate consistency progress and combined solves of your study group.",
        "usage": "!groupstats",
        "example": "!groupstats",
        "cooldown": "5 seconds"
    },
    "createvc": {
        "description": "Establish a temporary private voice channel for co-working or practicing with @user.",
        "usage": "!createvc @user",
        "example": "!createvc @tourist",
        "cooldown": "10 seconds"
    },

    # ── Admin ──
    "setup": {
        "description": "Admin command to fully initialize server category, channels, and hoisted roles.",
        "usage": "!setup",
        "example": "!setup",
        "cooldown": "None (Admin only)"
    },
    "resetprogress": {
        "description": "Admin override to wipe a member's consistency streak, stats, and tier roles to Day 0.",
        "usage": "!resetprogress @user",
        "example": "!resetprogress @tourist",
        "cooldown": "None (Admin only)"
    },

    # ── Analytics ──
    "predict": {
        "description": "Estimate your Codeforces rating change delta for a recently finished contest.",
        "usage": "!predict <contest_id>",
        "example": "!predict 1934",
        "cooldown": "5 seconds"
    },
    "heatmap": {
        "description": "Generate a beautiful GitHub-style Codeforces solve activity heatmap image.",
        "usage": "!heatmap [@user]",
        "example": "!heatmap @tourist",
        "cooldown": "10 seconds"
    },
    "weakness": {
        "description": "Analyze your last 200 submissions to find weakest and strongest problem tag topics.",
        "usage": "!weakness",
        "example": "!weakness",
        "cooldown": "10 seconds"
    },
    "upsolve": {
        "description": "Scan a contest and add unsolved problems directly to your upsolving backlog list.",
        "usage": "!upsolve <contest_id>",
        "example": "!upsolve 1934",
        "cooldown": "5 seconds"
    },
    "myupsolves": {
        "description": "Display all pending upsolve problems in your database backlog.",
        "usage": "!myupsolves",
        "example": "!myupsolves",
        "cooldown": "5 seconds"
    },
    "solvedupsolve": {
        "description": "Mark a pending upsolve problem in your backlog list as resolved.",
        "usage": "!solvedupsolve <problem_id>",
        "example": "!solvedupsolve 1934A",
        "cooldown": "5 seconds"
    },

    # ── Economy ──
    "xp": {
        "description": "Show your current XP level, total XP, and a custom progress bar to next level.",
        "usage": "!xp [@user]",
        "example": "!xp @tourist",
        "cooldown": "3 seconds"
    },
    "balance": {
        "description": "Show your coin balance.",
        "usage": "!balance [@user]",
        "example": "!balance",
        "cooldown": "3 seconds"
    },
    "xpleaderboard": {
        "description": "Display top 10 users ranked by overall economy level & XP.",
        "usage": "!xpleaderboard",
        "example": "!xpleaderboard",
        "cooldown": "5 seconds"
    },
    "shop": {
        "description": "Browse available boosters, skips, custom color tags, and upgrades in the shop.",
        "usage": "!shop",
        "example": "!shop",
        "cooldown": "5 seconds"
    },
    "buy": {
        "description": "Purchase an upgrade item from the shop (Streak Freeze, Custom Color, Nickname Color, XP Boost, Problem Skip).",
        "usage": "!buy <item_name> [color_hex]",
        "example": "!buy custom_role_color #FF5733",
        "cooldown": "5 seconds"
    },
    "give": {
        "description": "Gift coins from your balance to another user.",
        "usage": "!give @user <amount>",
        "example": "!give @tourist 100",
        "cooldown": "5 seconds"
    },

    # ── Achievements ──
    "achievements": {
        "description": "Show all 12 automatic achievement badges with unlocked and locked hint statuses.",
        "usage": "!achievements [@user]",
        "example": "!achievements",
        "cooldown": "5 seconds"
    },

    # ── Seasons ──
    "season": {
        "description": "Show details for the active season, days remaining, and your personal ranking.",
        "usage": "!season",
        "example": "!season",
        "cooldown": "5 seconds"
    },
    "seasonleaderboard": {
        "description": "Show the top 10 players for the active month's season.",
        "usage": "!seasonleaderboard",
        "example": "!seasonleaderboard",
        "cooldown": "5 seconds"
    },
    "halloffame": {
        "description": "Display all past season champions archived permanently in the Hall of Fame.",
        "usage": "!halloffame",
        "example": "!halloffame",
        "cooldown": "5 seconds"
    },

    # ── Community ──
    "tip": {
        "description": "Submit a Competitive Programming tip to the tips channel anonymously.",
        "usage": "!tip <content>",
        "example": "!tip Make sure to read problem constraints first!",
        "cooldown": "10 seconds"
    },
    "lookingforteam": {
        "description": "Register yourself in the ICPC team formation sign-up pool.",
        "usage": "!lookingforteam",
        "example": "!lookingforteam",
        "cooldown": "5 seconds"
    },
    "formteam": {
        "description": "Form an ICPC team with 2 partners, auto-generating private text & VC rooms.",
        "usage": "!formteam @user1 @user2",
        "example": "!formteam @tourist @Benq",
        "cooldown": "10 seconds"
    },

    # ── Help ──
    "help": {
        "description": "Display the interactive paginated help menu or view details for a specific command.",
        "usage": "!help [command]",
        "example": "!help virtualduel",
        "cooldown": "3 seconds"
    }
}


# ── Interactive Dropdown Menu ──────────────────────────

class HelpDropdown(discord.ui.Select):
    """Dropdown list that selects specific modules in the help menu."""

    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="Progress Tracker",
                description="Day consistency, leaderboard, handle setup",
                emoji="📋",
                value="1"
            ),
            discord.SelectOption(
                label="Codeforces Setup",
                description="Problem recommendations & duels",
                emoji="⚔️",
                value="2"
            ),
            discord.SelectOption(
                label="Contests Setup",
                description="Upcoming contests & weekly results",
                emoji="🏆",
                value="3"
            ),
            discord.SelectOption(
                label="Stats Profile",
                description="Profile analysis cards & duels",
                emoji="📊",
                value="4"
            ),
            discord.SelectOption(
                label="Social Setup",
                description="Partners, study groups, private VCs",
                emoji="🤝",
                value="5"
            ),
            discord.SelectOption(
                label="Admin Override",
                description="Administrators server initialization",
                emoji="⚙️",
                value="6"
            ),
            discord.SelectOption(
                label="Analytics",
                description="CF Deltas, Pillow heatmaps, weaknesses, upsolves",
                emoji="📈",
                value="7"
            ),
            discord.SelectOption(
                label="Economy & Badges",
                description="Levels, Shop, buy/give coins, achievements",
                emoji="🪙",
                value="8"
            ),
            discord.SelectOption(
                label="Roadmaps & Seasons",
                description="CP Roadmaps, done topics, monthly seasons",
                emoji="🎯",
                value="9"
            ),
            discord.SelectOption(
                label="Doubts & Community",
                description="Doubt threads, anonymous tips, LFT, ICPC teams",
                emoji="💬",
                value="10"
            ),
        ]
        super().__init__(
            placeholder="Select Module To Get Help For That Module",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        view: HelpView = self.view
        view.current_page = int(self.values[0])
        await view.update_message(interaction)


# ── Interactive Paginated View ─────────────────────────

class HelpView(discord.ui.View):
    """View managing buttons, select dropdowns, timeout, and message state."""

    def __init__(self, ctx: commands.Context, bot: commands.Bot, total_cmds: int) -> None:
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.bot = bot
        self.total_cmds = total_cmds
        self.current_page = 0
        self.message = None

        # Add select dropdown menu
        self.add_item(HelpDropdown())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "❌ This help menu is not for you! Run `!help` to create your own.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        try:
            if self.message:
                await self.message.edit(view=self)
        except Exception:
            pass

    # ── Pagination Buttons ─────────────────────────────

    @discord.ui.button(label="«", style=discord.ButtonStyle.blurple, row=1)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = 0
        await self.update_message(interaction)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.success, row=1)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = (self.current_page - 1) % 11
        await self.update_message(interaction)

    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger, row=1)
    async def close_menu(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.success, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = (self.current_page + 1) % 11
        await self.update_message(interaction)

    @discord.ui.button(label="»", style=discord.ButtonStyle.blurple, row=1)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = 10
        await self.update_message(interaction)

    # ── Embed Generator ────────────────────────────────

    def get_embed(self) -> discord.Embed:
        avatar_url = self.bot.user.display_avatar.url if self.bot.user else None

        embed = discord.Embed(color=0x2C2F33)
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)

        if self.current_page == 0:
            # Main Help Embed
            embed.title = "🖥️ AGNoobies Control Panel"
            embed.description = "Type `!help <command>` to get more info about a specific command."
            
            embed.add_field(
                name="📋 Progress Module",
                value="View consistency streaks, server rankings, streak freezes, and link accounts.",
                inline=False
            )
            embed.add_field(
                name="⚔️ Codeforces Module",
                value="Fetch targeted unsolved problems, challenge rivals in duels, and link profiles.",
                inline=False
            )
            embed.add_field(
                name="📈 Analytics Module (New!)",
                value="Contest rating deltas, Pillow solves heatmaps, weaknesses finder, and upsolving lists.",
                inline=False
            )
            embed.add_field(
                name="🪙 Economy & Badges Module (New!)",
                value="Levels and XP progress bars, virtual shop upgrades, custom colors, and achievements.",
                inline=False
            )
            embed.add_field(
                name="🎯 Roadmaps & Seasons Module (New!)",
                value="CP learning checklists, marking topics done, monthly seasons, and the permanent HOF.",
                inline=False
            )
            embed.add_field(
                name="💬 Doubts & Community Module (New!)",
                value="Raising doubt threads, solvers rewards, anonymous CP tips, LFT pool, and ICPC teams.",
                inline=False
            )
            embed.set_footer(text=f"{self.total_cmds} Commands total", icon_url=avatar_url)

        elif self.current_page == 1:
            embed.title = "📋 PROGRESS TRACKER MODULE"
            embed.description = (
                "```\n"
                "!progress     →  View your current day and rank\n"
                "!leaderboard  →  See top grinders on the server\n"
                "!freeze       →  Use your streak freeze (1/week)\n"
                "!setcf        →  Link your Codeforces handle\n"
                "!unsetcf      →  Unlink your Codeforces handle\n"
                "!cfstats      →  View detailed profile solves\n"
                "```"
            )
            embed.set_footer(text="Page 1/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 2:
            embed.title = "⚔️ CODEFORCES MODULE"
            embed.description = (
                "```\n"
                "!giveproblem  →  Get unsolved problem recommendations\n"
                "!virtualduel  →  Start a 2-hour competitive CP duel\n"
                "!compare      →  Compare statistics side-by-side\n"
                "!setcf        →  Link your Codeforces handle\n"
                "```"
            )
            embed.set_footer(text="Page 2/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 3:
            embed.title = "🏆 CONTESTS MODULE"
            embed.description = (
                "```\n"
                "!contests       →  Show next 5 upcoming CF contests\n"
                "!weeklyresults  →  View weekly mini-contest status\n"
                "```"
            )
            embed.set_footer(text="Page 3/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 4:
            embed.title = "📊 STATS PROFILE MODULE"
            embed.description = (
                "```\n"
                "!cfstats      →  View detailed profile & solves\n"
                "!compare      →  Compare statistics side-by-side\n"
                "!leaderboard  →  See top grinders on the server\n"
                "```"
            )
            embed.set_footer(text="Page 4/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 5:
            embed.title = "🤝 SOCIAL MODULE"
            embed.description = (
                "```\n"
                "!findpartner  →  Find practice partners in rating range\n"
                "!creategroup  →  Create a study group (max 5 members)\n"
                "!joingroup    →  Join an active study group\n"
                "!groupstats   →  View study group aggregate stats\n"
                "!createvc     →  Launch temporary private VC room\n"
                "```"
            )
            embed.set_footer(text="Page 5/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 6:
            embed.title = "⚙️ ADMIN MODULE"
            embed.description = (
                "```\n"
                "!setup          →  Initialize server category & channels\n"
                "!resetprogress  →  Wipe user progress & roles to Day 0\n"
                "```"
            )
            embed.set_footer(text="Page 6/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 7:
            embed.title = "📈 ANALYTICS MODULE"
            embed.description = (
                "```\n"
                "!predict         →  Estimate Codeforces rating delta\n"
                "!heatmap         →  Show PIL-drawn CF solves heatmap\n"
                "!weakness        →  Analyze weakest & strongest tag topics\n"
                "!upsolve         →  Add contest problems to upsolving list\n"
                "!myupsolves      →  View your pending upsolve list\n"
                "!solvedupsolve   →  Mark a pending upsolve as solved\n"
                "```"
            )
            embed.set_footer(text="Page 7/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 8:
            embed.title = "🪙 ECONOMY & BADGES MODULE"
            embed.description = (
                "```\n"
                "!xp             →  View level progress & XP stats\n"
                "!balance        →  Check your economy coin balance\n"
                "!xpleaderboard  →  Rank grinders by levels & XP\n"
                "!shop           →  Purchase skips, boosts, custom roles\n"
                "!buy            →  Buy shop upgrade items using coins\n"
                "!give           →  Gift/transfer coins to another member\n"
                "!achievements   →  Show unlocked & locked CP badges\n"
                "```"
            )
            embed.set_footer(text="Page 8/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 9:
            embed.title = "🎯 ROADMAPS & SEASONS MODULE"
            embed.description = (
                "```\n"
                "!roadmap            →  Show CP learning checklist roadmap\n"
                "!done               →  Mark a roadmap topic as completed\n"
                "!mytopics           →  Show statistics of topics mastered\n"
                "!tplearnors         →  Leaderboard of roadmap top learnors\n"
                "!season             →  Check season points and rank\n"
                "!seasonleaderboard  →  Show top season leaderboard grinders\n"
                "!halloffame         →  Show all past archived HOF winners\n"
                "```"
            )
            embed.set_footer(text="Page 9/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        elif self.current_page == 10:
            embed.title = "💬 DOUBTS & COMMUNITY MODULE"
            embed.description = (
                "```\n"
                "!doubt           →  Raise a doubt and start a thread\n"
                "!solved          →  Mark doubt solved inside active thread\n"
                "!opendoubts      →  Show active unresolved doubts list\n"
                "!mydoubts        →  Check your personal doubts raised history\n"
                "!tip             →  Post anonymous CP tips to #tips\n"
                "!lookingforteam  →  Sign up for LFT ICPC partner pool\n"
                "!formteam        →  Form ICPC team & create private VC/Text\n"
                "```"
            )
            embed.set_footer(text="Page 10/10 • Type !help <command> for detailed info", icon_url=avatar_url)

        return embed

    async def update_message(self, interaction: discord.Interaction) -> None:
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)


# ── Help Cog Class ─────────────────────────────────────

class Help(commands.Cog):
    """Interactive help command cog designed with CP themed elements."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"])
    async def help_cmd(self, ctx: commands.Context, command_name: str = None) -> None:
        """Show the AGNoobies control panel or get detailed info about a specific command."""
        avatar_url = self.bot.user.display_avatar.url if self.bot.user else None

        if command_name:
            command_name = command_name.lower().strip()
            # Resolve common aliases to provide correct help entries
            alias_map = {
                "vd": "virtualduel",
                "duel": "virtualduel",
                "h": "help",
                "commands": "help",
                "cfprofile": "cfstats",
                "weekly": "weeklyresults",
                "weekly_results": "weeklyresults",
                "mini_contest": "weeklyresults",
                "upcoming": "contests",
                "level": "xp",
                "lvl": "xp",
                "bal": "balance",
                "coins": "balance",
                "badges": "achievements",
                "xplb": "xpleaderboard",
                "slb": "seasonleaderboard",
                "seasonlb": "seasonleaderboard",
                "hof": "halloffame",
                "lfpool": "lookingforteam",
                "tplearnors": "tplearnors",
                "toplearners": "tplearnors",
            }
            resolved_name = alias_map.get(command_name, command_name)

            if resolved_name in COMMAND_HELP:
                info = COMMAND_HELP[resolved_name]
                embed = discord.Embed(
                    title=f"🖥️ Command Help: !{resolved_name}",
                    color=0x2C2F33
                )
                if avatar_url:
                    embed.set_thumbnail(url=avatar_url)
                embed.add_field(name="Description", value=info["description"], inline=False)
                embed.add_field(name="Usage", value=f"`{info['usage']}`", inline=False)
                embed.add_field(name="Example", value=f"`{info['example']}`", inline=False)
                embed.add_field(name="Cooldown", value=f"`{info['cooldown']}`", inline=False)
                embed.set_footer(
                    text=f"Requested by {ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(
                    f"❌ Command `!{command_name}` not found. Type `!help` to see all available commands."
                )
            return

        # Interactive Paginated help menu
        total_cmds = len(COMMAND_HELP)
        view = HelpView(ctx, self.bot, total_cmds)
        embed = view.get_embed()

        msg = await ctx.reply(embed=embed, view=view)
        view.message = msg


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
