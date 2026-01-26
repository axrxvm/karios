import logging
import psutil
from datetime import datetime

logger = logging.getLogger(__name__)


def get_time():
    logger.debug("get_time() called")
    result = datetime.now().strftime("The time is %H:%M")
    logger.info(f"get_time() result: {result}")
    return result


def get_date():
    logger.debug("get_date() called")
    result = datetime.now().strftime("Today is %A, %B %d")
    logger.info(f"get_date() result: {result}")
    return result


def get_uptime():
    logger.debug("get_uptime() called")
    seconds = int(psutil.boot_time())
    logger.debug(f"Boot time (seconds): {seconds}")
    result = "System uptime available"
    logger.info(f"get_uptime() result: {result}")
    return result


def get_battery():
    logger.debug("get_battery() called")
    battery = psutil.sensors_battery()
    if battery:
        logger.debug(f"Battery info: {battery.percent}% (plugged={battery.power_plugged})")
        result = f"Battery at {int(battery.percent)} percent"
    else:
        logger.debug("No battery detected")
        result = "No battery detected"
    logger.info(f"get_battery() result: {result}")
    return result


def get_cpu_usage():
    logger.debug("get_cpu_usage() called")
    cpu = psutil.cpu_percent()
    logger.debug(f"CPU usage: {cpu}%")
    result = f"CPU usage is {cpu} percent"
    logger.info(f"get_cpu_usage() result: {result}")
    return result


def get_memory_usage():
    logger.debug("get_memory_usage() called")
    mem = psutil.virtual_memory()
    logger.debug(f"Memory info: used={mem.used}, total={mem.total}, percent={mem.percent}")
    result = f"Memory usage is {int(mem.percent)} percent"
    logger.info(f"get_memory_usage() result: {result}")
    return result
