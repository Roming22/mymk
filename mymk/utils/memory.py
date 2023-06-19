import gc
from math import ceil

from mymk.utils.toolbox import debug_mode, debug

# Test mode
for func in ["mem_alloc", "mem_free"]:
    if not func in dir(gc):
        setattr(gc, func, lambda: 1)


def memory_cost(name, run_gc=True):
    total_mem = gc.mem_free() + gc.mem_alloc()

    def inner(func):
        def wrapper(*args, **kwargs):
            if run_gc:
                gc.collect()
            free_mem = gc.mem_free()
            result = func(*args, **kwargs)
            if run_gc:
                gc.collect()
            mem_used = free_mem - gc.mem_free()
            debug(
                f"[Memory] {name} cost {mem_used} bytes ({mem_used*100/(total_mem):02f}%). Total memory used: {ceil(100*gc.mem_alloc()/total_mem)}%"
            )
            return result

        return wrapper

    return inner


if not debug_mode:
    def memory_cost(*_):
        def inner(func):
            return func

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
