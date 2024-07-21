from flask import Flask, request, jsonify
import docker
import json
import os
import time
import traceback

app = Flask(__name__)

# Path to store submissions
SUBMISSIONS_FILE = 'submissions.json'

# Initialize Docker client
client = docker.from_env()

# Helper function to load problems
def load_problems():
    with open('problems.json', 'r') as file:
        return json.load(file)

# Route to get problem by ID
@app.route('/problem/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    problems = load_problems()
    problem = next((p for p in problems if p['id'] == problem_id), None)
    if problem is None:
        return jsonify({'error': 'Problem not found'}), 404
    return jsonify(problem)

# Route to submit code
@app.route('/submit', methods=['POST'])
def submit_code():
    data = request.json
    problem_id = data.get('problem_id')
    code = data.get('code')
    user_id = data.get('user_id')

    if not problem_id or not code or not user_id:
        return jsonify({'error': 'Missing required fields'}), 400

    # Run the user code in a Docker container and validate
    result, runtime, memory, test_results = run_code_in_docker_and_test(code, problem_id)

    # Store the submission
    save_submission(user_id, problem_id, result, runtime, memory, test_results)

    return jsonify({
        'result': result,
        'runtime': runtime,
        'memory': memory,
        'test_results': test_results
    })

# Function to run code in a Docker container and capture output
def run_code_in_docker_and_test(code, problem_id):
    # Path where the Dockerfile will be located
    code_file_path = 'code_to_run.py'
    
    # Write the user code to a file
    with open(code_file_path, 'w') as file:
        file.write(code)

    # Load the problem and its test cases
    problems = load_problems()
    problem = next((p for p in problems if p['id'] == problem_id), None)
    if problem is None:
        return "Problem not found", None, None, []

    test_cases = problem.get('test_cases', [])
    
    try:
        # Build the Docker image
        image = client.images.build(path='.', dockerfile='Dockerfile.sandbox', tag='user-code')[0]
        
        # Run the Docker container
        start_time = time.time()
        container = client.containers.run(
            image.id,
            detach=True,
            stdout=True,
            stderr=True,
            remove=True,
            timeout=5
        )
        logs = container.logs(follow=True).decode('utf-8')
        end_time = time.time()

        runtime = end_time - start_time
        memory = None  # Memory usage would need additional setup

        # Evaluate test cases
        test_results = evaluate_test_cases(code, test_cases)

        return logs, runtime, memory, test_results
    except docker.errors.ContainerError as e:
        return f"Container Error: {str(e)}", None, None, []
    except docker.errors.ImageNotFound as e:
        return f"Image Not Found Error: {str(e)}", None, None, []
    except Exception as e:
        return f"Error: {str(e)}\n{traceback.format_exc()}", None, None, []
    finally:
        # Cleanup Docker resources
        client.images.remove('user-code', force=True)
        os.remove(code_file_path)

# Function to evaluate test cases against the user code
def evaluate_test_cases(code, test_cases):
    results = []
    for case in test_cases:
        input_data = case['input']
        expected_output = case['expected_output']

        # Write input and expected output to files
        with open('input.txt', 'w') as file:
            file.write(input_data)
        with open('expected_output.txt', 'w') as file:
            file.write(expected_output)
        
        # Run the user code
        try:
            result = subprocess.run(
                ['python', 'code_to_run.py'],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip()
            if output == expected_output:
                results.append({'input': input_data, 'expected_output': expected_output, 'result': 'Pass'})
            else:
                results.append({'input': input_data, 'expected_output': expected_output, 'result': f'Fail - Got: {output}'})
        except subprocess.TimeoutExpired:
            results.append({'input': input_data, 'expected_output': expected_output, 'result': 'Fail - Timeout'})
        except Exception as e:
            results.append({'input': input_data, 'expected_output': expected_output, 'result': f'Error: {str(e)}'})

    return results

# Function to save submission details to a JSON file
def save_submission(user_id, problem_id, result, runtime, memory, test_results):
    submission = {
        'user_id': user_id,
        'problem_id': problem_id,
        'result': result,
        'runtime': runtime,
        'memory': memory,
        'test_results': test_results,
        'timestamp': time.time()
    }
    
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'r') as file:
            submissions = json.load(file)
    else:
        submissions = []

    submissions.append(submission)
    
    with open(SUBMISSIONS_FILE, 'w') as file:
        json.dump(submissions, file, indent=4)

if __name__ == '__main__':
    app.run(debug=True)
