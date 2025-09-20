# app.py - Main Flask Application (Controller Layer in MVC)
"""
BirbFunding  - MVC 
=======================================

Author:66050265 Birb-png

"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
import json
import os

# Import Model classes (Data Layer)
from models.project_model import ProjectModel
from models.user_model import UserModel
from models.pledge_model import PledgeModel

# ===== APPLICATION CONFIGURATION =====

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'crowdfunding_secret_key_2024'  # For session management

# Configure template and static folders (View Layer)
app.template_folder = 'views'  # HTML templates location
app.static_folder = 'static'   # CSS, JS, images location

# Initialize Model instances (Data Access Objects)
project_model = ProjectModel()  # Handles project and reward data
user_model = UserModel()        # Handles user authentication and data
pledge_model = PledgeModel()    # Handles pledge transactions and validation

# ===== AUTHENTICATION CONTROLLERS =====

@app.route('/')
def index():
    """
    Home page controller - redirects to appropriate page based on auth status
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('projects_list'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login controller - handles both GET (show form) and POST (process login)
    """
    if request.method == 'POST':
        # Extract form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('login.html')
        
        # Authenticate user through Model
        user = user_model.authenticate(username, password)
        
        if user:
            # Successful authentication - create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('projects_list'))
        else:
            # Failed authentication
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    
    # GET request - show login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logout controller - clears session and redirects
    """
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('login'))

# ===== PROJECT CONTROLLERS =====

@app.route('/projects')
def projects_list():
    """
    Project listing controller - handles search, filtering, and sorting
    Implements: หน้ารวมโครงการ with search, filter, and sorting features
    """
    # Authentication check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Extract query parameters for filtering/sorting
    search_term = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    sort_option = request.args.get('sort_by', 'newest')
    
    try:
        # Get filtered and sorted projects from Model
        projects = project_model.get_filtered_projects(
            search=search_term,
            category=category_filter,
            sort_by=sort_option
        )
        
        # Get available categories for filter dropdown
        categories = project_model.get_all_categories()
        
        # Render View with data
        return render_template('projects_list.html',
                             projects=projects,
                             categories=categories,
                             current_search=search_term,
                             current_category=category_filter,
                             current_sort=sort_option)
                             
    except Exception as e:
        flash(f'Error loading projects: {str(e)}', 'error')
        return render_template('projects_list.html', 
                             projects=[], 
                             categories=[])

@app.route('/project/<project_id>')
def project_detail(project_id):
    """
    Project detail controller - shows individual project information
    Implements: หน้ารายละเอียดโครงการ with progress tracking
    """
    # Authentication check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get project data from Model
        project = project_model.get_project_by_id(project_id)
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('projects_list'))
        
        # Get related data
        reward_tiers = project_model.get_reward_tiers(project_id)
        project_pledges = pledge_model.get_project_pledges(project_id)
        
        # Render project detail view
        return render_template('projects_detail.html',
                             project=project,
                             rewards=reward_tiers,
                             pledges=project_pledges)
                             
    except Exception as e:
        flash(f'Error loading project details: {str(e)}', 'error')
        return redirect(url_for('projects_list'))

# ===== PLEDGE CONTROLLERS =====

@app.route('/pledge/<project_id>', methods=['POST'])
def make_pledge(project_id):
    """
    Pledge creation controller - handles project backing with business rule validation
    Implements all business rules from requirements
    """
    # Authentication check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Extract form data
        amount_str = request.form.get('amount', '').strip()
        reward_id = request.form.get('reward_id', '').strip()
        user_id = session['user_id']
        
        # Validate amount input
        if not amount_str:
            flash('Please enter a pledge amount', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                flash('Pledge amount must be greater than zero', 'error')
                return redirect(url_for('project_detail', project_id=project_id))
        except ValueError:
            flash('Please enter a valid amount', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        
        # Create pledge through Model (includes all business rule validation)
        result = pledge_model.create_pledge(
            user_id=user_id,
            project_id=project_id,
            amount=amount,
            reward_id=reward_id if reward_id else None
        )
        
        # Handle result
        if result['success']:
            flash(f'Thank you! Your pledge of ${amount:.2f} was successful!', 'success')
        else:
            flash(f'Pledge failed: {result["message"]}', 'error')
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('project_detail', project_id=project_id))

# ===== STATISTICS CONTROLLERS =====

@app.route('/statistics')
def statistics():
    """
    Statistics page controller - displays comprehensive platform analytics
    Implements: หน้าสรุปสถิติ with success/rejection metrics
    """
    # Authentication check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Gather statistics from all Models
        pledge_statistics = pledge_model.get_pledge_statistics()
        project_statistics = project_model.get_project_statistics()
        user_statistics = user_model.get_user_statistics()
        
        # Get additional analytics data
        top_backers = pledge_model.get_top_backers(limit=10)
        
        # Render statistics view
        return render_template('statistics.html',
                             stats=pledge_statistics,
                             project_stats=project_statistics,
                             user_stats=user_statistics,
                             top_backers=top_backers)
                             
    except Exception as e:
        flash(f'Error loading statistics: {str(e)}', 'error')
        return render_template('statistics.html',
                             stats={},
                             project_stats={},
                             user_stats={})

# ===== USER PROFILE CONTROLLERS =====

@app.route('/profile')
def user_profile():
    """
    User profile controller - shows user's pledge history and statistics
    """
    # Authentication check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        user_id = session['user_id']
        
        # Get user data and pledges from Models
        user = user_model.get_user_by_id(user_id)
        user_pledges = pledge_model.get_user_pledges(user_id)
        
        # Calculate user statistics
        total_pledged = sum(pledge['amount'] for pledge in user_pledges)
        projects_backed = len(set(pledge['project_id'] for pledge in user_pledges))
        
        return render_template('user_profile.html',
                             user=user,
                             pledges=user_pledges,
                             total_pledged=total_pledged,
                             projects_backed=projects_backed)
                             
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('projects_list'))

