
## Author

**66050265 Birb-png**  
Year 3, Term 1 - MVC Exit Exam
-- Some code are from different project of mine...

# Key Features Explained

### 1. MVC Architecture
- **Model**: Data access and business logic (`models/` directory)
- **View**: User interface templates (`views/` directory)
- **Controller**: Request handling and coordination (`main.py`)

### 2. Database Schema
The application uses JSON files to simulate a database with the following structure:

#### Projects Table
- `id`: 8-digit project identifier
- `name`: Project title
- `description`: Project description
- `category`: Project category
- `goal_amount`: Funding target
- `current_amount`: Amount raised
- `deadline`: Project end date
- `creator`: Project creator
- `status`: Project status

#### Users Table
- `id`: User identifier
- `username`: Login username
- `password`: Hashed password
- `email`: User email
- `full_name`: Display name
- `status`: Account status

#### Pledges Table
- `id`: Pledge identifier
- `user_id`: Pledger ID
- `project_id`: Project ID
- `amount`: Pledge amount
- `reward_id`: Selected reward tier
- `pledge_date`: Transaction date
- `status`: Pledge status

### 3. Interactive Features

#### Automatic Amount Filling
- Select a reward tier to automatically fill the minimum pledge amount
- Real-time validation with visual feedback
- Smart form behavior for better user experience

#### Real-time Updates
- Live progress tracking
- Automatic statistics refresh
- Dynamic content updates

## Configuration

### Environment Variables
The application uses default configuration. To customize:

```python
# In main.py
app.secret_key = 'your-secret-key-here'  # Change for production
```

### Database
The application uses JSON files for data storage. To reset data:
1. Delete files in `data/` directory
2. Restart the application
3. Sample data will be automatically generated

## Usage Guide

### For Users
1. **Login** with demo credentials
2. **Browse Projects** on the main page
3. **View Project Details** by clicking on any project
4. **Make a Pledge** by selecting a reward tier and amount
5. **View Statistics** to see platform analytics

### For Developers
1. **Models**: Add business logic in `models/` directory
2. **Views**: Modify templates in `views/` directory
3. **Controllers**: Add routes in `main.py`
4. **Styling**: Update CSS in `static/css/` directory

## Customization

### Themes
The application uses a dark theme. To customize:
1. Modify CSS variables in `static/css/style.css`
2. Update color schemes in `:root` selector
3. Adjust component-specific styles


### Common Issues

#### Port Already in Use
```bash
# Kill process using port 5000
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

#### Module Not Found
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

#### Data Not Loading
- Check if `data/` directory exists
- Verify JSON files are valid
- Restart the application

## 📊 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout user

### Projects
- `GET /projects` - List all projects
- `GET /project/<id>` - View project details
- `POST /pledge/<id>` - Make a pledge

### Statistics
- `GET /statistics` - Statistics dashboard
- `GET /api/project/<id>/progress` - Project progress API
- `GET /api/statistics/summary` - Statistics summary API


**Happy Programming !**