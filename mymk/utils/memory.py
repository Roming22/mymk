import gc
from math import ceil

from mymk.utils.logger import logger

# Test mode
for func in ["mem_alloc", "mem_free"]:
    if not func in dir(gc):
        setattr(gc, func, lambda: 1)

profile = True
# profile = False


def free_memory(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            gc.collect()
            logger.info("\n\nMemory after instanciation of %s: %s", name, get_usage(True))

        return wrapper

    return inner


def check_memory():
    total_mem = gc.mem_free() + gc.mem_alloc()

    def inner(func):
        def wrapper(*args, **kwargs):
            used_mem = gc.mem_alloc()
            if used_mem / total_mem >= 0.8:
                gc.collect()
            result = func(*args, **kwargs)
            return result

        return wrapper

    return inner


def memory_cost(name, run_gc=True):
    total_mem = gc.mem_free() + gc.mem_alloc()

    def inner(func):
        def wrapper(*args, **kwargs):
            if run_gc:
                gc.collect()
            if profile:
                free_mem = gc.mem_free()
            result = func(*args, **kwargs)
            if run_gc:
                gc.collect()
            if profile:
                mem_used = free_mem - gc.mem_free()
                logger.info(
                    "[Memory] %s cost %s bytes (%s%%). Total memory used: %s%%",
                    name,
                    mem_used,
                    f"{mem_used*100/(total_mem):02f}",
                    ceil(100*gc.mem_alloc()/total_mem),
                )
            return result

        return wrapper

    return inner


def get_usage(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = "{0:.2f}%".format(A / T * 100)
    if not full:
        return A
    else:
        return "Total:{0} Used:{1} ({2})".format(T, A, P)
