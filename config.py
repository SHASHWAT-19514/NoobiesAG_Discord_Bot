# ══════════════════════════════════════════════════════
#  config.py  —  Central configuration for the bot
#  Edit values here, no need to touch any other file.
# ══════════════════════════════════════════════════════

import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# ── Channel names ──────────────────────────────────────
PROGRESS_CHANNEL    = os.getenv("PROGRESS_CHANNEL", "progress-updates")
CF_ACTIVITY_CHANNEL = os.getenv("CF_ACTIVITY_CHANNEL", "cf-activity")

# ── Category + Channels created by !setup ─────────────
SETUP_CATEGORY = os.getenv("SETUP_CATEGORY", "📊 Progress Tracker")   # category that holds all bot channels

SETUP_CHANNELS: list[str] = [
    "progress-updates",
    "cf-activity",
    "leaderboard",
]

# ── Day roles (Day 1 … Day 30) ─────────────────────────
DAY_ROLES: dict[int, str] = {day: f"Day {day}" for day in range(1, 31)}

# ── Phase roles ────────────────────────────────────────
#  Awarded automatically when a phase boundary is crossed.
#  Key = last day of the phase, Value = role name
PHASE_ROLES: dict[int, str] = {
    10: "Phase 1 Complete",
    20: "Phase 2 Complete",
    30: "Phase 3 Complete",
}

# ── Tier roles ─────────────────────────────────────────
#  Ordered from lowest to highest.
#  color    → hex int used with discord.Color
#  min_day  → first day this tier applies (inclusive)
#  max_day  → last day this tier applies (inclusive), use 9999 for "30+"
#  perms    → kwargs forwarded to discord.Permissions (cumulative across tiers)
TIER_ROLES: list[dict] = [
    {
        "name":    "Beginner",
        "color":   0x95A5A6,
        "min_day": 1,
        "max_day": 9,
        "perms":   {},                              # basic chat (default)
    },
    {
        "name":    "Consistent",
        "color":   0x2ECC71,
        "min_day": 10,
        "max_day": 14,
        "perms":   {
            "change_nickname": True,
        },
    },
    {
        "name":    "Dedicated",
        "color":   0x3498DB,
        "min_day": 15,
        "max_day": 19,
        "perms":   {
            "change_nickname": True,
            "attach_files":    True,
        },
    },
    {
        "name":    "Grinder",
        "color":   0x9B59B6,
        "min_day": 20,
        "max_day": 24,
        "perms":   {
            "change_nickname":   True,
            "attach_files":      True,
            "add_reactions":     True,
            "use_external_emojis": True,
        },
    },
    {
        "name":    "Elite",
        "color":   0xE67E22,
        "min_day": 25,
        "max_day": 29,
        "perms":   {
            "change_nickname":   True,
            "attach_files":      True,
            "add_reactions":     True,
            "use_external_emojis": True,
            "embed_links":       True,
        },
    },
    {
        "name":    "Legend",
        "color":   0xF1C40F,
        "min_day": 30,
        "max_day": 9999,
        "perms":   {
            "change_nickname":   True,
            "attach_files":      True,
            "add_reactions":     True,
            "use_external_emojis": True,
            "embed_links":       True,
        },
    },
]

# ── Codeforces settings ────────────────────────────────
CF_POLL_INTERVAL    = 300  # seconds between submission polls (5 min)
CF_SUBMISSION_COUNT = 5    # how many recent submissions to fetch per user

# ── Misc ───────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "bot_data.db")
