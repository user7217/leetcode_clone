from flask import Flask, request, jsonify
import sys
import io

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    problem = data.get('problem', '')
    test_cases = data.get('testCases', [])
    
    def run_test_case(test_case):
        input_data, expected_output = test_case['input'], test_case['expected']
        # Redirect stdout to capture the output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            # Use exec to run the code
            exec(code, {'input': input_data, 'print': print})
            output = sys.stdout.getvalue().strip()
        except Exception as e:
            output = str(e)
        finally:
            sys.stdout = old_stdout
        return output == expected_output

    results = []
    for test_case in test_cases:
        result = run_test_case(test_case)
        results.append({
            'input': test_case['input'],
            'expected': test_case['expected'],
            'result': result
        })

    return jsonify({'problem': problem, 'results': results})

if __name__ == '__main__':
    app.run(debug=True)
