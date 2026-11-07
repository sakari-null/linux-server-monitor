import shutil
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CRITICAL_THRESHOLD = 90
WARNING_THRESHOLD = 80


def main():
    LogDirectory = BASE_DIR / "logs"

    try:
        LogDirectory.mkdir(parents=True, exist_ok=True)
        
        LogHandler = RotatingFileHandler(
            LogDirectory / "monitor.log",
            maxBytes=1_000_000,
            backupCount=5
        )

    except OSError as Error:
        print(f"Logging setup failed: {Error}")
        return
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[LogHandler]
    )
    logging.info("System monitoring started")
    try:
        DiskUsage = shutil.disk_usage("/")
    except OSError as Error:
        print(f"Disk monitoring failed: {Error}")
        logging.error(f"Disk monitoring failed: {Error}")
        return

    TotalSpace = DiskUsage.total
    UsedSpace = DiskUsage.used
    FreeSpace = DiskUsage.free
    UsagePercent = (UsedSpace / TotalSpace) * 100

    DiskStatus = GetStatus(UsagePercent)

    print("Linux Server Monitor")
    print("--------------------")

    print(f"Total space: {TotalSpace / (1024 ** 3):.2f} GB")
    print(f"Used space:  {UsedSpace / (1024 ** 3):.2f} GB")
    print(f"Free space:  {FreeSpace / (1024 ** 3):.2f} GB")
    print(f"Disk usage:  {UsagePercent:.1f} %")
    print(f"Disk status: {DiskStatus}")

    if DiskStatus == "CRITICAL":
        logging.critical(
            f"Disk usage: {UsagePercent:.1f}% - Status: {DiskStatus}"
        )
    elif DiskStatus == "WARNING":
        logging.warning(
            f"Disk usage: {UsagePercent:.1f}% - Status: {DiskStatus}"
        )
    else:
        logging.info(
            f"Disk usage: {UsagePercent:.1f}% - Status: {DiskStatus}"
        )

    MemoryInfo = GetMemoryInfo()

    if MemoryInfo is None:
        return

    MemoryTotal = MemoryInfo["MemTotal"]
    MemoryAvailable = MemoryInfo["MemAvailable"]

    MemoryUsed = MemoryTotal - MemoryAvailable
    MemoryUsagePercent = (MemoryUsed / MemoryTotal) * 100

    MemoryStatus = GetStatus(MemoryUsagePercent)

    print("\nMemory Monitor")
    print("--------------------")
    print(f"Total RAM: {MemoryTotal / (1024 ** 2):.2f} GB")
    print(f"Used RAM: {MemoryUsed / (1024 ** 2):.2f} GB")
    print(f"Available RAM: {MemoryAvailable / (1024 ** 2):.2f} GB")
    print(f"Memory usage: {MemoryUsagePercent:.1f} %")
    print(f"Memory status: {MemoryStatus}")

    if MemoryStatus == "CRITICAL":
        logging.critical(
            f"Memory usage: {MemoryUsagePercent:.1f}% - Status: {MemoryStatus}"
        )
    elif MemoryStatus == "WARNING":
        logging.warning(
            f"Memory usage: {MemoryUsagePercent:.1f}% - Status: {MemoryStatus}"
        )
    else:
        logging.info(
            f"Memory usage: {MemoryUsagePercent:.1f}% - Status: {MemoryStatus}"
        )

    CPUUsage = GetCPUUsage()

    if CPUUsage is None:
        return

    CPUStatus = GetStatus(CPUUsage)

    print(f"CPU usage: {CPUUsage:.1f} %")
    print(f"CPU status: {CPUStatus}")

    if CPUStatus == "CRITICAL":
        logging.critical(
            f"CPU usage: {CPUUsage:.1f}% - Status: {CPUStatus}"
        )
    elif CPUStatus == "WARNING":
        logging.warning(
            f"CPU usage: {CPUUsage:.1f}% - Status: {CPUStatus}"
        )
    else:
        logging.info(
            f"CPU usage: {CPUUsage:.1f}% - Status: {CPUStatus}"
        )

    SystemStatus = [DiskStatus, MemoryStatus, CPUStatus]

    if "CRITICAL" in SystemStatus:
        OverallStatus = "CRITICAL"
    elif "WARNING" in SystemStatus:
        OverallStatus = "WARNING"
    else:
        OverallStatus = "NORMAL"

    print("\nSystem Overview")
    print("--------------------")
    print(f"Disk: {DiskStatus}")
    print(f"Memory: {MemoryStatus}")
    print(f"CPU: {CPUStatus}")
    print("--------------------")
    print(f"Overall status: {OverallStatus}")

    if OverallStatus == "CRITICAL":
        logging.critical(f"Overall system status: {OverallStatus}")
    elif OverallStatus == "WARNING":
        logging.warning(f"Overall system status: {OverallStatus}")
    else:
        logging.info(f"Overall system status: {OverallStatus}")


