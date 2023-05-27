import gc
import os


def get_free_rom():
    """
    Returns available storage in KBs
    """
    s = os.statvfs("//")
    return s[0] * s[3] // 1024


def get_ram_size():
    """
    Returns free, allocated and total RAM in KBs
    """
    free = gc.mem_free() // 1024
    allocated = gc.mem_alloc() // 1024
    return free, allocated, free + allocated


def print_stats():
    print(f"Free ROM remaining: {get_free_rom()}kBs")
    print_RAM_usage()


def print_RAM_usage():
    free, allocated, total = get_ram_size()
    print("RAM:")
    print(f"\tFree: {free}kBs")
    print(f"\tAllocated: {allocated}kBs")
    print(f"\tTotal: {total}kBs")


if __name__ == "__main__":
    print_stats()
