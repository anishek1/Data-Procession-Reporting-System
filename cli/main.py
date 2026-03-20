"""
CLI Entry Point

Command-line interface for DPRS using argparse.
"""


import argparse
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_processor import load_file, compute_statistics
from reporting.report_generator import ReportGenerator
from utils.logger import logger
from core.exceptions import DPRSException 

def main():
    # CLI Command Interface [cite: 50]
    parser = argparse.ArgumentParser(description="Data Processing & Reporting System (DPRS)")
    subparsers = parser.add_subparsers(dest="command", help="System operations")

    # Command: load --file data.csv [cite: 56, 167]
    load_parser = subparsers.add_parser('load')
    load_parser.add_argument('--file', required=True, help="Path to input data file")

    # Command: summary [cite: 57, 172]
    subparsers.add_parser('summary')

    # Command: report --type text [cite: 58]
    report_parser = subparsers.add_parser('report')
    report_parser.add_argument('--type', choices=['text'], default='text')

    # Command: export --format json [cite: 59]
    export_parser = subparsers.add_parser('export')
    export_parser.add_argument('--format', choices=['json'], default='json')

    args = parser.parse_args()
    
    # Initialization
    try:
        generator = ReportGenerator()
    except DPRSException as e:
        logger.error(f"Operation failed: {e}") 
        print(f"System Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == 'load':
            logger.info(f"Loading file: {args.file}") 
            load_file(args.file)
            print(f"Data successfully loaded from {args.file}")

        elif args.command == 'summary':
            stats = compute_statistics() 
            generator.display_summary_to_console(stats)

        elif args.command == 'report':
            stats = compute_statistics()
            path = generator.generate_text_report(stats)
            print(f"Report saved to: {path}")

        elif args.command == 'export':
            stats = compute_statistics()
            path = generator.generate_json_report(stats)
            print(f"JSON data exported to: {path}")
        
        else:
            parser.print_help() 

    except (DPRSException, ValueError) as e:
        # Custom Error Handling [cite: 10, 156]
        logger.error(f"Operation failed: {e}") 
        print(f"System Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
