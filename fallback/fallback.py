from metaflow import user_step_decorator, current

@user_step_decorator
def fallback(step_name, flow, inputs=None, attributes=None):
    def _fallback_step(self):
        print("🛟 step failed: executing a fallback")
        var = attributes.get('indicator')
        if var:
            setattr(self, var, True)

    if current.retry_count == 0:
        yield
    else:
        yield _fallback_step