# ===== API CONTROLLERS (For AJAX/Real-time updates) =====

@app.route('/api/project/<project_id>/progress')
def api_project_progress(project_id):
    """
    API controller for real-time project progress updates
    Returns JSON data for AJAX requests
    """
    # Authentication check
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get project data from Model
        project = project_model.get_project_by_id(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get current pledge count
        pledges = pledge_model.get_project_pledges(project_id)
        
        # Return JSON response
        return jsonify({
            'success': True,
            'current_amount': project['current_amount'],
            'goal_amount': project['goal_amount'],
            'progress_percentage': min((project['current_amount'] / project['goal_amount']) * 100, 100),
            'days_remaining': project['days_remaining'],
            'backers_count': len(pledges),
            'status': 'active' if project['days_remaining'] > 0 else 'expired'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/summary')
def api_statistics_summary():
    """
    API controller for dashboard statistics (for charts and widgets)
    """
    # Authentication check
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get summary statistics from Models
        pledge_stats = pledge_model.get_pledge_statistics()
        project_stats = project_model.get_project_statistics()
        
        return jsonify({
            'success': True,
            'pledge_success_rate': pledge_stats.get('success_rate_percentage', 0),
            'total_pledges': pledge_stats.get('total_successful_pledges', 0),
            'total_projects': project_stats.get('total_projects', 0),
            'active_projects': project_stats.get('active_projects', 0),
            'total_raised': pledge_stats.get('total_pledged_amount', 0)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors"""
    flash('The requested page was not found', 'error')
    return redirect(url_for('projects_list'))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    flash('An internal server error occurred', 'error')
    return redirect(url_for('projects_list'))

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors"""
    flash('Access denied', 'error')
    return redirect(url_for('login'))

# ===== TEMPLATE FILTERS (View helpers) =====

@app.template_filter('currency')
def currency_filter(amount):
    """Format numbers as currency"""
    return "${:,.2f}".format(float(amount))

@app.template_filter('percentage')
def percentage_filter(value):
    """Format numbers as percentages"""
    return "{:.1f}%".format(float(value))

@app.template_filter('days_remaining')
def days_remaining_filter(days):
    """Format days remaining text"""
    if days <= 0:
        return "Expired"
    elif days == 1:
        return "1 day left"
    else:
        return f"{days} days left"

# ===== CONTEXT PROCESSORS (Global template variables) =====

@app.context_processor
def inject_global_data():
    """
    Inject global data into all templates
    This makes data available to all views without passing explicitly
    """
    if 'user_id' in session:
        try:
            # Get quick stats for navigation/footer
            project_stats = project_model.get_project_statistics()
            return {
                'global_project_count': project_stats.get('total_projects', 0),
                'global_active_count': project_stats.get('active_projects', 0)
            }
        except:
            pass
    
    return {}

# ===== APPLICATION INITIALIZATION =====

def initialize_sample_data():
    """
    Initialize sample data for demonstration
    Creates all required sample data as per requirements
    """
    print("🔄 Initializing sample data...")
    
    # Initialize each model's sample data
    project_model.initialize_sample_data()  # 8+ projects, 3+ categories
    user_model.initialize_sample_data()     # 10+ users
    pledge_model.initialize_sample_data()   # Mix of successful/rejected pledges
    
    print("✅ Sample data initialization complete!")

def display_startup_info():
    """
    Display system information on startup by reading from setup.txt
    """
    try:
        # Read setup information from setup.txt file
        with open('setup.txt', 'r', encoding='utf-8') as file:
            setup_content = file.read()
            print(setup_content)
    except FileNotFoundError:
        # Fallback if setup.txt doesn't exist T-T
        print("\n" + "="*70)
        print("🚀 CROWDFUNDING PLATFORM - MVC ARCHITECTURE")
        print("="*70)
        print(" setup.txt file not found. Using default startup message.")
        print("="*70)
    except Exception as e:
        # Fallback for any other error
        print(f"\n  Error reading setup.txt: {e}")
        print("Using default startup message.")

# ===== MAIN APPLICATION ENTRY POINT =====

if __name__ == '__main__':
    """
    Main application entry point
    Initializes data and starts the Flask development server
    """
    
    # Check if this is first run (no data directory exists)
    if not os.path.exists('data'):
        print(" First run detected - setting up system...")
        os.makedirs('data', exist_ok=True)
        initialize_sample_data()
        display_startup_info()
    else:
        print(" Crowdfunding Platform starting...")
        print(" Server: http://localhost:5000")
        print(" Use Ctrl+C to stop the server")
        display_startup_info()
    
    # Start Flask development server
    # debug=True enables auto-reload and detailed error messages
    app.run(debug=True, host='0.0.0.0', port=5000)