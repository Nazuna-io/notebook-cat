"""
Web interface for notebook-cat using Gradio.

This module provides a simple web UI for the notebook-cat tool,
allowing users to select files, configure options, and download
the concatenated output files.
"""

import os
import tempfile
import shutil
import gradio as gr
from pathlib import Path
import zipfile
import sys
import re

# Import from the project
try:
    from notebook_cat import core
    from notebook_cat.config.defaults import (
        WORD_LIMIT,
        DEFAULT_SOURCE_LIMIT,
        PLUS_SOURCE_LIMIT,
        SUPPORTED_EXTENSIONS
    )
    from notebook_cat.validation import (
        validate_inputs, 
        sanitize_filename,
        validate_json_path
    )
except ImportError:
    # Fall back to relative import for development
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.notebook_cat import core
    from src.notebook_cat.config.defaults import (
        WORD_LIMIT,
        DEFAULT_SOURCE_LIMIT,
        PLUS_SOURCE_LIMIT,
        SUPPORTED_EXTENSIONS
    )
    from src.notebook_cat.validation import (
        validate_inputs, 
        sanitize_filename,
        validate_json_path
    )

def process_files(
    files,
    plan_type="free",
    word_limit=WORD_LIMIT,
    json_path=None,
    progress=gr.Progress()
):
    """
    Process uploaded files and create concatenated output files.
    
    Args:
        files: List of file paths uploaded through Gradio
        plan_type: NotebookLM plan type ('free', 'plus', or 'custom')
        word_limit: Word limit per source file
        json_path: Optional path to text field in JSON files
        progress: Gradio progress indicator
        
    Returns:
        tuple: (list of output files, status message, summary)
    """
    # Validate all inputs
    is_valid, sanitized, errors = validate_inputs(files, plan_type, word_limit, json_path)
    
    if not is_valid and not sanitized.get("files"):
        error_message = "Validation errors: " + ", ".join(errors)
        return [], error_message, ""
    
    # Use sanitized inputs
    files = sanitized.get("files", files)
    plan_type = sanitized.get("plan_type", plan_type)
    word_limit = sanitized.get("word_limit", word_limit)
    json_path = sanitized.get("json_path", json_path)
    
    # Show validation warnings if any
    validation_warnings = []
    if errors:
        validation_warnings.append("Some inputs were sanitized:")
        validation_warnings.extend(errors)
    
    # Track start time for performance reporting
    import time
    start_time = time.time()
    
    # Set source limit based on plan type
    if plan_type == "free":
        source_limit = DEFAULT_SOURCE_LIMIT
    elif plan_type == "plus":
        source_limit = PLUS_SOURCE_LIMIT
    else:  # custom
        source_limit = int(plan_type)
    
    # Initialize file info
    file_count = len(files)
    progress(0.0, desc=f"Starting to process {file_count} files...")
    
    # Create actual directories in /tmp that will persist
    import subprocess
    temp_base = "/tmp/notebook-cat-temp-" + str(int(time.time()))
    temp_input_dir = temp_base + "-input"
    temp_output_dir = temp_base + "-output"
    
    # Create the directories with secure permissions
    try:
        os.makedirs(temp_input_dir, exist_ok=True)
        os.makedirs(temp_output_dir, exist_ok=True)
        # Set more secure permissions (user read/write/execute only)
        os.chmod(temp_input_dir, 0o700)
        os.chmod(temp_output_dir, 0o700)
        print(f"Created temp directories: {temp_input_dir}, {temp_output_dir}")
    except Exception as e:
        print(f"Error creating temp directories: {e}")
        return [], f"Error creating temporary directories: {str(e)}", ""
    
    try:
        # Copy uploaded files to the temporary input directory with validation
        progress(0.1, desc=f"Copying {file_count} files...")
        copied_count = 0
        for i, file in enumerate(files):
            file_path = Path(file)
            # Only copy files with supported extensions
            extension = file_path.suffix.lower()[1:]
            if extension in SUPPORTED_EXTENSIONS:
                # Sanitize filename to prevent path traversal
                safe_filename = sanitize_filename(file_path.name)
                if safe_filename != file_path.name:
                    print(f"Sanitized filename: {file_path.name} -> {safe_filename}")
                
                dest_path = os.path.join(temp_input_dir, safe_filename)
                shutil.copy2(file, dest_path)
                copied_count += 1
                progress(0.1 + 0.1 * (i + 1) / file_count)
                print(f"Copied file {i+1}/{file_count}: {file} -> {dest_path}")
            else:
                print(f"Skipped unsupported file: {file}")
        
        # Check if files were copied
        copied_files = os.listdir(temp_input_dir)
        print(f"Files copied to temp dir: {len(copied_files)} - {copied_files}")
        
        if copied_count == 0:
            return [], "No valid files were found. Please upload files with supported extensions (.txt, .md, .json).", ""
        
        # Validate JSON path one more time before processing
        if json_path:
            is_valid_json_path, sanitized_json_path = validate_json_path(json_path)
            if not is_valid_json_path:
                json_path = sanitized_json_path
                print(f"Sanitized JSON path: {json_path}")
                # Add a warning but continue processing
                validation_warnings.append(f"Invalid JSON path format was sanitized to: {sanitized_json_path}")
        
        # Process the files
        progress(0.2, desc="Processing files...")
        
        # Override the word limit for this run
        original_word_limit = core.WORD_LIMIT
        core.WORD_LIMIT = word_limit
        
        # Process the directory
        core.process_directory(
            input_dir=temp_input_dir,
            output_dir=temp_output_dir,
            source_limit=source_limit,
            json_path=json_path,
            max_files=None  # No limit for the web UI
        )
        
        # Restore the original word limit
        core.WORD_LIMIT = original_word_limit
        
        # Update progress
        progress(0.8, desc="Reading processing summary...")
        
        # Read the summary report
        summary_path = os.path.join(temp_output_dir, "notebook_cat_summary.txt")
        summary = ""
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = f.read()
                print(f"Read summary file: {summary_path}")
        
        # Check if any output files were created
        output_files_list = []
        for item in os.listdir(temp_output_dir):
            if item.startswith("notebooklm_source_") and item.endswith(".txt"):
                output_file_path = os.path.join(temp_output_dir, item)
                if os.path.isfile(output_file_path):
                    output_files_list.append(output_file_path)
                    print(f"Found output file: {output_file_path}")
        
        if not output_files_list:
            print("No output files were created")
            return [], "Error: No output files were created. Check if input files are valid.", summary
        
        # Create zip file path
        progress(0.85, desc="Creating output archive...")
        zip_filename = "notebook_cat_output.zip"
        zip_path = os.path.join(temp_output_dir, zip_filename)
        print(f"Creating ZIP at {zip_path}")
        
        try:
            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add summary file if it exists
                if os.path.exists(summary_path):
                    zipf.write(summary_path, arcname=os.path.basename(summary_path))
                    progress(0.87, desc="Archiving summary file...")
                    print(f"Added summary to ZIP: {summary_path}")
                
                # Add output files
                total_files = len(output_files_list)
                for i, file_path in enumerate(output_files_list):
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                    # Update progress from 0.87 to 0.97
                    progress_value = 0.87 + (0.1 * (i + 1) / total_files)
                    progress(progress_value, desc=f"Archiving file {i+1} of {total_files}...")
                    print(f"Added file to ZIP ({i+1}/{total_files}): {file_path}")
        except Exception as e:
            print(f"Error creating ZIP: {e}")
            # Create simple error text file instead
            error_file = os.path.join(temp_output_dir, "error.txt")
            with open(error_file, 'w') as f:
                f.write(f"Error creating ZIP: {str(e)}\n\n")
                f.write("Files processed:\n")
                for i, file_path in enumerate(output_files_list):
                    f.write(f"{i+1}. {os.path.basename(file_path)}\n")
            return [error_file], f"Error creating ZIP: {str(e)}", summary
        
        # Check if ZIP exists
        if not os.path.exists(zip_path):
            print(f"ZIP file doesn't exist at expected path: {zip_path}")
            # Return the first output file as a fallback
            if output_files_list:
                return [output_files_list[0]], "Error creating ZIP archive. Returning first output file instead.", summary
            else:
                return [], "Error: No output files found.", summary
        
        # Get ZIP file size
        zip_size = os.path.getsize(zip_path)
        print(f"ZIP created successfully at {zip_path}, size: {zip_size} bytes")
        
        # Verify ZIP contents
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zip_contents = zipf.namelist()
                print(f"ZIP contains {len(zip_contents)} files: {zip_contents}")
        except Exception as e:
            print(f"Error reading ZIP file: {e}")
        
        # Complete progress
        progress(1.0, desc="Processing complete!")
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Add validation warnings if any
        status_message = f"Processing complete! {len(output_files_list)} files created in {elapsed_time:.2f} seconds."
        if validation_warnings:
            status_message += "\n\nWarnings: " + "; ".join(validation_warnings)
        
        return [zip_path], status_message, summary
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {str(e)}")
        print(error_trace)
        
        # Try to create an error file
        error_file = os.path.join(temp_output_dir, "error_report.txt")
        try:
            with open(error_file, 'w') as f:
                f.write(f"Error processing files: {str(e)}\n\n")
                f.write(f"Error details:\n{error_trace}\n")
            
            progress(1.0, desc=f"Error: {str(e)}")
            return [error_file], f"Error processing files: {str(e)}", ""
        except:
            progress(1.0, desc=f"Error: {str(e)}")
            return [], f"Error processing files: {str(e)}", ""

