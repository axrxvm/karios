from core.config import OS_TYPE, OS

if OS_TYPE == OS.WINDOWS:
    from tools.os_windows import (
        open_app,
        close_app,
        lock_screen,
        reboot,
        shutdown,
        volume_up,
        volume_down,
        mute_volume,
    )
elif OS_TYPE == OS.LINUX:
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
elif OS_TYPE == OS.MAC:
    from tools.os_mac import (
        open_app,
        close_app,
        lock_screen,
        reboot,
        shutdown,
        volume_up,
        volume_down,
        mute_volume,
    )
else:
    raise RuntimeError("Unsupported OS")
