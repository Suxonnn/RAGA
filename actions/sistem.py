"""Aksi baca-saja untuk status sistem. Semua fungsi menerima **_ agar seragam."""
import psutil

GB = 1024 ** 3


def cek_ram(**_) -> str:
    m = psutil.virtual_memory()
    return (
        f"RAM terpakai {m.percent:.0f} persen, "
        f"{m.used / GB:.1f} dari {m.total / GB:.1f} gigabyte."
    )


def cek_cpu(**_) -> str:
    return f"Beban CPU saat ini {psutil.cpu_percent(interval=1):.0f} persen."


def cek_baterai(**_) -> str:
    b = psutil.sensors_battery()
    if b is None:
        return "Tidak ada baterai yang terdeteksi."
    status = "sedang diisi" if b.power_plugged else "belum dicolok"
    return f"Baterai tersisa {int(b.percent)} persen, {status}."


def cek_disk(**_) -> str:
    bagian = []
    for p in psutil.disk_partitions():
        if "cdrom" in p.opts or not p.fstype:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
        except OSError:
            continue
        bagian.append(f"Disk {p.device.rstrip(chr(92))} sisa {u.free / GB:.0f} gigabyte")
    return ". ".join(bagian) + "." if bagian else "Tidak ada disk yang terbaca."
