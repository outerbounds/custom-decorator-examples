import os
from metaflow import Flow, user_step_decorator, current

@user_step_decorator
def memoize(step_name, flow, inputs=None, attributes=None):
    artifact = attributes['artifact']
    reset = attributes.get('reset')
    if reset and getattr(flow, reset, False):
        print("⚙️  memoized results disabled - running the step")
        yield
    else:
        try:
            run = Flow(current.flow_name).latest_successful_run
            previous_value = run[step_name].task[artifact].data
        except:
            print("⚙️ previous results not found - running the step")
            yield
        else:
            print(f"✅ reusing results from a previous run {run.id}")
            setattr(flow, artifact, previous_value)
            yield {}
