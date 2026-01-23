import psutil
from datetime import datetime


def get_time():
    return datetime.now().strftime("The time is %H:%M")


def get_date():
    return datetime.now().strftime("Today is %A, %B %d")


def get_uptime():
    seconds = int(psutil.boot_time())
    return "System uptime available"


def get_battery():
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery at {int(battery.percent)} percent"
    return "No battery detected"


def get_cpu_usage():
    return f"CPU usage is {psutil.cpu_percent()} percent"


def get_memory_usage():
    mem = psutil.virtual_memory()
    return f"Memory usage is {int(mem.percent)} percent"
