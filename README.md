# Notebook Cat

A command-line tool to concatenate text files into larger source files suitable for Google NotebookLM, respecting source count and word limits.

## Problem

Google NotebookLM limits the number of sources you can upload:
- Free plan: 50 sources maximum
- Plus plan: 300 sources maximum

Each source file is limited to 200MB in size or 500,000 words.

Many users have dozens or hundreds of smaller text files they'd like to use as sources, but they hit the source count limit long before the word limit. This tool solves that problem by intelligently combining files.

## Features

- Scans a directory for all text files
- Counts words in each file to ensure proper grouping
- Groups files optimally to maximize content per source without exceeding word limits
- Creates concatenated output files with clear separators between original sources
- Respects NotebookLM's source count limits based on your plan
- Provides detailed reporting on files processed, grouped, and any that couldn't be included

## Usage

```bash
# Basic usage with default source limit (50)
notebook-cat /path/to/input/files /path/to/output/directory

# Specify a custom source limit (e.g., for Plus plan)
notebook-cat /path/to/input/files /path/to/output/directory -l 300
```

## Installation

From source:
```bash
git clone https://github.com/yourusername/notebook-cat.git
cd notebook-cat
pip install -e .
```

## Limitations

- Currently only processes .txt files
- Does not split files that exceed the word limit - they'll be skipped
- Files are concatenated with simple text separators

## Configuration

The tool uses these default limits:
- Word limit per source file: 500,000 words
- Default source limit: 50 sources (Free plan)

## Example Output

The tool creates files with clearly marked sections like:

```
--- START FILE: original_filename.txt (1234 words) ---

[Original file content here]

--- END FILE: original_filename.txt ---
```
