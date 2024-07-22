from flask import Flask, request, jsonify, send_from_directory
import sys
import io
import json

app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/problems')
def problems():
    with open('problems.json') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/template')
def template():
    initial_code = """\
def main():
    x = input("Enter a number: ")
    return int(x) * int(x)

print(main())"""
    return jsonify({'code': initial_code})

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    test_cases = data.get('testCases', [])
    
    def run_test_case(test_case):
        input_data, expected_output = test_case['input'], test_case['expected']
        # Redirect stdout to capture the output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            # Use exec to run the code
            exec(code, {'input': lambda: input_data, 'print': print})
            output = sys.stdout.getvalue().strip()
        except Exception as e:
            output = str(e)
        finally:
            sys.stdout = old_stdout
        return {
            'input': input_data,
            'expected': expected_output,
            'output': output,
            'passed': output == expected_output
        }

    results = [run_test_case(test_case) for test_case in test_cases]

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
