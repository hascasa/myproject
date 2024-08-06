
## Run Redis server
redis-server

## Start the Celery worker
celery -A eLearning worker --loglevel=info


## Run the ASGI Server ##

uvicorn eLearning.asgi:application



# eLearning Django Application

This is a sample eLearning application built using Django. It includes features such as user authentication, course management, and real-time communication using WebSockets.

## Features

- User Registration and Authentication
- Course Creation and Management
- Enroll in Courses
- Real-time Chat for Courses
- Feedback System
- User Profile Management
- Real-time Notifications

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/hascasa/myproject.git
    cd myproject
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Apply the migrations:
    ```bash
    python manage.py migrate
    ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

7. Open your browser and go to `http://127.0.0.1:8000` to access the application.

## Usage

### Admin Interface

The admin interface is accessible at `http://127.0.0.1:8000/admin`. You can manage users, courses, and other data from here.

### API

The API is accessible at `http://127.0.0.1:8000/api`. It allows you to perform CRUD operations on users and courses.

