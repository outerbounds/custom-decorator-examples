import time
import json
from metaflow import user_step_decorator
from collections import defaultdict

@user_step_decorator
def stats_profile(step_name, flow, inputs=None, attributes=None):
    start = time.time()
    yield
    duration = int(1000 * (time.time() - start))

    if not hasattr(flow, "timings"):
        flow.timings = defaultdict(list)
    if inputs:
        for inp in inputs:
            for step, timings in inp.timings.items():
                flow.timings[step].extend(timings)
    flow.timings[step_name].append(duration)
    if step_name == "end" and not attributes.get("silent"):
        print_results(flow.timings)

def print_results(all_timings):
    print("📊 Step timings")
    print(f"{'Step':<20}{'P10 (ms)':<15}{'Median (ms)':<15}{'P90 (ms)':<15}")
    for step, timings in all_timings.items():
        timings.sort()
        n = len(timings)
        p10 = timings[int(n * 0.1)]
        median = timings[n // 2]
        p90 = timings[int(n * 0.9)]
        print(f"{step:<20}{p10:<15}{median:<15}{p90:<15}")