def create_ui():
    """Create and configure the Gradio interface."""
    
    # Define CSS for a cleaner look
    css = """
    #file-upload { min-height: 10em; }
    #summary-output { font-family: monospace; white-space: pre; }
    .output-section { margin-top: 1em; }
    .result-box { background-color: #f8f9fa; padding: 1em; border-radius: 0.5em; margin-bottom: 1em; }
    /* Add CSP-like protections via CSS since we can't set headers directly */
    iframe { display: none; }
    """
    
    with gr.Blocks(css=css, title="Notebook Cat - File Concatenator for NotebookLM") as app:
        # Add the notebook cat image at the top
        with gr.Row(variant="panel"):
            with gr.Column(scale=1):
                gr.Image(value=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "notebook-cat-small.jpg"), 
                          show_label=False, height=100, width=100)
            with gr.Column(scale=5):
                gr.Markdown("# Notebook Cat")
                gr.Markdown("""
                A tool to optimally concatenate text, markdown, and JSON files into larger source files for Google NotebookLM.
                This helps maximize your content while respecting NotebookLM's source count limits.
                """)
        
        with gr.Row():
            with gr.Column(scale=2):
                files = gr.File(
                    label="Upload Files",
                    file_types=list(SUPPORTED_EXTENSIONS.keys()),
                    file_count="multiple",
                    elem_id="file-upload"
                )
                
                with gr.Row():
                    plan = gr.Radio(
                        label="NotebookLM Plan", 
                        choices=["free", "plus", "custom"],
                        value="free",
                        info="Free: 50 sources max, Plus: 300 sources max"
                    )
                    custom_limit = gr.Number(
                        label="Custom Source Limit",
                        value=100,
                        minimum=1,
                        precision=0,
                        visible=False
                    )
                
                word_limit = gr.Slider(
                    label="Word Limit per Source",
                    minimum=10000,
                    maximum=500000,
                    value=WORD_LIMIT,
                    step=10000,
                    info=f"Default: {WORD_LIMIT} words (recommended for NotebookLM)"
                )
                
                json_path = gr.Textbox(
                    label="JSON Path (Optional)",
                    placeholder="E.g., segments.text",
                    info="Path to text field in JSON files using dot notation"
                )
                
                process_btn = gr.Button("Process Files", variant="primary", size="lg")
                
            with gr.Column(scale=3):
                gr.Markdown("## Results")
                status = gr.Textbox(label="Status", interactive=False)
                output_files = gr.File(label="Download Concatenated Files")
                
                gr.Markdown("## Processing Summary")
                summary = gr.Textbox(
                    label="",
                    interactive=False,
                    elem_id="summary-output",
                    lines=15,
                    show_label=False
                )
        
        # Handle plan selection to show/hide custom limit input
        def update_custom_limit_visibility(plan_value):
            return gr.update(visible=(plan_value == "custom"))
        
        plan.change(
            fn=update_custom_limit_visibility,
            inputs=plan,
            outputs=custom_limit
        )
        
        # Process files when button is clicked
        process_btn.click(
            fn=process_files,
            inputs=[
                files,
                plan,
                word_limit,
                json_path,
            ],
            outputs=[output_files, status, summary]
        )
        
        # Auto-update the source limit based on the plan
        def get_source_limit(plan_value, custom_value):
            if plan_value == "free":
                return f"Source Limit: {DEFAULT_SOURCE_LIMIT} files"
            elif plan_value == "plus":
                return f"Source Limit: {PLUS_SOURCE_LIMIT} files"
            else:  # custom
                return f"Source Limit: {int(custom_value)} files"
        
        # Add a footer with information
        gr.Markdown("""
        ## About Notebook Cat
        - Supports text (.txt), markdown (.md), and JSON (.json) files
        - Optimally groups files to maximize content while respecting NotebookLM's limits
        - Creates clear separators between original files in the output
        
        [Visit GitHub Repository](https://github.com/Nazuna-io/notebook-cat)
        """)
    
    return app

