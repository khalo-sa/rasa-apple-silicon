import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Tuple  # noqa

import toml
import yaml

import rasa_dc.poetry_semver as poetry_semver
from rasa_dc import __version__
from rasa_dc.poetry_semver.version import Version


def load_version_file(platform: str, rasa_version: str) -> dict:
    version_dir = Path(__file__).parent.resolve() / "recipes"
    version_file = version_dir / f"{platform}-{rasa_version}.yaml"
    if not version_file.exists():
        print(
            f"Rasa version {rasa_version} not supported for this platform, available recipes:"
        )
        for file in version_dir.glob(f"{platform}-*.yaml"):
            print(f"- {file.stem}")
        exit(-1)

    with open(version_file) as f:
        env_stub = yaml.load(f, Loader=yaml.FullLoader)

    env_stub["name"] = "rasa" + "".join([c for c in rasa_version if c.isdigit()])
    env_stub["conda"], env_stub["pip"] = {}, {}

    return env_stub


def convert(
    rasa_version: str = "3.0.5",
    platform: str = "docker",
    include_dev: bool = False,
    python_version: str = "3.8",
    only_conda: bool = False,
    out_dir: Path = Path("./output"),
    out_file: str = None,
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

    out_dir.mkdir(exist_ok=True)

    env_stub = load_version_file(platform, rasa_version)
    only_conda_suffix = "_only_conda" if only_conda else ""
    out_file = (
        out_file
        if out_file
        else f"rasa_{rasa_version}_{platform}{only_conda_suffix}_env.yml"
    )
    PYPROJECT_TOML = Path(f"{out_dir}/rasa_{rasa_version}_pyproject.toml")
    CONDA_ENV = Path(f"{out_dir}/{out_file}")

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

    env_obj = create_env_obj(env_stub, poetry_dependencies, python_version, only_conda)
    yaml_str = to_yaml_string(env_obj)
    with open(CONDA_ENV, "w") as f:
        f.write(yaml_str)
    print(f"Created env file: {CONDA_ENV}")


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
        # print("Complex version constraints are not supported at the moment.")
        converted = " # " + str(spec)
    else:
        raise ValueError(f"dependency '{name}': unknown spec '{spec}' [{type(spec)}]")
    return converted


def create_env_obj(
    env_stub: dict,
    poetry_dependencies: Mapping,
    python_version: str,
    only_conda: bool = False,
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
    # resolved = (
    #     {*env_stub["conda"].keys(), *env_stub["pip"].keys()} if not only_conda else {}
    # )

    add, modify = (
        env_stub.pop("add"),
        env_stub.pop("modify"),
    )

    # add new deps
    for name, dep_d in add.items():
        git = dep_d.get("git")
        if git:
            env_stub["pip"][git] = None
        else:
            source = dep_d["source"]
            version = dep_d.get("version")
            version = convert_version(name, version) if version else ""
            env_stub[source][name] = version

    # add and optionally modify original deps
    dependency_items = list()
    for name, constraint in poetry_dependencies.items():
        if isinstance(constraint, list):
            # e.g. numpy
            for _constraint in constraint:
                dependency_items.append((name, _constraint))
        else:
            dependency_items.append((name, constraint))

    for name, constraint in dependency_items:

        if isinstance(constraint, str):
            pip_version = constraint
        elif isinstance(constraint, dict):
            if constraint.get("optional", False):
                continue

            if "python" in constraint:
                spec = poetry_semver.parse_constraint(constraint["python"])
                if not spec.allows(Version.parse(python_version)):
                    continue

            if "markers" in constraint:
                print(f"skipped constraint with markers: {name}", constraint)
                continue

            if "git" in constraint:
                git = constraint["git"]
                tag = constraint["tag"]
                name = f"git+{git}@{tag}#egg={name}"

            if "version" in constraint:
                pip_version = constraint["version"]

            if "extras" in constraint:
                name = f"{name}[{','.join(constraint['extras'])}]"

        else:
            raise ValueError(
                f"This converter only supports normal dependencies and "
                f"git dependencies. No path, url, python restricted, "
                f"environment markers or multiple constraints. In your "
                f'case, check the "{name}" dependency. Sorry.'
            )

        name: str
        pip_version: str
        version: str = None
        source: str = "pip"

        if name in modify:
            # dependency has been manually resolved
            dep = modify[name]
            source = dep["source"]
            version = dep.get("version")

        if not version:
            version = convert_version(name, pip_version)

        env_stub[source][name] = version

    if only_conda:
        env_stub["conda"].update(env_stub["pip"])
        env_stub["pip"] = {}

    return env_stub


def to_yaml_string(env_object: dict) -> str:
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
    deps = []
    for name, version in sorted(env_object["conda"].items()):
        version = version or ""
        line = f"  - {name}{version}"
        line = f"# {line}" if name in env_object["remove"] else line
        deps.append(line)
    if env_object["pip"]:
        deps.append("  - pip")
        deps.append("  - pip:")
    for name, version in sorted(env_object["pip"].items()):
        version = version or ""
        line = f"    - {name}{version}"
        line = f"# {line}" if name in env_object["remove"] else line
        deps.append(line)
    deps_str = "\n".join(deps)

    channels_str = []
    for channel in env_object["channels"]:
        line = f"  - {channel}"
        channels_str.append(line)
    channels_str = "\n".join(channels_str)

    date_str = datetime.now().strftime("%c")
    conda_yaml = f"""
###############################################################################
# NOTE: This file has been auto-generated by rasa-apple-silicon
#       version = {__version__}
#       date: {date_str}
###############################################################################
name: {env_object["name"]}
channels:
{channels_str}
dependencies:
{deps_str}
""".lstrip()
    return conda_yaml
