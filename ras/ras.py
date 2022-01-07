from pathlib import Path
import urllib.request
from datetime import datetime
from typing import Iterable, Mapping, Optional, TextIO, Tuple  # noqa

import semver
import toml

from ras import __version__
import ras.poetry_semver as poetry_semver
import yaml


def get_hardcoded(rasa_version: str) -> dict:
    if semver.compare(rasa_version, "3.0.3") in [0, 1] or semver.compare(
        rasa_version, "3.0.4"
    ) in [0, -1]:
        hardcoded = {
            "conda": {
                "python": "==3.8.12",
                "h5py": "==3.1.0",
                "numpy": "==1.19.5",
                "scikit-learn": "==0.24.2",
                "uvloop": "==0.14",
                "ruamel.yaml": ">=0.16.5,<0.17.0",
                "dask": "==2021.11.2",
                "aiohttp": ">=3.6,<3.7.4",
            },
            "pip": {},
            "channels": ["conda-forge", "noarch"],
            "name": "rasa" + "".join([c for c in rasa_version if c.isdigit()]),
        }
    else:
        raise ValueError(f"Version {rasa_version} not supported yet")

    return hardcoded


def convert(
    rasa_version: str = "3.0.4",
    include_dev: bool = False,
    extras: Optional[Iterable[str]] = None,
) -> str:
    """Convert a pyproject.toml file to a conda environment YAML

    This is the main function of poetry2conda, where all parsing, converting,
    etc. gets done.

    Parameters
    ----------
    file
        A file-like object containing a pyproject.toml file.
    include_dev
        Whether to include the dev dependencies in the resulting environment.
    extras
        The name of extras to include in the output.  Can be None or empty
        for no extras.

    Returns
    -------
    The contents of an environment.yaml file as a string.

    """

    yaml_obj_stub = get_hardcoded(rasa_version)

    PYPROJECT_TOML = Path(f"./output/rasa_{rasa_version}_pyproject.toml")
    CONDA_ENV = Path(f"./output/rasa_{rasa_version}_env.yml")

    with urllib.request.urlopen(
        f"https://github.com/RasaHQ/rasa/raw/{rasa_version}/pyproject.toml"
    ) as response:
        response_str = response.read().decode()

        with open(PYPROJECT_TOML, "w") as f:
            f.write(response_str)

        pyproject_toml = toml.loads(response_str)

    poetry_config = pyproject_toml.get("tool", {}).get("poetry", {})
    assert poetry_config

    if extras is None:
        extras = []

    poetry_dependencies = poetry_config.get("dependencies", {})
    poetry_extras = poetry_config.get("extras", {})
    # We mark the items listed in the selected extras as non-optional
    for extra in extras:
        for item in poetry_extras[extra]:
            dep = poetry_dependencies[item]
            if isinstance(dep, dict):
                dep["optional"] = False

    yaml_obj = create_yaml_obj(yaml_obj_stub, poetry_dependencies)
    yaml_str = to_yaml_string(yaml_obj)

    with open(CONDA_ENV, "w") as f:
        f.write(yaml_str)


def convert_version(name: str, spec_str: str) -> str:
    """Convert a poetry version spec to a conda-compatible version spec.

    Poetry accepts tilde and caret version specs, but conda does not support
    them. This function uses the `poetry-semver` package to parse it and
    transform it to regular version spec ranges.

    Parameters
    ----------
    spec_str
        A poetry version specification string.

    Returns
    -------
    The same version specification without tilde or caret.

    """
    # print(f"Converting '{spec_str}'")
    spec = poetry_semver.parse_constraint(spec_str)
    if isinstance(spec, poetry_semver.Version):
        converted = f"=={str(spec)}"
    elif isinstance(spec, poetry_semver.VersionRange):
        converted = str(spec)
    elif isinstance(spec, poetry_semver.VersionUnion):
        # raise ValueError("Complex version constraints are not supported at the moment.") # noqa
        print("Complex version constraints are not supported at the moment.")
        converted = " # " + str(spec)
    else:
        raise ValueError(f"dependency '{name}': unknown spec '{spec}' [{type(spec)}]")
    return converted


def create_yaml_obj(
    yaml_obj: dict, poetry_dependencies: Mapping
) -> Tuple[Mapping, Mapping]:
    """Organize and apply conda constraints to dependencies

    Parameters
    ----------
    poetry_dependencies
        A dictionary with dependencies as declared with poetry.
    conda_constraints
        A dictionary with conda constraints as declared with poetry2conda.

    Returns
    -------
    A tuple with the modified dependencies and the dependencies that must be
    installed with pip.

    """

    # 2. Now do the conversion
    resolved = {*yaml_obj["conda"].keys(), *yaml_obj["pip"].keys()}
    for name, constraint in poetry_dependencies.items():
        if name in resolved:
            # dependency has been manually resolved
            continue
        elif isinstance(constraint, str):
            yaml_obj["pip"][name] = convert_version(name, constraint)
        elif isinstance(constraint, dict):
            if constraint.get("optional", False):
                continue
            if "git" in constraint:
                git = constraint["git"]
                tag = constraint["tag"]
                yaml_obj["pip"][f"git+{git}@{tag}#egg={name}"] = None
            elif "version" in constraint:
                yaml_obj["pip"][name] = convert_version(name, constraint["version"])
            else:
                raise ValueError(
                    f"This converter only supports normal dependencies and "
                    f"git dependencies. No path, url, python restricted, "
                    f"environment markers or multiple constraints. In your "
                    f'case, check the "{name}" dependency. Sorry.'
                )
        else:
            raise ValueError(
                f"This converter only supports normal dependencies and "
                f"git dependencies. No multiple constraints. In your "
                f'case, check the "{name}" dependency. Sorry.'
            )

    return yaml_obj


def to_yaml_string(yaml_object: dict) -> str:
    """Converts dependencies to a string in YAML format.

    Note that there is no third party library to manage the YAML format. This is
    to avoid an additional package dependency (like pyyaml, which is already
    one of the packages that behaves badly in conda+pip mixed environments).
    But also because our YAML is very simple

    Parameters
    ----------
    env_name
        Name for the conda environment.
    dependencies
        Regular conda dependencies.
    pip_dependencies
        Pure pip dependencies.

    Returns
    -------
    A string with an environment.yaml definition usable by conda.

    """
    deps_str = []
    for name, version in yaml_object["conda"].items():
        version = version or ""
        deps_str.append(f"  - {name}{version}")
    if yaml_object["pip"]:
        deps_str.append("  - pip")
        deps_str.append("  - pip:")
    for name, version in yaml_object["pip"].items():
        version = version or ""
        deps_str.append(f"    - {name}{version}")
    deps_str = "\n".join(deps_str)

    date_str = datetime.now().strftime("%c")
    conda_yaml = f"""
###############################################################################
# NOTE: This file has been auto-generated by rasa-apple-silicon
#       version = {__version__}
#       date: {date_str}
###############################################################################
name: {yaml_object["name"]}
dependencies:
{deps_str}
""".lstrip()
    return conda_yaml
