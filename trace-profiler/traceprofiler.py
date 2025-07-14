import time
from metaflow import user_step_decorator
from collections import defaultdict

@user_step_decorator
def trace_profile(step_name, flow, inputs=None, attributes=None):
    flow.trace = TraceCollector
    yield
    del flow.trace
    flow.timings = TraceCollector.timings
    for name, timings in TraceCollector.timings.items():
        print(f"Trace: {name} - Total: {int(timings)}ms")

class TraceCollector(object):

    timings = defaultdict(int)

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        self.timings[self.name] += 1000 * (time.time() - self.start)

