import subprocess
import sys

def main():
    # Path to the user-submitted code file
    code_file_path = '/usr/src/app/code_to_run.py'

    # Execute the user code using subprocess
    try:
        result = subprocess.run(
            ['python', code_file_path],
            capture_output=True,
            text=True,
            timeout=5  # Set a timeout for execution
        )
        # Print stdout and stderr from the code execution
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Execution timed out")
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()
