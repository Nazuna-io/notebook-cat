# Notebook Cat

A command-line tool to optimally concatenate text, markdown, and JSON files into larger source files ("sources") for Google NotebookLM, maximizing source count and word limits.

## Problem

Google NotebookLM limits the number of sources (files) you can upload.  As of April 9, 2025 these limits are:
- Free plan: 50 sources maximum
- Plus plan: 300 sources maximum

Each source file is limited to 200MB in size or 500,000 words, whichever comes first.

Many users have dozens or hundreds of smaller files they'd like to use as sources, but they hit the source count limit long before the word limit. This tool solves that problem by intelligently combining files.  For example, if a user is on the free plan with a 50 source limit but has 200 small files of 10,000 words each, this tool will combine those files in to the fewest number of files, which would be just 4 files/sources (though five files might be needed due extra word count needed for metadata and breaks between data).  With notebook-cat you can overcome the sources limits to load 25 million words on the free plan or 150 million works on the Plus plan.

## Features

- Supports multiple file types:
  - Text files (`.txt`)
  - Markdown files (`.md`)
  - JSON files (`.json`) with intelligent text extraction
- Counts words in each file to ensure proper grouping
- Groups files optimally to maximize content per source without exceeding word limits
- Creates concatenated output files with clear separators between original sources
- Resume functionality to continue interrupted operations
- Respects NotebookLM's source count limits based on your plan
- Provides detailed reporting on files processed, grouped, and any that couldn't be included
- Dry-run mode to preview operations without creating files

## Limitations
- NotebookLM is essentially a Retreival-Augmented Generation (RAG) tool that will decompose sources into embeddings.  This should not affect accuracy, but it may have a slight effect on accuracy
- It is possible there could be other trade-offs with citations and synthesis, but it should be minor.
- Please report any issues that you find, as there may be ways to improve the file structure to help NotebookLM

## Requirements
- Python 3.10 or 3.11 works best.  It's recommended to create a python or conda virtual environment, but not necessary
- Pytest is the only dependency
- Should work on just about any system

## Installation

From source:
```bash
git clone https://github.com/yourusername/notebook-cat.git
cd notebook-cat
pip install -e .
```

## Basic Usage

```bash
# Basic usage with default parameters (50 source limit, all supported file types)
notebook-cat /path/to/input/files /path/to/output/directory

# Specify a source limit for Plus plan
notebook-cat /path/to/input/files /path/to/output/directory --plus-plan

# Specify a custom source limit
notebook-cat /path/to/input/files /path/to/output/directory -l 75

# Preview what would be done without creating files
notebook-cat /path/to/input/files /path/to/output/directory --dry-run
```

## Advanced Usage

### Limiting Input Files

If you have a large directory with many files, you can limit the number of input files:

```bash
# Process only the first 100 files
notebook-cat /path/to/input/files /path/to/output/directory --max-files 100
```

### Selecting File Types

Process only specific file types:

```bash
# Process only text files
notebook-cat /path/to/input/files /path/to/output/directory --extensions txt

# Process only markdown and JSON files
notebook-cat /path/to/input/files /path/to/output/directory --extensions md,json
```

### JSON Processing Options

For JSON files, you can specify a path to the text content using dot notation:

```bash
# Extract text from a specific JSON path
notebook-cat /path/to/input/files /path/to/output/directory --json-path "segments.text"
```

### Resume Functionality

If processing is interrupted, you can resume where you left off:

```bash
# Resume a previously interrupted process
notebook-cat /path/to/input/files /path/to/output/directory --resume
```

## All Command Line Options

```
Required arguments:
  input_dir              Directory containing the files to process.
  output_dir             Directory where the concatenated source files will be saved.

Source Limit Options:
  -l LIMIT, --limit LIMIT
                        Maximum number of source files to create. (default: 50)
  --free-plan           Use NotebookLM Free plan limit (50 sources).
  --plus-plan           Use NotebookLM Plus plan limit (300 sources).

File Type Options:
  --extensions EXTENSIONS
                        Comma-separated list of file extensions to process. (default: txt,md,json)
  --json-path JSON_PATH
                        Path to text field in JSON files (dot notation, e.g., 'segments.text')
  --max-files MAX_FILES
                        Maximum number of input files to process (useful for large directories)

Processing Options:
  --dry-run             Show what would be done without creating output files
  --resume              Resume a previously interrupted operation
```

## Limitations

- Does not split files that exceed the word limit - they'll be skipped
- Files are concatenated with simple text separators
- JSON extraction works best with simple structures; complex nested objects may need a specific path

## Configuration

The tool uses these default limits which can be adjusted in the configuration file:
- Word limit per source file: 500,000 words
- Default source limit: 50 sources (Free plan)
- Plus plan limit: 300 sources

## Example Output

The tool creates files with clearly marked sections:

```
--- START FILE: original_filename.json (1234 words) ---

[Original file content here]

--- END FILE: original_filename.json ---

--- START FILE: another_file.md (567 words) ---

[Original markdown content here]

--- END FILE: another_file.md ---
```

## Output Report

After processing, a detailed summary report is created in the output directory:

```
NOTEBOOK CAT - PROCESSING SUMMARY
===============================

Total files processed: 120
Total words processed: 1,234,567
Files successfully grouped: 118
Files not grouped: 2

Output sources created: 5

GROUP DETAILS
-------------
Group 1: 25 files, 480,123 words (96.0% of capacity)
  1. large_file.txt (50,000 words)
  2. medium_file.json (30,000 words)
  ...

UNGROUPED FILES
--------------
- huge_file.txt (600,000 words): Exceeds word limit
```
