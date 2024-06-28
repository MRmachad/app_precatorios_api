import importlib
import os
import pkgutil
from typing import Any, List, Type


def import_submodules(package_name: str) -> None:
    package = importlib.import_module(package_name)
    package_path = os.path.dirname(package.__file__)
    for _, name, is_pkg in pkgutil.iter_modules([package_path]):
        full_name = f"{package_name}.{name}"
        importlib.import_module(full_name)
        if is_pkg:
            import_submodules(full_name)

def get_subclasses( cls: Type[Any]) -> List[Any]:
    subclasses = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses.update(get_subclasses(subclass))
    return subclasses