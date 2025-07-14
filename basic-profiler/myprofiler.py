import time
from metaflow import user_step_decorator, current


@user_step_decorator
def my_profile(step_name, flow, inputs=None, attributes=None):
    start = time.time()
    yield
    duration = 1000 * (time.time() - start)
    print(f"⏰ Task [{current.pathspec}] completed in {duration:.1f}ms")
