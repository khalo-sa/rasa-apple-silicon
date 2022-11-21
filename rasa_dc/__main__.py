import argparse
from pathlib import Path

from rasa_dc import __version__
from rasa_dc.rasa_dc import convert


def main():
    parser = argparse.ArgumentParser(
        description="Convert a poetry-based pyproject.toml "
        "to a conda environment.yaml"
    )
    parser.add_argument(
        "-v",
        "--rasa_version",
        default="3.0.5",
        type=str,
        help="Rasa Version",
    )
    parser.add_argument(
        "-p",
        "--platform",
        default="docker",
        choices=["docker", "native"],
        type=str,
        help="Target Platform. Allowed values are 'docker' (default), or 'native'. ",
    )
    parser.add_argument(
        "--python",
        default="3.8",
        type=str,
        help="Target Python Version",
    )
    parser.add_argument(
        "-d",
        "--out_dir",
        default="./output",
        metavar="dir path",
        type=Path,
        help="directory to place generated output files",
    )
    parser.add_argument(
        "-f",
        "--out_file",
        # default="./rasa-conda-env.yml",
        metavar="out_file.yml",
        type=str,
        help="name of generated conda environment file",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="include dev dependencies",
    )
    parser.add_argument(
        "--only_conda",
        action="store_true",
        help="convert all pip deps to conda deps ignoring hardcoded rules",
    )
    parser.add_argument(
        "--extras",
        "-E",
        action="append",
        help="Add extra requirements",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s (version {__version__})"
    )
    args = parser.parse_args()

    convert(
        rasa_version=args.rasa_version,
        platform=args.platform,
        python_version=args.python,
        only_conda=args.only_conda,
        out_dir=args.out_dir,
        out_file=args.out_file,
        include_dev=args.dev,
        extras=args.extras,
    )


if __name__ == "__main__":
    main()
