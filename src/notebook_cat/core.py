# Core logic for counting words, grouping files, and concatenating
import os
import math
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set

from .config.defaults import (
    WORD_LIMIT,
    DEFAULT_SOURCE_LIMIT,
    SUPPORTED_EXTENSIONS,
    RESUME_MARKER_FILE,
    JSON_TEXT_FIELDS
)

def count_words_in_file(filepath: Path, json_path: Optional[str] = None) -> int:
    """
    Counts the words in a file (supporting multiple file types).
    
    Args:
        filepath: Path to the file
        json_path: Optional path to text field in JSON files
        
    Returns:
        Word count
    """
    try:
        # Get file extension (lowercase)
        ext = filepath.suffix.lower()[1:]  # Remove the dot
        
        # Handle different file types
        if ext == 'json':
            content = extract_text_from_json(filepath, json_path)
        else:  # For .txt and .md and any other text-based formats
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Count words (common for all file types)
        words = content.split()
        return len(words)
    except Exception as e:
        print(f"Error reading or counting words in {filepath}: {e}")
        return 0  # Treat files with errors as having 0 words

def extract_default_text_from_json(data):
    """
    Extract text content from JSON data using default extraction methods.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        Extracted text content as a string
    """
    # Case 1: Simple array of strings
    if isinstance(data, list) and all(isinstance(item, str) for item in data):
        return "\n\n".join(data)
    
    # Case 2: Object with text-like fields
    if isinstance(data, dict):
        for field in JSON_TEXT_FIELDS:
            if field in data and isinstance(data[field], str):
                return data[field]
        
        # Case 3: Look for arrays of objects with text fields
        for field, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                texts = []
                for item in value:
                    for text_field in JSON_TEXT_FIELDS:
                        if text_field in item and isinstance(item[text_field], str):
                            texts.append(item[text_field])
                            break
                if texts:
                    return "\n\n".join(texts)
    
    # If nothing worked, convert the whole thing to a string
    return json.dumps(data, indent=2)

def extract_text_from_json(filepath: Path, json_path: Optional[str] = None) -> str:
    """
    Extract text content from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        json_path: Optional dot-notation path to text field (e.g., "segments.text")
        
    Returns:
        Extracted text content as a string
    """
    try:
        # Set file size limit to prevent JSON bomb attacks (50MB)
        file_size_limit = 50 * 1024 * 1024  # 50MB
        
        # Check file size before loading
        file_size = filepath.stat().st_size
        if file_size > file_size_limit:
            print(f"Warning: JSON file {filepath} exceeds size limit of 50MB. Skipping.")
            return ""
            
        with open(filepath, 'r', encoding='utf-8') as f:
            # Use json.load with size limit to prevent DoS attacks
            data = json.load(f)
        
        # If a specific JSON path is provided, use it
        if json_path:
            # Validate JSON path to prevent traversal vulnerabilities
            valid_path = True
            for part in json_path.split('.'):
                if not (part.isalnum() or part.isdigit()):
                    print(f"Warning: Invalid JSON path format: {json_path}. Using default extraction.")
                    valid_path = False
                    break
            
            if valid_path:
                parts = json_path.split('.')
                current = data
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    elif isinstance(current, list) and part.isdigit():
                        current = current[int(part)]
                    else:
                        return ""  # Path not found
                
                # Handle different types that the path might resolve to
                if isinstance(current, str):
                    return current
                elif isinstance(current, list):
                    # If it's a list of strings, join them
                    if all(isinstance(item, str) for item in current):
                        return "\n\n".join(current)
                    # If it's a list of objects with text fields, extract and join
                    texts = []
                    for item in current:
                        if isinstance(item, dict):
                            for field in JSON_TEXT_FIELDS:
                                if field in item and isinstance(item[field], str):
                                    texts.append(item[field])
                                    break
                    return "\n\n".join(texts)
                elif isinstance(current, dict):
                    # Extract text from known text fields
                    for field in JSON_TEXT_FIELDS:
                        if field in current and isinstance(current[field], str):
                            return current[field]
                    
                    # No known text field found, convert to string
                    return json.dumps(current, indent=2)
                else:
                    # Convert to string as fallback
                    return str(current)
            else:
                # If path is invalid, use default extraction
                return extract_default_text_from_json(data)
        
        # No path specified, try to automatically extract text
        return extract_default_text_from_json(data)
    
    except Exception as e:
        print(f"Error extracting text from JSON file {filepath}: {e}")
        return ""

