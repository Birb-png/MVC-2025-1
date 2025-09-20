# models/project_model.py - Project Model (Data Layer)
import json
import os
from datetime import datetime, timedelta
import random

class ProjectModel:
    """Model class for handling Project and RewardTier data operations"""
    
    def __init__(self):
        """Initialize ProjectModel with data file paths"""
        self.projects_file = 'data/projects.json'
        self.rewards_file = 'data/reward_tiers.json'
        self.categories_file = 'data/categories.json'
        
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
    
    def get_all_projects(self):
        """Get all projects with calculated progress"""
        projects = self._load_data(self.projects_file)
        for project in projects:
            project['days_remaining'] = self._calculate_days_remaining(project['deadline'])
            project['progress_percentage'] = self._calculate_progress_percentage(
                project['current_amount'], project['goal_amount'])
        return projects
    
    def get_project_by_id(self, project_id):
        """Get specific project by ID"""
        projects = self.get_all_projects()
        for project in projects:
            if project['id'] == project_id:
                return project
        return None
    
    def get_filtered_projects(self, search='', category='', sort_by='newest'):
        """Get projects with filtering and sorting"""
        projects = self.get_all_projects()
        
        # Filter by search term
        if search:
            projects = [p for p in projects if search.lower() in p['name'].lower() 
                       or search.lower() in p.get('description', '').lower()]
        
        # Filter by category
        if category:
            projects = [p for p in projects if p['category'] == category]
        
        # Sort projects based on sort_by parameter
        if sort_by == 'newest':
            projects.sort(key=lambda x: x['created_date'], reverse=True)
        elif sort_by == 'deadline':
            projects.sort(key=lambda x: x['deadline'])
        elif sort_by == 'raised_amount':
            projects.sort(key=lambda x: x['current_amount'], reverse=True)
        elif sort_by == 'goal_amount':
            projects.sort(key=lambda x: x['goal_amount'], reverse=True)
        
        return projects
    
    def get_all_categories(self):
        """Get all project categories"""
        categories = self._load_data(self.categories_file)
        return [cat['name'] for cat in categories]
    
    def get_reward_tiers(self, project_id):
        """Get all reward tiers for a specific project"""
        rewards = self._load_data(self.rewards_file)
        project_rewards = [r for r in rewards if r['project_id'] == project_id]
        # Sort by minimum amount ascending
        project_rewards.sort(key=lambda x: x['min_amount'])
        return project_rewards
    
    def update_project_amount(self, project_id, additional_amount):
        """Update project's current raised amount"""
        projects = self._load_data(self.projects_file)
        for project in projects:
            if project['id'] == project_id:
                project['current_amount'] += additional_amount
                self._save_data(projects, self.projects_file)
                return True
        return False
    
    def update_reward_quota(self, reward_id, decrease_by=1):
        """Decrease reward tier quota when someone pledges"""
        rewards = self._load_data(self.rewards_file)
        for reward in rewards:
            if reward['id'] == reward_id and reward['remaining_quota'] > 0:
                reward['remaining_quota'] -= decrease_by
                self._save_data(rewards, self.rewards_file)
                return True
        return False
    
    def get_project_statistics(self):
        """Get overall project statistics"""
        projects = self.get_all_projects()
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if p['days_remaining'] > 0])
        expired_projects = total_projects - active_projects
        
        total_goal = sum(p['goal_amount'] for p in projects)
        total_raised = sum(p['current_amount'] for p in projects)
        
        successful_projects = len([p for p in projects 
                                 if p['current_amount'] >= p['goal_amount']])
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'expired_projects': expired_projects,
            'successful_projects': successful_projects,
            'success_rate': (successful_projects / total_projects * 100) if total_projects > 0 else 0,
            'total_goal_amount': total_goal,
            'total_raised_amount': total_raised,
            'overall_progress': (total_raised / total_goal * 100) if total_goal > 0 else 0
        }
    
    def _calculate_days_remaining(self, deadline_str):
        """Calculate remaining days until deadline"""
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            remaining = (deadline - today).days
            return max(0, remaining)  # Don't return negative days
        except:
            return 0
    
    def _calculate_progress_percentage(self, current_amount, goal_amount):
        """Calculate funding progress percentage"""
        if goal_amount <= 0:
            return 0
        return min((current_amount / goal_amount) * 100, 100)
    
    def initialize_sample_data(self):
        """Initialize sample data for testing"""
        # Sample categories
        categories = [
            {'id': 'tech', 'name': 'Technology'},
            {'id': 'art', 'name': 'Arts & Crafts'},
            {'id': 'game', 'name': 'Games'},
            {'id': 'education', 'name': 'Education'},
            {'id': 'health', 'name': 'Health & Fitness'}
        ]
        
        # Sample projects (8+ projects, 3+ categories as required)
        today = datetime.now()
        projects = [
            {
                'id': '10001001',  # 8-digit ID, first digit not 0
                'name': 'Smart Home IoT System',
                'description': 'Revolutionary smart home automation system with AI integration',
                'category': 'Technology',
                'goal_amount': 50000.0,
                'current_amount': 35750.0,
                'deadline': (today + timedelta(days=45)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=15)).strftime('%Y-%m-%d'),
                'creator': 'TechTeam Alpha'
            },
            {
                'id': '20002002',
                'name': 'Handcrafted Wooden Furniture Collection',
                'description': 'Beautiful sustainable furniture made from reclaimed wood',
                'category': 'Arts & Crafts',
                'goal_amount': 25000.0,
                'current_amount': 28500.0,  # Over-funded
                'deadline': (today + timedelta(days=12)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
                'creator': 'CraftMaster Studio'
            },
            {
                'id': '30003003',
                'name': 'Epic Fantasy Board Game',
                'description': 'Immersive board game with 3D miniatures and epic storyline',
                'category': 'Games',
                'goal_amount': 75000.0,
                'current_amount': 42300.0,
                'deadline': (today + timedelta(days=60)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=10)).strftime('%Y-%m-%d'),
                'creator': 'Fantasy Games Co'
            },
            {
                'id': '40004004',
                'name': 'Interactive Learning Platform for Kids',
                'description': 'Educational platform making learning fun with AR/VR technology',
                'category': 'Education',
                'goal_amount': 80000.0,
                'current_amount': 15200.0,
                'deadline': (today + timedelta(days=90)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
                'creator': 'EduTech Innovations'
            },
            {
                'id': '50005005',
                'name': 'Fitness Tracking Wearable Device',
                'description': 'Advanced fitness tracker with health monitoring capabilities',
                'category': 'Health & Fitness',
                'goal_amount': 40000.0,
                'current_amount': 38900.0,
                'deadline': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=25)).strftime('%Y-%m-%d'),
                'creator': 'HealthTech Labs'
            },
            {
                'id': '60006006',
                'name': 'Mobile App Development Toolkit',
                'description': 'Comprehensive toolkit for rapid mobile app development',
                'category': 'Technology',
                'goal_amount': 30000.0,
                'current_amount': 8500.0,
                'deadline': (today + timedelta(days=75)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=8)).strftime('%Y-%m-%d'),
                'creator': 'DevTools Inc'
            },
            {
                'id': '70007007',
                'name': 'Digital Art Creation Course',
                'description': 'Complete online course for digital art and design',
                'category': 'Arts & Crafts',
                'goal_amount': 15000.0,
                'current_amount': 12750.0,
                'deadline': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=35)).strftime('%Y-%m-%d'),
                'creator': 'Digital Artists Guild'
            },
            {
                'id': '80008008',
                'name': 'Virtual Reality Education System',
                'description': 'Immersive VR system for educational institutions',
                'category': 'Education',
                'goal_amount': 120000.0,
                'current_amount': 95400.0,
                'deadline': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
                'created_date': (today - timedelta(days=40)).strftime('%Y-%m-%d'),
                'creator': 'VR Education Labs'
            },
            {
                'id': '90009009',
                'name': 'Retro Arcade Gaming Console',
                'description': 'Classic gaming console with modern hardware',
                'category': 'Games',
                'goal_amount': 55000.0,
                'current_amount': 67200.0,  # Over-funded
                'deadline': (today + timedelta(days=3)).strftime('%Y-%m-%d'),  # Almost expired
                'created_date': (today - timedelta(days=50)).strftime('%Y-%m-%d'),
                'creator': 'Retro Games Studio'
            }
        ]
        
        # Sample reward tiers (2-3 per project as required)
        reward_tiers = []
        reward_id = 1
        
        for project in projects:
            # Create 2-3 reward tiers per project
            project_rewards = [
                {
                    'id': f'reward_{reward_id}',
                    'project_id': project['id'],
                    'name': 'Early Bird Special',
                    'description': 'Get the product at discounted price',
                    'min_amount': project['goal_amount'] * 0.05,  # 5% of goal
                    'remaining_quota': random.randint(50, 200)
                },
                {
                    'id': f'reward_{reward_id + 1}',
                    'project_id': project['id'],
                    'name': 'Standard Package',
                    'description': 'Standard product with basic features',
                    'min_amount': project['goal_amount'] * 0.10,  # 10% of goal
                    'remaining_quota': random.randint(100, 300)
                },
                {
                    'id': f'reward_{reward_id + 2}',
                    'project_id': project['id'],
                    'name': 'Premium Package',
                    'description': 'Premium product with extra features and bonuses',
                    'min_amount': project['goal_amount'] * 0.20,  # 20% of goal
                    'remaining_quota': random.randint(20, 100)
                }
            ]
            reward_tiers.extend(project_rewards)
            reward_id += 3
        
        # Save all sample data
        self._save_data(categories, self.categories_file)
        self._save_data(projects, self.projects_file)
        self._save_data(reward_tiers, self.rewards_file)
        
        print("Project sample data initialized successfully!")