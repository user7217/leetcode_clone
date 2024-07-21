import json 
import os 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATA_DIR = 'data'

def get_file_path(file_name):
    return os.path.join(DATA_DIR, f'{file_name}.json')

def read_json(file_name):
    file_path = get_file_path(file_name)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as file:
        return json.load(file)
    

def write_json(file_name, data):
    file_path = get_file_path(file_name)
    with open(file_path, 'w') as file:
        json.dump(data, file)


class User:
    @staticmethod
    def get_all():
        return read_json('users')
    
    @staticmethod
    def save_all(users):
        write_json('users', users)

    @classmethod
    def find_by_id(cls, user_id):
        users = cls.get_all()
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    @classmethod
    def find_by_email(cls, email):
        users = cls.get_all()
        for user in users:
            if user['email'] == email:
                return user
        return None
    
    @classmethod
    def create(cls, username, email, password):
        users = cls.get_all()
        user_id = len(users) + 1
        hashed_password = generate_password_hash(password)
        user = {'id': user_id, 'username': username, 'email': email, 'password': hashed_password}
        users.append(user)
        cls.save_all(users)
        return user
    
class Problem:
    @staticmethod
    def get_all():
        return read_json('problems')
    
    @staticmethod
    def save_all(problems):
        write_json('problems', problems)

    @classmethod
    def find_by_id(cls, problem_id):
        problems = cls.get_all()
        for problem in problems:
            if problem['id'] == problem_id:
                return problem
        return None
    
    @classmethod
    def create(cls, title, description, sample_input, sample_output):
        problems = cls.get_all()
        problem_id = len(problems) + 1
        problem = {'id': problem_id, 'title': title, 'description': description, 'sample_input': sample_input, 'sample_output': sample_output}
        problems.append(problem)
        cls.save_all(problems)
        return problem
    
class Submission:
    @staticmethod
    def get_all():
        return read_json('submissions')
    
    @staticmethod
    def save_all(submissions):
        write_json('submissions', submissions)

    @classmethod
    def find_by_id(cls, submission_id):
        submissions = cls.get_all()
        for submission in submissions:
            if submission['id'] == submission_id:
                return submission
        return None
    
    @classmethod
    def create(cls, code, result, user_id, problem_id, runtime, memory_used):
        submissions = cls.get_all()
        submission_id = len(submissions) + 1
        submission = {'id': submission_id, 'code': code, 'result': result, 'user_id': user_id, 'problem_id': problem_id, 'runtime': runtime, 'memory_used': memory_used, 'created_at': datetime.now().isoformat()}
        submissions.append(submission)
        cls.save_all(submissions)
        return submission
