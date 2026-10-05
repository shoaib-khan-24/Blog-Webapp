# Blog Webapp

A fully functional blogging website built with Python and Flask. The application allows users to register, log in, create and manage blog posts, leave comments, and contact the site owner through a contact form powered by Twilio.

## Features

- User registration and login system
- Secure password hashing with Werkzeug
- Admin-only access for creating, editing, and deleting posts
- Blog post creation with title, subtitle, cover image, and rich text content
- Comments on posts
- Responsive UI using Bootstrap
- Contact form that sends SMS notifications via Twilio
- Gravatar support for user avatars

## Tech Stack

- Python
- Flask
- Flask-Login
- SQLAlchemy
- Flask-WTF / WTForms
- Bootstrap-Flask
- Flask-CKEditor
- Flask-Gravatar
- Twilio

## Project Structure

- `main.py` – application routes, database models, and app configuration
- `forms.py` – form definitions for login, registration, posts, comments, and contact
- `templates/` – HTML templates for the web interface
- `static/` – CSS, JavaScript, and static assets
- `requirements.txt` – Python dependencies

## Prerequisites

- Python 3.9+
- pip
- A Twilio account for the contact form (optional if you do not plan to use SMS notifications)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/shoaib-khan-24/Blog-Webapp.git
cd Blog-Webapp
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

3. Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root and add the following values for Twilio support:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE=your_twilio_phone_number
ADMIN_PHONE=admin_phone_number
```

These variables are loaded at runtime by `python-dotenv`.

## Running the App

Start the Flask server:

```bash
python main.py
```

Then open your browser and visit:

```text
http://127.0.0.1:5002
```

## Usage

- Register a new account to access the blogging platform.
- The first registered user is treated as the admin user and can create, edit, and delete posts.
- Use the "New Post" page to publish blog content.
- Visitors can leave comments on individual posts.
- The contact page allows users to send a message and trigger a Twilio SMS notification.

## License

This project is open for educational and personal use.

## Acknowledgements

- Flask documentation and community
- Bootstrap for the responsive front-end
- SQLAlchemy for database management
- Twilio for SMS notifications
