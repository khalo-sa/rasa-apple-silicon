from ras.ras import convert
import argparse
from ras import __version__


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
        "-o",
        "--output",
        default="./rasa-conda-env.yml",
        metavar="YAML",
        type=str,
        help="environment.yaml output file.",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="include dev dependencies",
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

    convert(args.rasa_version, args.platform, include_dev=args.dev, extras=args.extras)


if __name__ == "__main__":
    main()