def launch_ui():
    """Launch the Gradio interface."""
    import socket
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch the Notebook Cat web interface")
    parser.add_argument("--network", action="store_true", help="Allow network access (bind to all interfaces)")
    args = parser.parse_args()
    
    # Determine server name based on network flag
    server_name = "0.0.0.0" if args.network else "127.0.0.1"
    
    # Get hostname information only if needed
    hostname = ""
    ip_address = ""
    if args.network:
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "your-ip-address"
    
    app = create_ui()
    print("\n🔥 Starting Notebook Cat Web UI...")
    print("📝 Local access: http://localhost:7860")
    
    if args.network:
        print(f"📝 Network access: http://{ip_address}:7860 (from any device on your network)")
        print("\nWARNING: Network access is enabled. The web interface is accessible from other devices.")
    else:
        print("\nNote: By default, the web interface is only accessible on localhost for security.")
        print("To enable network access, use the --network flag when starting the application.")
    
    print("\nPress Ctrl+C to stop the server\n")
    
    # Set strict Content Security Policy headers
    # These would normally be passed as headers parameter to app.launch(), but older
    # Gradio versions don't support this. Setting CSP is still recommended when upgrading.
    csp_headers = {
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; form-action 'self';",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    # Launch the app with verbose output
    app.launch(
        server_name=server_name,  # Bind to localhost by default or all interfaces if --network
        show_error=True,          # Show detailed error messages
        share=False,              # No Gradio public share
        quiet=False,              # Show server logs
        ssl_verify=True,          # Verify SSL
    )

if __name__ == "__main__":
    launch_ui()
