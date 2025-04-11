# Command-line interface entry point
import argparse
import sys
import os
from pathlib import Path

# Import from the installed package
try:
    from notebook_cat import core
    from notebook_cat.config.defaults import (
        DEFAULT_SOURCE_LIMIT,
        PLUS_SOURCE_LIMIT,
        WORD_LIMIT,
        SUPPORTED_EXTENSIONS
    )
except ImportError:
    # Fall back to relative import for development
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.notebook_cat import core
    from src.notebook_cat.config.defaults import (
        DEFAULT_SOURCE_LIMIT,
        PLUS_SOURCE_LIMIT,
        WORD_LIMIT,
        SUPPORTED_EXTENSIONS
    )

def main():
    # Show all available file extensions in the help
    supported_ext_list = ", ".join(SUPPORTED_EXTENSIONS.keys())
    
    parser = argparse.ArgumentParser(
        description=f"Notebook Cat: Concatenate files for Google NotebookLM. "
                    f"Combines files from an input directory into larger source files, "
                    f"respecting a word limit per file ({WORD_LIMIT}) and a total source count limit.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # Show default values in help
    )
    
    # Required arguments
    parser.add_argument(
        "input_dir",
        help="Directory containing the files to process."
    )
    parser.add_argument(
        "output_dir",
        help="Directory where the concatenated source files will be saved."
    )
    
    # Source limit options
    limit_group = parser.add_argument_group('Source Limit Options')
    limit_group.add_argument(
        "-l", "--limit",
        type=int,
        default=DEFAULT_SOURCE_LIMIT,
        help=f"Maximum number of source files to create."
    )
    limit_group.add_argument(
        "--free-plan",
        action="store_const",
        const=DEFAULT_SOURCE_LIMIT,
        dest="limit",
        help=f"Use NotebookLM Free plan limit ({DEFAULT_SOURCE_LIMIT} sources)."
    )
    limit_group.add_argument(
        "--plus-plan",
        action="store_const",
        const=PLUS_SOURCE_LIMIT,
        dest="limit",
        help=f"Use NotebookLM Plus plan limit ({PLUS_SOURCE_LIMIT} sources)."
    )
    
    # File type options
    file_group = parser.add_argument_group('File Type Options')
    file_group.add_argument(
        "--extensions",
        type=str,
        default="txt,md,json",
        help=f"Comma-separated list of file extensions to process. Supported: {supported_ext_list}"
    )
    file_group.add_argument(
        "--json-path",
        type=str,
        help="Path to text field in JSON files (dot notation, e.g., 'segments.text')"
    )
    file_group.add_argument(
        "--max-files",
        type=int,
        help="Maximum number of input files to process (useful for large directories)"
    )
    
    # Processing options
    proc_group = parser.add_argument_group('Processing Options')
    proc_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without creating output files"
    )
    proc_group.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previously interrupted operation"
    )
    
    args = parser.parse_args()
    
    # Parse file extensions
    extensions = set(ext.strip() for ext in args.extensions.split(',') if ext.strip())
    
    # Check if all extensions are supported
    for ext in extensions:
        if ext not in SUPPORTED_EXTENSIONS:
            print(f"Warning: Extension '{ext}' is not in the supported list: {supported_ext_list}")
            print("It will be included but may not work as expected.")

    print("--- Notebook Cat ---")
    try:
        # Convert paths to absolute paths for clearer reporting
        input_dir = str(Path(args.input_dir).absolute())
        output_dir = str(Path(args.output_dir).absolute())
        
        core.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            source_limit=args.limit,
            dry_run=args.dry_run,
            file_extensions=extensions,
            json_path=args.json_path,
            resume=args.resume,
            max_files=args.max_files
        )
        print("\nSuccessfully finished.")
    except FileNotFoundError as e:
        print(f"\nError: File or directory not found: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"\nError: Permission denied: {e}")
        sys.exit(1)
    except Exception as e:
        # Provide a generic error message without detailed traceback
        print(f"\nAn error occurred during processing: {type(e).__name__}")
        print("Check input arguments and file permissions.")
        
        # Enable this for debugging but disable for production
        if 'NOTEBOOK_CAT_DEBUG' in os.environ:
            import traceback
            traceback.print_exc()
        
        sys.exit(1)

if __name__ == '__main__':
    main()
