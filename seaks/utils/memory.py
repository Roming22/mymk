import gc


def free_memory(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            gc.collect()
            print(f"\n\nMemory after instanciation of {name}: ", get_free(True))

        return wrapper

    return inner


#
def memory_cost(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            gc.collect()
            free_mem = gc.mem_free()
            func(*args, **kwargs)
            gc.collect()
            print(f"{name} cost {free_mem-gc.mem_free()} bytes.")

        return wrapper

    return inner


def get_free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = "{0:.2f}%".format(F / T * 100)
    if not full:
        return P
    else:
        return "Total:{0} Free:{1} ({2})".format(T, F, P)


# def monitor_usage(func,*args,**kwargs):
#   def wrapped_func():
