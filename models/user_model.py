# models/user_model.py - User Model (Data Layer)
import json
import os
import hashlib
from datetime import datetime

class UserModel:
    """Model class for handling User data operations and authentication"""
    
    def __init__(self):
        """Initialize UserModel with data file path"""
        self.users_file = 'data/users.json'
    
    def _load_data(self, filename):
        """Load data from JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []
    
    def _save_data(self, data, filename):
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving {filename}: {e}")
    
    def _hash_password(self, password):
        """Simple password hashing (in production, use bcrypt or similar)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        users = self._load_data(self.users_file)
        hashed_password = self._hash_password(password)
        
        for user in users:
            if user['username'] == username and user['password'] == hashed_password:
                # Return user data without password
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'created_date': user['created_date']
                }
        return None
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        users = self._load_data(self.users_file)
        for user in users:
            if user['id'] == user_id:
                # Return user data without password
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'created_date': user['created_date']
                }
        return None
    
    def get_all_users(self):
        """Get all users (without passwords)"""
        users = self._load_data(self.users_file)
        return [
            {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'created_date': user['created_date']
            }
            for user in users
        ]
    
    def create_user(self, username, password, email, full_name):
        """Create new user account"""
        users = self._load_data(self.users_file)
        
        # Check if username already exists
        if any(user['username'] == username for user in users):
            return {'success': False, 'message': 'Username already exists'}
        
        # Check if email already exists
        if any(user['email'] == email for user in users):
            return {'success': False, 'message': 'Email already exists'}
        
        # Generate new user ID
        user_id = f"user_{len(users) + 1:04d}"
        
        # Create new user
        new_user = {
            'id': user_id,
            'username': username,
            'password': self._hash_password(password),
            'email': email,
            'full_name': full_name,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        users.append(new_user)
        self._save_data(users, self.users_file)
        
        return {'success': True, 'message': 'User created successfully', 'user_id': user_id}
    
    def get_user_statistics(self):
        """Get user-related statistics"""
        users = self.get_all_users()
        
        total_users = len(users)
        
        # Calculate users by registration date (last 30 days)
        today = datetime.now()
        recent_users = 0
        
        for user in users:
            try:
                created_date = datetime.strptime(user['created_date'], '%Y-%m-%d %H:%M:%S')
                days_ago = (today - created_date).days
                if days_ago <= 30:
                    recent_users += 1
            except:
                pass
        
        return {
            'total_users': total_users,
            'recent_users': recent_users,
            'active_users': total_users  # In a real system, would track last login
        }
    
    def initialize_sample_data(self):
        """Initialize sample user data for testing (10+ users as required)"""
        sample_users = [
            {
                'id': 'user_0001',
                'username': 'admin',
                'password': self._hash_password('admin123'),  # Simple password for testing
                'email': 'admin@crowdfunding.com',
                'full_name': 'System Administrator',
                'created_date': '2024-01-15 10:00:00'
            },
            {
                'id': 'user_0002',
                'username': 'john_doe',
                'password': self._hash_password('password123'),
                'email': 'john.doe@email.com',
                'full_name': 'John Doe',
                'created_date': '2024-02-10 14:30:00'
            },
            {
                'id': 'user_0003',
                'username': 'jane_smith',
                'password': self._hash_password('password123'),
                'email': 'jane.smith@email.com',
                'full_name': 'Jane Smith',
                'created_date': '2024-02-15 09:15:00'
            },
            {
                'id': 'user_0004',
                'username': 'mike_johnson',
                'password': self._hash_password('password123'),
                'email': 'mike.johnson@email.com',
                'full_name': 'Mike Johnson',
                'created_date': '2024-03-01 11:45:00'
            },
            {
                'id': 'user_0005',
                'username': 'sarah_wilson',
                'password': self._hash_password('password123'),
                'email': 'sarah.wilson@email.com',
                'full_name': 'Sarah Wilson',
                'created_date': '2024-03-05 16:20:00'
            },
            {
                'id': 'user_0006',
                'username': 'alex_brown',
                'password': self._hash_password('password123'),
                'email': 'alex.brown@email.com',
                'full_name': 'Alex Brown',
                'created_date': '2024-03-10 13:10:00'
            },
            {
                'id': 'user_0007',
                'username': 'lisa_davis',
                'password': self._hash_password('password123'),
                'email': 'lisa.davis@email.com',
                'full_name': 'Lisa Davis',
                'created_date': '2024-03-15 10:30:00'
            },
            {
                'id': 'user_0008',
                'username': 'tom_miller',
                'password': self._hash_password('password123'),
                'email': 'tom.miller@email.com',
                'full_name': 'Tom Miller',
                'created_date': '2024-03-20 15:45:00'
            },
            {
                'id': 'user_0009',
                'username': 'emma_garcia',
                'password': self._hash_password('password123'),
                'email': 'emma.garcia@email.com',
                'full_name': 'Emma Garcia',
                'created_date': '2024-03-25 12:00:00'
            },
            {
                'id': 'user_0010',
                'username': 'david_martinez',
                'password': self._hash_password('password123'),
                'email': 'david.martinez@email.com',
                'full_name': 'David Martinez',
                'created_date': '2024-04-01 09:30:00'
            },
            {
                'id': 'user_0011',
                'username': 'anna_rodriguez',
                'password': self._hash_password('password123'),
                'email': 'anna.rodriguez@email.com',
                'full_name': 'Anna Rodriguez',
                'created_date': '2024-04-05 14:15:00'
            },
            {
                'id': 'user_0012',
                'username': 'chris_lee',
                'password': self._hash_password('password123'),
                'email': 'chris.lee@email.com',
                'full_name': 'Chris Lee',
                'created_date': '2024-04-10 11:20:00'
            }
        ]
        
        self._save_data(sample_users, self.users_file)
        print("User sample data initialized successfully!")
        print("Login credentials for testing:")
        print("Username: admin, Password: admin123")
        print("Username: john_doe, Password: password123")
        print("(All sample users use 'password123' except admin)")