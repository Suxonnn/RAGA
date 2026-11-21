"""Aksi baca-saja untuk status sistem. Semua fungsi menerima **_ agar seragam."""
import psutil

GB = 1024 ** 3

def cek_ram(**_) -> str:
    m = psutil.virtual_memory()
    return (
        f"Memory usage is at {m.percent:.0f} percent, "
        f"{m.used / GB:.1f} of {m.total / GB:.1f} gigabytes."
    )


def cek_cpu(**_) -> str:
    return f"CPU load is at {psutil.cpu_percent(interval=1):.0f} percent."


def cek_baterai(**_) -> str:
    b = psutil.sensors_battery()
    if b is None:
        return "No battery detected."
    status = "charging" if b.power_plugged else "not plugged in"
    return f"Battery is at {int(b.percent)} percent, {status}."


def cek_disk(**_) -> str:
    bagian = []
    for p in psutil.disk_partitions():
        if "cdrom" in p.opts or not p.fstype:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
        except OSError:
            continue
        bagian.append(f"Drive {p.device[0]} has {u.free / GB:.0f} gigabytes free")
    return ". ".join(bagian) + "." if bagian else "No drives could be read."