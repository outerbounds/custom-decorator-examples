import tomllib

from metaflow import Config, FlowSpec, project, config_expr, schedule

from flow_linter import flow_linter

def parse_limits(x):
    return tomllib.loads(x)['limits']

@flow_linter
@project(name=config_expr('project.name'))
@schedule(cron=config_expr('project.schedule'))
class BaseFlow(FlowSpec):

    project_config = Config('project', default='project.toml', parser=tomllib.loads)
    limits = Config('limits', default='project.toml', parser=parse_limits)

    def number_of_rows(self):
        return len(self.table)
