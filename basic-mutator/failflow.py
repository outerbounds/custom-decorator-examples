import math
from metaflow import FlowSpec, step

from robust_flow import robust_flow

@robust_flow(fallback_indicator='failed')
class FailFlow(FlowSpec):

    @step
    def start(self):
        x = 3
        for i in range(5):
            math.sqrt(x - i)
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    FailFlow()