def get_files_by_extensions(directory: Path, extensions: Set[str], limit: Optional[int] = None) -> List[Path]:
    """
    Gets a list of files with the specified extensions in the directory.
    
    Args:
        directory: Directory to search
        extensions: Set of file extensions to include (e.g., {"txt", "md", "json"})
        limit: Optional maximum number of files to return
        
    Returns:
        List of matching file paths
    """
    if not directory.is_dir():
        raise ValueError(f"Input path {directory} is not a valid directory.")
    
    all_files = []
    for ext in extensions:
        # Either use the pattern from config or build a simple one
        pattern = SUPPORTED_EXTENSIONS.get(ext, f"*.{ext}")
        matching_files = list(directory.glob(pattern))
        all_files.extend(matching_files)
        print(f"Found {len(matching_files)} files with extension '{ext}' in {directory}")
    
    # Sort files by name for consistent results
    all_files.sort()
    
    # Apply limit if specified
    if limit is not None and limit > 0:
        all_files = all_files[:limit]
        print(f"Limited to {limit} files, returning {len(all_files)}")
    
    return all_files


def group_files(files_with_counts: List[Tuple[Path, int]], source_limit: int) -> Tuple[List[List[Tuple[Path, int]]], List[Tuple[Path, int]]]:
    """Groups files into lists, respecting the word limit per group and the total source limit."""
    # Sort files by word count, descending. This might help pack larger files first.
    sorted_files = sorted(files_with_counts, key=lambda item: item[1], reverse=True)

    groups: List[List[Tuple[Path, int]]] = []
    group_word_counts: List[int] = []
    ungrouped_files: List[Tuple[Path, int]] = []

    for file_path, word_count in sorted_files:
        if word_count == 0:
            print(f"Skipping file {file_path.name} due to read error or empty content.")
            continue

        if word_count > WORD_LIMIT:
            print(f"Warning: File {file_path.name} ({word_count} words) exceeds the single source word limit of {WORD_LIMIT}. It will be skipped.")
            ungrouped_files.append((file_path, word_count))
            continue

        placed = False
        # Try to place the file in an existing group
        for i in range(len(groups)):
            if group_word_counts[i] + word_count <= WORD_LIMIT:
                groups[i].append((file_path, word_count))
                group_word_counts[i] += word_count
                placed = True
                break

        # If it wasn't placed and we have room for a new group
        if not placed:
            if len(groups) < source_limit:
                groups.append([(file_path, word_count)])
                group_word_counts.append(word_count)
                placed = True
            else:
                # Cannot place the file, exceeds source limit
                print(f"Warning: Could not place file {file_path.name} ({word_count} words) without exceeding the source limit of {source_limit}. It will be skipped.")
                ungrouped_files.append((file_path, word_count))

    return groups, ungrouped_files

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent injection attacks.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Replace potentially dangerous characters with underscores
    return ''.join(c if c.isalnum() or c in '._- ' else '_' for c in filename)

def concatenate_files(group: List[Tuple[Path, int]], output_filepath: Path):
    """Concatenates files from a group into a single output file with separators."""
    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            for file_path, word_count in group:
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        # Sanitize filename before including in output
                        safe_filename = sanitize_filename(file_path.name)
                        outfile.write(f"--- START FILE: {safe_filename} ({word_count} words) ---\n\n")
                        outfile.write(content)
                        outfile.write(f"\n\n--- END FILE: {safe_filename} ---\n\n")
                except Exception as e:
                    print(f"Error reading file {file_path} during concatenation: {e}")
                    # Sanitize filename in error message
                    safe_filename = sanitize_filename(file_path.name)
                    outfile.write(f"--- ERROR: Could not read file {safe_filename} ---\n\n")
        print(f"Successfully created concatenated file: {output_filepath.name}")
    except Exception as e:
        print(f"Error writing output file {output_filepath}: {e}")

