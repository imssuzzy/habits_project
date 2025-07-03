import pathlib
import pkgutil
from importlib import import_module
from importlib.util import find_spec
import importlib


def _modules(postfix="") -> list:
    return [
        import_module(f".{name}{postfix}", package=__name__)
        for (_, name, _) in pkgutil.iter_modules([str(pathlib.Path(__file__))])
        if find_spec(f".{name}{postfix}", package=__name__)
    ]


def detect_models():
    app_dir = pathlib.Path(__file__).parent
    for path in app_dir.glob("**/models.py"):
        rel = path.relative_to(app_dir.parent)
        module = ".".join(rel.with_suffix("").parts)
        importlib.import_module(module)
