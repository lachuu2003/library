Library Management System
----------------------------


A Library Management System built with HTML, CSS, Flask, and MySQL. This project provides a simple yet effective way to manage books, users, and transactions in a library environment.

🚀 Tech Stack
--------------
HTML – for structuring the web pages

CSS – for styling and layout

Flask – lightweight Python web framework for backend logic

MySQL – relational database for storing library records

✨ Features
--------------

User Management: Add, update, and delete user accounts

Book Catalog: Manage book details including title, author, and availability

Issue/Return System: Track borrowing and returning of books

Search Functionality: Find books by title, author, or category

Admin Dashboard: Overview of users, books, and transactions

🛠️ Installation & Setup
----------------------------

dependencies:
-------------
pip install -r requirements.txt

Configure MySQL database in config.py:

python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "yourpassword"
DB_NAME = "library_db"
Run the Flask app:

bash
flask run
