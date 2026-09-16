import os
import importlib.util
import sys
from pathlib import Path


def exact_runtime_source(_: Path) -> str:
    """Return the reviewed contract bytes without rewriting runtime syntax."""
    return str(Path(__file__).parents[1] / "contracts" / "accordlens.py")


def deploy_exact(direct_deploy, tmp_path: Path):
    """Deploy exact source around gltest's Windows-only fd0 cleanup defect."""
    if importlib.util.find_spec("cloudpickle") is None:
        package = Path(sys.base_prefix) / "Lib" / "site-packages" / "cloudpickle"
        spec = importlib.util.spec_from_file_location(
            "cloudpickle", package / "__init__.py", submodule_search_locations=[str(package)]
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("cloudpickle is required for nondeterministic closure checks")
        module = importlib.util.module_from_spec(spec)
        sys.modules["cloudpickle"] = module
        spec.loader.exec_module(module)

    unlink = os.unlink

    def windows_safe_unlink(path):
        try:
            unlink(path)
        except PermissionError as error:
            if error.winerror != 32 or Path(path).parent != Path(os.getenv("TEMP", "")):
                raise

    os.unlink = windows_safe_unlink
    try:
        return direct_deploy(exact_runtime_source(tmp_path), sdk_version="v0.6.0-rc5")
    finally:
        os.unlink = unlink
