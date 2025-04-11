![Notebook Cat](assets/notebook-cat-small.jpg)

# Notebook Cat

A command-line tool to optimally concatenate text, markdown, and JSON files into larger source files ("sources") for Google NotebookLM, maximizing source count and word limits.

## Problem

Google NotebookLM limits the number of sources (files) you can upload.  As of April 9, 2025 these limits are:
- Free plan: 50 sources maximum
- Plus plan: 300 sources maximum

Each source file is limited to 200MB in size or 500,000 words, whichever comes first. Many users have dozens or hundreds of smaller files they'd like to use as sources, but they hit the source count limit long before the word limit. This tool solves that problem by intelligently combining files.  For example, if a user is on the free plan with a 50 source limit but has 200 small files of 10,000 words each, this tool will combine those files in to the fewest number of files, which would be just 4 files/sources (though five files might be needed due extra word count needed for metadata and breaks between data).  With notebook-cat you can overcome the sources limits to load 25 million words on the free plan or 150 million words on the Plus plan.

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
- Currently, only txt, markdown (.md), and json files are supported
- NotebookLM is essentially a Retreival-Augmented Generation (RAG) tool that will decompose sources into embeddings.  Concatenating or grouping files should not affect accuracy, but it may have a slight effect on accuracy
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

- Does not split files that exceed the word limit - they'll be skipped.  The notebook-cat can only group files under the word limit
- Files are concatenated with simple text separators
- JSON extraction works best with simple structures; complex nested objects may need a specific path

## Configuration

