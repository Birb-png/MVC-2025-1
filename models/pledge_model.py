# models/pledge_model.py - Pledge Model (Data Layer)
import json
import os
from datetime import datetime
import random
from models.project_model import ProjectModel
from models.user_model import UserModel

class PledgeModel:
    """Model class for handling Pledge data operations and business rules"""
    
    def __init__(self):
        """Initialize PledgeModel with data file paths"""
        self.pledges_file = 'data/pledges.json'
        self.rejected_pledges_file = 'data/rejected_pledges.json'
        
        # Initialize related models for business rule validation
        self.project_model = ProjectModel()
        self.user_model = UserModel()
    
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
    
    def create_pledge(self, user_id, project_id, amount, reward_id=''):
        """
        Create new pledge with business rule validation
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Validate project exists and is still active
            project = self.project_model.get_project_by_id(project_id)
            if not project:
                return self._reject_pledge(user_id, project_id, amount, reward_id, 
                                         "Project not found")
            
            # Business Rule 1: Check if project deadline is in the future
            if project['days_remaining'] <= 0:
                return self._reject_pledge(user_id, project_id, amount, reward_id, 
                                         "Project deadline has passed")
            
            # Business Rule 2: Validate reward tier if selected
            if reward_id:
                rewards = self.project_model.get_reward_tiers(project_id)
                selected_reward = None
                
                for reward in rewards:
                    if reward['id'] == reward_id:
                        selected_reward = reward
                        break
                
                if not selected_reward:
                    return self._reject_pledge(user_id, project_id, amount, reward_id, 
                                             "Selected reward tier not found")
                
                # Check minimum amount requirement
                if amount < selected_reward['min_amount']:
                    return self._reject_pledge(user_id, project_id, amount, reward_id, 
                                             f"Amount must be at least {selected_reward['min_amount']} for this reward")
                
                # Check reward quota availability
                if selected_reward['remaining_quota'] <= 0:
                    return self._reject_pledge(user_id, project_id, amount, reward_id, 
                                             "Selected reward tier is sold out")
            
            # All validations passed - create successful pledge
            pledge_id = f"pledge_{len(self._load_data(self.pledges_file)) + 1:06d}"
            
            new_pledge = {
                'id': pledge_id,
                'user_id': user_id,
                'project_id': project_id,
                'amount': amount,
                'reward_id': reward_id if reward_id else None,
                'pledge_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'successful'
            }
            
            # Save successful pledge
            pledges = self._load_data(self.pledges_file)
            pledges.append(new_pledge)
            self._save_data(pledges, self.pledges_file)
            
            # Business Rule 3: Update project amount and reward quota
            self.project_model.update_project_amount(project_id, amount)
            if reward_id:
                self.project_model.update_reward_quota(reward_id)
            
            return {'success': True, 'message': 'Pledge created successfully', 'pledge_id': pledge_id}
            
        except Exception as e:
            return self._reject_pledge(user_id, project_id, amount, reward_id, 
                                     f"System error: {str(e)}")
    
    def _reject_pledge(self, user_id, project_id, amount, reward_id, reason):
        """
        Record rejected pledge with reason
        Business Rule 4: Store rejected pledges for statistics
        """
        rejected_pledge = {
            'user_id': user_id,
            'project_id': project_id,
            'amount': amount,
            'reward_id': reward_id if reward_id else None,
            'rejection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rejection_reason': reason,
            'status': 'rejected'
        }
        
        # Save rejected pledge
        rejected_pledges = self._load_data(self.rejected_pledges_file)
        rejected_pledges.append(rejected_pledge)
        self._save_data(rejected_pledges, self.rejected_pledges_file)
        
        return {'success': False, 'message': reason}
    
    def get_user_pledges(self, user_id):
        """Get all pledges made by a specific user"""
        pledges = self._load_data(self.pledges_file)
        user_pledges = [p for p in pledges if p['user_id'] == user_id]
        
        # Add project information to each pledge
        for pledge in user_pledges:
            project = self.project_model.get_project_by_id(pledge['project_id'])
            pledge['project_name'] = project['name'] if project else 'Unknown Project'
        
        return user_pledges
    
    def get_project_pledges(self, project_id):
        """Get all successful pledges for a specific project"""
        pledges = self._load_data(self.pledges_file)
        project_pledges = [p for p in pledges if p['project_id'] == project_id]
        
        # Add user information to each pledge (without sensitive data)
        for pledge in project_pledges:
            user = self.user_model.get_user_by_id(pledge['user_id'])
            pledge['user_name'] = user['full_name'] if user else 'Anonymous'
        
        # Sort by pledge date (newest first)
        project_pledges.sort(key=lambda x: x['pledge_date'], reverse=True)
        
        return project_pledges
    
    def get_pledge_statistics(self):
        """
        Get comprehensive pledge statistics
        Required: Statistics of successful vs rejected pledges
        """
        successful_pledges = self._load_data(self.pledges_file)
        rejected_pledges = self._load_data(self.rejected_pledges_file)
        
        total_successful = len(successful_pledges)
        total_rejected = len(rejected_pledges)
        total_attempts = total_successful + total_rejected
        
        # Calculate success rate
        success_rate = (total_successful / total_attempts * 100) if total_attempts > 0 else 0
        
        # Calculate total amount pledged
        total_amount = sum(pledge['amount'] for pledge in successful_pledges)
        average_pledge = total_amount / total_successful if total_successful > 0 else 0
        
        # Analyze rejection reasons
        rejection_reasons = {}
        for rejection in rejected_pledges:
            reason = rejection['rejection_reason']
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
        # Get recent pledge activity (last 7 days)
        recent_successful = 0
        recent_rejected = 0
        current_date = datetime.now()
        
        for pledge in successful_pledges:
            pledge_date = datetime.strptime(pledge['pledge_date'], '%Y-%m-%d %H:%M:%S')
            if (current_date - pledge_date).days <= 7:
                recent_successful += 1
        
        for rejection in rejected_pledges:
            rejection_date = datetime.strptime(rejection['rejection_date'], '%Y-%m-%d %H:%M:%S')
            if (current_date - rejection_date).days <= 7:
                recent_rejected += 1
        
        return {
            'total_successful_pledges': total_successful,
            'total_rejected_pledges': total_rejected,
            'total_pledge_attempts': total_attempts,
            'success_rate_percentage': round(success_rate, 2),
            'total_pledged_amount': total_amount,
            'average_pledge_amount': round(average_pledge, 2),
            'recent_successful_pledges': recent_successful,
            'recent_rejected_pledges': recent_rejected,
            'top_rejection_reasons': dict(sorted(rejection_reasons.items(), 
                                               key=lambda x: x[1], reverse=True)[:5])
        }
    
    def get_top_backers(self, limit=10):
        """Get top backers by total pledge amount"""
        pledges = self._load_data(self.pledges_file)
        
        # Group pledges by user
        user_totals = {}
        for pledge in pledges:
            user_id = pledge['user_id']
            user_totals[user_id] = user_totals.get(user_id, 0) + pledge['amount']
        
        # Sort by total amount
        sorted_backers = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)
        
        # Add user information
        top_backers = []
        for user_id, total_amount in sorted_backers[:limit]:
            user = self.user_model.get_user_by_id(user_id)
            if user:
                top_backers.append({
                    'user_name': user['full_name'],
                    'username': user['username'],
                    'total_pledged': total_amount,
                    'pledge_count': len([p for p in pledges if p['user_id'] == user_id])
                })
        
        return top_backers
    
    def initialize_sample_data(self):
        """Initialize sample pledge data with both successful and rejected pledges"""
        # Load existing data
        projects = self.project_model.get_all_projects()
        users = self.user_model.get_all_users()
        
        if not projects or not users:
            print("Warning: Projects or Users not found. Initialize them first.")
            return
        
        successful_pledges = []
        rejected_pledges = []
        
        pledge_id = 1
        
        # Create sample successful pledges
        for i in range(50):  # Create 50 successful pledges
            user = random.choice(users)
            project = random.choice(projects)
            
            # Get project rewards for validation
            rewards = self.project_model.get_reward_tiers(project['id'])
            
            # Randomly decide if this pledge will have a reward
            use_reward = random.choice([True, False]) and rewards
            
            if use_reward:
                reward = random.choice(rewards)
                # Ensure pledge amount meets minimum requirement
                amount = random.uniform(reward['min_amount'], reward['min_amount'] * 2)
                reward_id = reward['id']
            else:
                # Pledge without reward tier
                amount = random.uniform(100, 5000)
                reward_id = None
            
            successful_pledge = {
                'id': f"pledge_{pledge_id:06d}",
                'user_id': user['id'],
                'project_id': project['id'],
                'amount': round(amount, 2),
                'reward_id': reward_id,
                'pledge_date': self._random_date_within_days(45),
                'status': 'successful'
            }
            
            successful_pledges.append(successful_pledge)
            pledge_id += 1
        
        # Create sample rejected pledges (various rejection reasons)
        rejection_reasons = [
            "Amount below minimum requirement for selected reward",
            "Selected reward tier is sold out",
            "Project deadline has passed",
            "Selected reward tier not found",
            "System error: Invalid project ID"
        ]
        
        for i in range(15):  # Create 15 rejected pledges
            user = random.choice(users)
            project = random.choice(projects)
            
            rejected_pledge = {
                'user_id': user['id'],
                'project_id': project['id'],
                'amount': round(random.uniform(50, 1000), 2),
                'reward_id': f"reward_{random.randint(1, 10)}" if random.choice([True, False]) else None,
                'rejection_date': self._random_date_within_days(45),
                'rejection_reason': random.choice(rejection_reasons),
                'status': 'rejected'
            }
            
            rejected_pledges.append(rejected_pledge)
        
        # Save sample data
        self._save_data(successful_pledges, self.pledges_file)
        self._save_data(rejected_pledges, self.rejected_pledges_file)
        
        print("Pledge sample data initialized successfully!")
        print(f"Created {len(successful_pledges)} successful pledges and {len(rejected_pledges)} rejected pledges")
    
    def _random_date_within_days(self, days):
        """Generate random datetime within specified days from now"""
        from datetime import timedelta
        
        base_date = datetime.now() - timedelta(days=days)
        random_days = random.randint(0, days)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        
        result_date = base_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        return result_date.strftime('%Y-%m-%d %H:%M:%S')