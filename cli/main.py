"""
CLI Entry Point

Command-line interface for DPRS using argparse.
"""

import argparse


def main():
    """Entry point for the DPRS command-line interface."""
    parser = argparse.ArgumentParser(
        description="Data Processing & Reporting System",
        prog="dprs"
    )
    # Subparsers will be added in Sprint 2
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
