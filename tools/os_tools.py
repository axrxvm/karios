from core.config import OS_TYPE, OS

if OS_TYPE == OS.WINDOWS:
    from tools.os_windows import open_app
elif OS_TYPE == OS.LINUX:
    from tools.os_linux import open_app
elif OS_TYPE == OS.MAC:
    from tools.os_mac import open_app
else:
    raise RuntimeError("Unsupported OS")
