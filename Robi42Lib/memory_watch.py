import gc
import os


def get_free_rom():
    """
    Returns available storage in KBs
    """
    s = os.statvfs("//")
    return s[0] * s[3] / 1024


def get_ram_size():
    """
    Returns free, allocated and total RAM
    """
    free = gc.mem_free()
    allocated = gc.mem_alloc()
    return free, allocated, free + allocated
