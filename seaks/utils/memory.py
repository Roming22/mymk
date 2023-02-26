import gc


def free_memory(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            # print("Garbage collect !")
            gc.collect()
            print(f"\n\nMemory after instanciation of {name}: ", get_usage(True))

        return wrapper

    return inner


def check_memory(name):
    total_mem = gc.mem_free() + gc.mem_alloc()

    def inner(func):
        def wrapper(*args, **kwargs):
            used_mem = gc.mem_alloc()
            if used_mem / total_mem >= 0.8:
                # print("Garbage collect !!")
                gc.collect()
            result = func(*args, **kwargs)
            return result

        return wrapper

    return inner


def memory_cost(name):
    total_mem = gc.mem_free() + gc.mem_alloc()

    def inner(func):
        def wrapper(*args, **kwargs):
            # print("Garbage collect !!!")
            gc.collect()
            free_mem = gc.mem_free()
            result = func(*args, **kwargs)
            # print("Garbage collect !4!")
            gc.collect()
            mem_used = free_mem - gc.mem_free()
            print(f"{name} cost {mem_used} bytes ({mem_used*100/(total_mem):02f}%).")
            return result

        return wrapper

    return inner


def get_usage(full=False):
    # print("Garbage collect !5!")
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = "{0:.2f}%".format(A / T * 100)
    if not full:
        return A
    else:
        return "Total:{0} Used:{1} ({2})".format(T, A, P)
