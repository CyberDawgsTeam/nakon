"""
Auto-discovers all service installer modules in this directory and
builds a REGISTRY dict mapping lowercase service names -> install functions.

To add a new service:
  1. Create services/<name>.py
  2. Define SERVICE_NAME = "name"  (or a list of aliases, e.g. ["apache", "httpd"])
  3. Define install(client, password)
  That's it — it will be picked up automatically on next run.
"""

import os
import importlib

# Maps lowercase service/alias name -> install(client, password) callable
REGISTRY: dict = {}


def _load():
    services_dir = os.path.dirname(__file__)
    for filename in sorted(os.listdir(services_dir)):
        if not filename.endswith(".py") or filename in ("__init__.py", "base.py"):
            continue
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f"services.{module_name}")
        except ImportError as e:
            print(f"[registry] Could not load services/{filename}: {e}")
            continue
        if not (hasattr(module, "SERVICE_NAME") and hasattr(module, "install")):
            continue
        names = (
            module.SERVICE_NAME
            if isinstance(module.SERVICE_NAME, list)
            else [module.SERVICE_NAME]
        )
        for name in names:
            REGISTRY[name.lower()] = module.install
    print(f"[registry] Loaded {len(REGISTRY)} service(s): {', '.join(sorted(REGISTRY))}")


_load()