def GetCPUUsage():
    FirstMeasurement = GetCPUInfo()

    if FirstMeasurement is None:
        return None

    time.sleep(1)

    SecondMeasurement = GetCPUInfo()

    if SecondMeasurement is None:
        return None

    FirstTotal = sum(FirstMeasurement[:8])
    SecondTotal = sum(SecondMeasurement[:8])

    FirstIdle = FirstMeasurement[3] + FirstMeasurement[4]
    SecondIdle = SecondMeasurement[3] + SecondMeasurement[4]

    TotalDifference = SecondTotal - FirstTotal
    IdleDifference = SecondIdle - FirstIdle

    if TotalDifference <= 0:
        return 0.0

    CPUUsage = (1 - IdleDifference / TotalDifference) * 100

    return CPUUsage
    

def GetMemoryInfo():
    MemoryInfo = {}

    try:
        with open("/proc/meminfo", "r") as File:
            for Line in File:
                Key, Value = Line.split(":", 1)
                MemoryInfo[Key] = int(Value.strip().split()[0])

    except (OSError, ValueError, IndexError) as Error:
        print(f"Memory monitoring failed: {Error}")
        logging.error(f"Memory monitoring failed: {Error}")
        return None

    RequiredKeys = ["MemTotal", "MemAvailable"]

    if not all(Key in MemoryInfo for Key in RequiredKeys):
        Error = "Required memory information is missing"
        print(f"Memory monitoring failed: {Error}")
        logging.error(f"Memory monitoring failed: {Error}")
        return None

    if MemoryInfo["MemTotal"] <= 0:
        Error = "Invalid total memory value"
        print(f"Memory monitoring failed: {Error}")
        logging.error(f"Memory monitoring failed: {Error}")
        return None

    if not 0 <= MemoryInfo["MemAvailable"] <= MemoryInfo["MemTotal"]:
        Error = "Invalid available memory value"
        print(f"Memory monitoring failed: {Error}")
        logging.error(f"Memory monitoring failed: {Error}")
        return None    

    return MemoryInfo


def GetCPUInfo():
    try:
        with open("/proc/stat", "r") as File:
            FirstLine = File.readline()

        CPUValues = FirstLine.split()[1:]
        CPUValues = [int(Value) for Value in CPUValues]

        if len(CPUValues) < 8:
            raise ValueError("Incomplete CPU data")

        return CPUValues

    except (OSError, ValueError, IndexError) as Error:
        print(f"CPU monitoring failed: {Error}")
        logging.error(f"CPU monitoring failed: {Error}")
        return None


def GetStatus(UsagePercent):

    if not isinstance(UsagePercent, (int, float)):
        raise TypeError("UsagePercent must be a number")

    if not 0 <= UsagePercent <= 100:
        raise ValueError("UsagePercent must be between 0 and 100")

    if UsagePercent >= CRITICAL_THRESHOLD:
        return "CRITICAL"
    elif UsagePercent >= WARNING_THRESHOLD:
        return "WARNING"
    else:
        return "NORMAL"


if __name__ == "__main__":
    main()
