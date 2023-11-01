import subprocess

# List of Python script filenames to run sequentially
scripts_to_run = ["pp_results_grabber.py", "pp_results_parser.py", "pp_results_combined.py"]

for script in scripts_to_run:
    result = subprocess.run(["python", script])

    if result.returncode == 0:
        print(f"Script {script} ran successfully.")
        print("Output:", result.stdout)
    else:
        print(f"Script {script} encountered an error.")
        print("Error:", result.stderr)