def save_resume_state(output_path: Path, groups_processed: int, files_processed: Set[str]):
    """
    Save resume state to allow continuing an interrupted operation.
    
    Args:
        output_path: Output directory path
        groups_processed: Number of groups already processed
        files_processed: Set of file paths that have been processed
    """
    resume_file = output_path / RESUME_MARKER_FILE
    try:
        state = {
            'groups_processed': groups_processed,
            'files_processed': list(files_processed)  # Convert set to list for JSON serialization
        }
        with open(resume_file, 'w', encoding='utf-8') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Warning: Could not save resume state: {e}")

def load_resume_state(output_path: Path) -> Tuple[int, Set[str]]:
    """
    Load resume state from previous interrupted operation.
    
    Args:
        output_path: Output directory path
        
    Returns:
        Tuple of (groups_processed, files_processed)
    """
    resume_file = output_path / RESUME_MARKER_FILE
    
    if not resume_file.exists():
        return 0, set()
    
    try:
        with open(resume_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            groups_processed = state.get('groups_processed', 0)
            # Convert list back to set
            files_processed = set(state.get('files_processed', []))
            return groups_processed, files_processed
    except Exception as e:
        print(f"Warning: Could not load resume state: {e}")
        return 0, set()

def generate_summary_report(output_path: Path, groups: List[List[Tuple[Path, int]]], 
                           ungrouped: List[Tuple[Path, int]], 
                           total_files: int, total_words: int):
    """
    Generate a summary report file in the output directory.
    
    Args:
        output_path: Output directory path
        groups: List of file groups created
        ungrouped: List of files that couldn't be grouped
        total_files: Total number of files processed
        total_words: Total number of words processed
    """
    summary_path = output_path / "notebook_cat_summary.txt"
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("NOTEBOOK CAT - PROCESSING SUMMARY\n")
            f.write("===============================\n\n")
            
            f.write(f"Total files processed: {total_files}\n")
            f.write(f"Total words processed: {total_words}\n")
            f.write(f"Files successfully grouped: {total_files - len(ungrouped)}\n")
            f.write(f"Files not grouped: {len(ungrouped)}\n\n")
            
            f.write(f"Output sources created: {len(groups)}\n\n")
            
            f.write("GROUP DETAILS\n")
            f.write("-------------\n")
            for i, group in enumerate(groups):
                group_words = sum(count for _, count in group)
                efficiency = (group_words / WORD_LIMIT) * 100
                f.write(f"Group {i+1}: {len(group)} files, {group_words} words ")
                f.write(f"({efficiency:.1f}% of capacity)\n")
                
                # List files in each group
                for j, (file_path, word_count) in enumerate(group):
                    f.write(f"  {j+1}. {file_path.name} ({word_count} words)\n")
                f.write("\n")
            
            if ungrouped:
                f.write("UNGROUPED FILES\n")
                f.write("--------------\n")
                for file_path, word_count in ungrouped:
                    reason = "Exceeds word limit" if word_count > WORD_LIMIT else "Couldn't fit in groups"
                    f.write(f"- {file_path.name} ({word_count} words): {reason}\n")
        
        print(f"Summary report created: {summary_path}")
    except Exception as e:
        print(f"Warning: Could not create summary report: {e}")

def process_directory(input_dir: str, output_dir: str, source_limit: int = DEFAULT_SOURCE_LIMIT, 
                     dry_run: bool = False, file_extensions: Optional[Set[str]] = None,
                     json_path: Optional[str] = None, resume: bool = False,
                     max_files: Optional[int] = None):
    """
    Main processing function.
    
    Args:
        input_dir: Input directory containing source files
        output_dir: Output directory for concatenated files
        source_limit: Maximum number of source files to create
        dry_run: If True, don't create output files, just report
        file_extensions: Set of file extensions to process (default: txt, md, json)
        json_path: Optional path to text field in JSON files
        resume: If True, attempt to resume a previous interrupted operation
        max_files: Maximum number of input files to process
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.is_dir():
        print(f"Error: Input directory '{input_dir}' not found or is not a directory.")
        return

    output_path.mkdir(parents=True, exist_ok=True)  # Create output dir if it doesn't exist

    # Set default file extensions if not specified
    if file_extensions is None:
        file_extensions = {"txt", "md", "json"}

    # Check for resume state
    groups_processed = 0
    files_processed = set()
    if resume:
        groups_processed, files_processed = load_resume_state(output_path)
        if groups_processed > 0 or files_processed:
            print(f"Resuming previous operation: {groups_processed} groups already processed.")

    print(f"Scanning for files with extensions {file_extensions} in '{input_path}'...")
    all_files = get_files_by_extensions(input_path, file_extensions, max_files)
    
    # Remove already processed files if resuming
    if resume and files_processed:
        all_files = [f for f in all_files if str(f) not in files_processed]
    
    if not all_files:
        print(f"No matching files found in the input directory.")
        return

    print(f"Found {len(all_files)} files. Counting words...")
    files_with_counts = []
    total_words = 0
    for f in all_files:
        count = count_words_in_file(f, json_path)
        files_with_counts.append((f, count))
        total_words += count

    print(f"Total words across all files: {total_words}")
    print(f"Grouping files with a source limit of {source_limit} and word limit of {WORD_LIMIT} per source...")

    groups, ungrouped = group_files(files_with_counts, source_limit)

    if not groups:
        print("No groups could be formed. Check file sizes and limits.")
        return

    print(f"Created {len(groups)} groups.")
    
    if dry_run:
        print("\n--- DRY RUN MODE: No files will be created ---")
        print(f"Would create {len(groups)} output files with the following content:")
        
        for i, group in enumerate(groups):
            group_total_words = sum(count for _, count in group)
            efficiency = (group_total_words / WORD_LIMIT) * 100
            print(f"  Group {i+1}: {len(group)} files, {group_total_words} words ({efficiency:.1f}% of limit)")
            
            # Option to show detailed file list in dry run
            for j, (file_path, word_count) in enumerate(group[:5]):  # Show first 5 files
                print(f"    - {file_path.name} ({word_count} words)")
            if len(group) > 5:
                print(f"    - ... and {len(group) - 5} more files")
        
        # Generate summary report even in dry run mode
        generate_summary_report(output_path, groups, ungrouped, 
                              len(files_with_counts), total_words)
        return

    print(f"Concatenating files into '{output_path}'...")

    # Skip already processed groups if resuming
    if groups_processed > 0:
        groups = groups[groups_processed:]

    processed_file_paths = set(files_processed)  # Copy the set
    
    for i, group in enumerate(groups, start=groups_processed + 1):
        output_filename = f"notebooklm_source_{i}.txt"
        output_filepath = output_path / output_filename
        group_total_words = sum(count for _, count in group)
        print(f"  Creating {output_filename} from {len(group)} files (Total words: {group_total_words})...")
        concatenate_files(group, output_filepath)
        
        # Update resume state after each group
        for file_path, _ in group:
            processed_file_paths.add(str(file_path))
        save_resume_state(output_path, i, processed_file_paths)

    # Remove resume file when complete
    resume_file = output_path / RESUME_MARKER_FILE
    if resume_file.exists():
        try:
            resume_file.unlink()
        except Exception:
            pass  # Ignore errors in cleanup

    print("\nProcessing complete.")
    print(f"  {len(groups) + groups_processed} source files created in '{output_path}'.")
    if ungrouped:
        print(f"  {len(ungrouped)} files could not be grouped due to limits.")
        print("  See summary report for details.")
    
    # Generate summary report
    generate_summary_report(output_path, groups, ungrouped, 
                          len(files_with_counts), total_words)
