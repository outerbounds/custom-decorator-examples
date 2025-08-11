# Namespaced Triggers for Metaflow

This directory contains the `@namespaced_trigger` decorator and example flows demonstrating how to create event-driven workflows with automatic event name namespacing in Metaflow. On popular demand, this feature will be shipped as a part of Metaflow in the near future but for now, this is a workaround to attain similar functionality.

The intention of exposing the `@namespaced_trigger` decorator is to enable automatic namespacing of events raised by flows using the `@project` decorator. When an upstream flow raises an event, the decorator ensures it's properly namespaced with the project and branch information. Downstream flows can then subscribe to these namespaced events to create coordinated workflows. For example, if an upstream flow in project `foo` and branch `bar` raises an event called `food`, a downstream flow can listen specifically for that event within the same project and branch namespace. This ensures events are properly scoped and only trigger the intended downstream flows.


## Overview

The `@namespaced_trigger` decorator enables organized event-driven workflows by automatically formatting event names with project and branch information. This ensures events are properly scoped and prevents conflicts between different environments and branches.

## Event Name Format

Events are automatically namespaced using the pattern:
```
{project_name}.{branch}.{event_name}
```

### Branch Formats:
- **Production branches**: `prod.{branch_name}` (when `production: true`)
- **Test branches**: `test.{branch_name}` (when `production: false`)
- **User branches**: `user.{username}` (when no branch specified and not production)

## Files

- **`namespaced_trigger.py`**: The main decorator implementation
- **`parent_flow.py`**: Example upstream flow that publishes events
- **`child_flow.py`**: Example downstream flow that listens for events
- **`setup_flow.sh`**: Script demonstrating various deployment scenarios

## Usage

### 1. Upstream Flow (Event Publisher)

```python
from metaflow import FlowSpec, step, project, Config
from namespaced_trigger import namespaced_trigger

@project(name="foo")
class HelloFlowUpstream(FlowSpec):
    project = Config("project", default_value={})

    @step
    def start(self):
        print("Hello World!")
        self.next(self.end)

    @step
    def end(self):
        namespaced_trigger.raise_event("food", safe_publish=True)

if __name__ == "__main__":
    HelloFlowUpstream()
```

### 2. Downstream Flow (Event Listener)

```python
from metaflow import FlowSpec, step, project, Config
from namespaced_trigger import namespaced_trigger

@namespaced_trigger(event="food")
@project(name="foo")
class HelloFlowDownstream(FlowSpec):
    project = Config("project", default_value={})

    @step
    def start(self):
        print("Triggered by namespaced event!")
        self.next(self.end)

    @step
    def end(self):
        print("Flow complete!")

if __name__ == "__main__":
    HelloFlowDownstream()
```

## Configuration

### Required Setup

1. **Config Object**: Flow must have a `Config` object (default name: "project")
2. **Project Decorator**: Flow should use `@project` decorator or provide project name in config
3. **Event Specification**: Must specify either `event` or `events` parameter

### Configuration Priority

- Config values override `@project` decorator values (except for name)
- Branches can only be overridden via config, not CLI flags (`--branch`, `--production`)
- Project name can be set in either `@project` decorator or config

## Deployment Examples

### Scenario 1: Production Branch Deployment

**Deploy upstream flow:**
```bash
python parent_flow.py --branch bar --production argo-workflows create
```

**Deploy downstream flow:**
```bash
python child_flow.py --config-value project '{"branch": "bar", "production": true}' argo-workflows create
```

**Trigger upstream flow:**
```bash
python parent_flow.py --branch bar --production argo-workflows trigger
```

**Result**: Event name becomes `foo.prod.bar.food`

### Scenario 2: Test Branch Deployment

**Deploy upstream flow:**
```bash
python parent_flow.py --branch baaz argo-workflows create
```

**Deploy downstream flow:**
```bash
python child_flow.py --config-value project '{"branch": "baaz"}' argo-workflows create
```

**Trigger upstream flow:**
```bash
python parent_flow.py --branch baaz argo-workflows trigger
```

**Result**: Event name becomes `foo.test.baaz.food`

### Scenario 3: User Branch Deployment

**Deploy upstream flow:**
```bash
python parent_flow.py argo-workflows create
```

**Deploy downstream flow:**
```bash
python child_flow.py argo-workflows create
```

**Trigger upstream flow:**
```bash
python parent_flow.py argo-workflows trigger
```

**Result**: Event name becomes `foo.user.{username}.food`

## Decorator Parameters

```python
@namespaced_trigger(
    event="event_name",           # Single event to listen for
    events=["event1", "event2"],  # Multiple events to listen for
    options={},                   # Additional trigger options
    config_name="project",        # Config object name (default: "project")
    show_warnings=True           # Show warnings (default: True)
)
```

## Event Publishing

From upstream flows, publish events using:

```python
# Basic publishing
namespaced_trigger.raise_event("food")

# Safe publishing (recommended)
namespaced_trigger.raise_event("food", safe_publish=True)

# With payload
namespaced_trigger.raise_event("food", payload={"key": "value"}, safe_publish=True)
```

## Important Notes

1. **Cannot combine with @trigger**: The `@namespaced_trigger` and `@trigger` decorators cannot be used on the same flow
2. **Config vs CLI**: Branch and production settings must be provided via config values, not CLI flags for any flow decorated withe `@namespaced_trigger`
3. **Event Name Sanitization**: Event names are automatically sanitized to contain only alphanumeric characters, underscores, hyphens, and dots
4. **Project Context**: Events are automatically namespaced when published from flows with project context. Project name is required to be set either in the `@project` decorator or in the `Config` object.
5. **Config Object**: Ensure your flow which has the `@namespaced_trigger` decorator has a `Config` object with the correct name


## Testing

Run the provided setup script to test different scenarios:

```bash
bash setup_flow.sh
```
