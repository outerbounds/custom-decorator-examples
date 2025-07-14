import math
from metaflow import FlowSpec, step

from ai_debug import ai_debug

class FailFlow(FlowSpec):

    @ai_debug
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
