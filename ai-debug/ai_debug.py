import os
import inspect
import traceback

from metaflow import user_step_decorator

PROMPT = """
I have a Metaflow step that is defined as follows:
```
{source}
```
It raised the following exception:
```
{stack_trace}
```
Provide suggestions how to fix it.
"""

@user_step_decorator
def ai_debug(step_name, flow, inputs=None, attributes=None):
    source = inspect.getsource(getattr(flow, step_name))
    try:
        yield
    except:
        print("❌ Step failed:")
        stack_trace = traceback.format_exc()
        prompt_gpt(PROMPT.format(source=source, stack_trace=stack_trace))
        raise

def prompt_gpt(prompt):
    import requests
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if OPENAI_API_KEY:
        print("🧠 Asking AI for help..")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=data)
        resp = response.json()["choices"][0]["message"]["content"]
        markdown = f"🧠💡 AI suggestion:\n\n{resp}"
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            console = Console()
            md = Markdown(markdown)
            console.print(md)
        except ImportError:
            print(markdown)
    else:
        print("Specify OPENAI_API_KEY for debugging help")
