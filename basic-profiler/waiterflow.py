import time
from metaflow import FlowSpec, step

from myprofiler import my_profile

class WaiterFlow(FlowSpec):

    @step
    def start(self):
        self.waiters = list(range(5))
        self.next(self.wait, foreach='waiters')

    @my_profile
    @step
    def wait(self):
        self.duration = self.input / 10
        print(f"💤 Sleeping for {self.duration}s")
        time.sleep(self.duration)
        self.next(self.join)

    @step
    def join(self, inputs):
        self.total = sum(inp.duration for inp in inputs)
        print(f"Slept {self.total}s in total")
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    WaiterFlow()
