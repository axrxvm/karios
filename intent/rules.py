import logging
from intent.intents import Intent
from tools.general import (
    get_time,
    get_date,
    get_uptime,
    get_battery,
    get_cpu_usage,
    get_memory_usage,
)
from tools.os_linux import (
    open_app,
    close_app,
    lock_screen,
    reboot,
    shutdown,
    volume_up,
    volume_down,
    mute_volume,
)

logger = logging.getLogger(__name__)

logger.debug("Building INTENTS list...")
INTENTS = [

    # ===== TIME / DATE =====
    Intent(
        name="get_time",
        keywords=["time", "clock"],
        executor=get_time,
        description="Get current time",
    ),

    Intent(
        name="get_date",
        keywords=["date", "day"],
        executor=get_date,
        description="Get current date",
    ),

    Intent(
        name="uptime",
        keywords=["uptime"],
        executor=get_uptime,
        description="System uptime",
    ),

    # ===== SYSTEM INFO =====
    Intent(
        name="battery",
        keywords=["battery"],
        executor=get_battery,
        description="Battery status",
    ),

    Intent(
        name="cpu",
        keywords=["cpu"],
        executor=get_cpu_usage,
        description="CPU usage",
    ),

    Intent(
        name="memory",
        keywords=["memory", "ram"],
        executor=get_memory_usage,
        description="Memory usage",
    ),

    # ===== APP CONTROL =====
    Intent(
        name="open_app",
        keywords=["open", "launch", "start"],
        executor=open_app,
        takes_argument=True,
        description="Open application",
    ),

    Intent(
        name="close_app",
        keywords=["close", "kill", "terminate"],
        executor=close_app,
        takes_argument=True,
        description="Close application",
    ),

    # ===== POWER =====
    Intent(
        name="lock",
        keywords=["lock"],
        executor=lock_screen,
        description="Lock screen",
    ),

    Intent(
        name="reboot",
        keywords=["reboot", "restart"],
        executor=reboot,
        description="Reboot system",
    ),

    Intent(
        name="shutdown",
        keywords=["shutdown", "poweroff"],
        executor=shutdown,
        description="Shutdown system",
    ),

    # ===== VOLUME =====
    Intent(
        name="volume_up",
        keywords=["volume", "louder", "increase"],
        executor=volume_up,
        description="Increase volume",
    ),

    Intent(
        name="volume_down",
        keywords=["quieter", "decrease"],
        executor=volume_down,
        description="Decrease volume",
    ),

    Intent(
        name="mute",
        keywords=["mute"],
        executor=mute_volume,
        description="Mute volume",
    ),
]

logger.info(f"Loaded {len(INTENTS)} intents")
