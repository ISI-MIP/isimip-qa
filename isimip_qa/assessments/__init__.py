import importlib
import inspect
import os
from pathlib import Path

from ..models import Assessment

path = Path(__file__).parent

# gather assessment classes from the python files in this directory
assessment_classes = set()
for root, dirs, files in os.walk(path):
    for file_name in sorted(files):
        file_path = path / root / file_name
        if file_path.suffix == '.py' and file_path.name != '__init__.py':
            parts = file_path.relative_to(path.parent.parent).with_suffix('').parts
            module_name = '.'.join(parts)
            module = importlib.import_module(module_name)
            for module_class_name, module_class in inspect.getmembers(module, inspect.isclass):
                if module_class != Assessment and issubclass(module_class, Assessment):
                    assessment_classes.add(module_class)
