import time
from metaflow import FlowSpec, step

from traceprofiler import trace_profile

class TracingFlow(FlowSpec):

    @trace_profile
    @step
    def start(self):
        for i in range(10):
            with self.trace('database access'):
                time.sleep(0.1)
        with self.trace('process data'):
            time.sleep(0.5)
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    TracingFlow()