The tool uses these default limits which can be adjusted in the `config.py` file at the root of the project:
- Word limit per source file: 380,000 words (You can configure this to the full 500k, but there is a bug in Google's NotebookLM source upload that prevents it from successfully adding files with more than about 380k words, as of April 10, 2025)
- Default source limit: 50 sources (Free plan)
- Plus plan limit: 300 sources

Example configuration (`config.py`):
```python
# Maximum number of words per source file
WORD_LIMIT = 248000  # Includes a 20k word cushion

# Source count limits for different plans
DEFAULT_SOURCE_LIMIT = 50  # Free plan
PLUS_SOURCE_LIMIT = 300    # Plus plan
```

You can modify these values directly in this file to customize the behavior of the tool to your specific needs.

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## TODOs and Future Improvements

Future features and improvements planned for notebook-cat:

1. **Interactive Mode**: Add an interactive CLI mode for easier use without having to remember all command line options
2. **PDF Support**: Add support for extracting text from PDF files

## Example Output Report
```
NOTEBOOK CAT - PROCESSING SUMMARY
===============================

Total files processed: 76
Total words processed: 1019796
Files successfully grouped: 76
Files not grouped: 0

Output sources created: 3

GROUP DETAILS
-------------
Group 1: 22 files, 479766 words (100.0% of capacity)
  1. Video_KL_6BZhF0A8.txt (36378 words)
  2. Video_-57lSwEu9ro.txt (34764 words)
  3. Video_q0e3VcoT238.txt (31740 words)
  4. Video_eti_ewdbHKU.txt (30515 words)
  5. Video_T1GU1E9amfY.txt (28795 words)
  6. Video_4TB4zdQY8Jg.txt (28202 words)
  7. Video_V6Yql0jrjow.txt (28023 words)
  8. Video_OBvusf6vn-0.txt (26892 words)
  9. Video_yWQxaQ_tJVY.txt (26648 words)
  10. Video_0452NA7OnzU.txt (26076 words)
  11. Video_xFRgZOhCVLg.txt (25992 words)
  12. Video_OPxxJ2wBNTA.txt (25686 words)
  13. Video__tg1zT_2pyo.txt (22545 words)
  14. Video_JQzNDnJCtiQ.txt (21732 words)
  15. Video_lcn7D2DRtPU.txt (21714 words)
  16. Video_f125iYyWHZk.txt (21345 words)
  17. Video_PU8QJREj-54.txt (20928 words)
  18. Video_WUOfoNKLV_M.txt (20921 words)
  19. Video_0ynMlOnf5kw.txt (20522 words)
  20. Video_xWFdBFQc39A.txt (243 words)
  21. Video_jNQXAC9IVRw.txt (72 words)
  22. Video_dQw4w9WgXcQ.txt (33 words)

Group 2: 46 files, 479868 words (100.0% of capacity)
  1. Video_IvqSgHvzTnY.txt (20230 words)
  2. Video_2NWKJL6ihOw.txt (18939 words)
  3. Video_9HYpN0Bauk4.txt (17356 words)
  4. Video_iywvNIWKbPI.txt (16673 words)
  5. Video_6bJEM_J3uaE.txt (16404 words)
  6. Video_13KcN-fRLFI.txt (14752 words)
  7. Video_f7W-4HEGtHk.txt (14619 words)
  8. Video_IXfVyyjbTOs.txt (14326 words)
  9. Video_4mfMV4gpGDI.txt (14130 words)
  10. Video_gRQwbRtsebw.txt (14085 words)
  11. Video__D7fxkvsUUw.txt (14061 words)
  12. Video_SVIgQ9gglSI.txt (13157 words)
  13. Video__NLfn_p08KU.txt (13044 words)
  14. Video_CEWpapzhO1M.txt (12938 words)
  15. Video_gsu1thdI2Qo.txt (12938 words)
  16. Video_qfQpJxRP8ew.txt (12889 words)
  17. Video_fO-0uPN_f3w.txt (12852 words)
  18. Video_vo5dL-8-RPo.txt (12580 words)
  19. Video_UDSvo2nk_Hg.txt (12242 words)
  20. Video_gyFHlxdOSsw.txt (12036 words)
  21. Video_oPpDGrmX9No.txt (11963 words)
  22. Video_qdE8yaxK6BU.txt (11732 words)
  23. Video_TvXzhfySwWs.txt (11637 words)
  24. Video_SXaLoySpxUo.txt (11546 words)
  25. Video_3NXcqD8GyjY.txt (11516 words)
  26. Video_E5dE8U1eP3A.txt (10265 words)
  27. Video_Mo2-7RMOh5o.txt (10187 words)
  28. Video_pWFZafYLSeI.txt (8972 words)
  29. Video_wLYvfutQTQw.txt (8750 words)
  30. Video_8CtgO3EZOwk.txt (8399 words)
  31. Video_Mrx7JWEuRkc.txt (8028 words)
  32. Video_1tMKz-vmTEA.txt (7950 words)
  33. Video_VHzDsoliZiY.txt (7894 words)
  34. Video_j4LDqk3tKT0.txt (7554 words)
  35. Video_DlGJfhuno6g.txt (7547 words)
  36. Video_54c8svkLHf4.txt (7312 words)
  37. Video_Urmvgntxuss.txt (6942 words)
  38. Video_u_8vu-BY1mc.txt (6881 words)
  39. Video_ki6_ckQllyI.txt (6870 words)
  40. Video_A2BhItk6Fo0.txt (6629 words)
  41. Video_CwHdzz3RZLc.txt (6620 words)
  42. Video_c3vE5jpfBI0.txt (6251 words)
  43. Video__rHHNTrOgNk.txt (5637 words)
  44. Video_E1eoLw1goic.txt (4904 words)
  45. Video_Ax87nMWhmz0.txt (3977 words)
  46. Video_Rel3R79Y_oQ.txt (3654 words)

Group 3: 8 files, 20162 words (4.0% of capacity)
  1. Video_2-g1xYsgJ9s.txt (3893 words)
  2. Video_wCiOUNCpQzQ.txt (3455 words)
  3. Video_0psoYz3YrjU.txt (3110 words)
  4. Video_ikh8EIN3Qaw.txt (3030 words)
  5. Video_iUjCy3UbkHM.txt (2591 words)
  6. Video_9Ii6gVLGSqs.txt (1937 words)
  7. Video_ljfUtLK6qog.txt (1181 words)
  8. Video_FzIztse-FqM.txt (965 words)
```
