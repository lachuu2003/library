from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'vara'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PASSWORD'] = 'Sreedevi0#'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'exam'
mysql = MySQL(app)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT username, password,id FROM user_model WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['user_id'] = user[2]
            session['username'] = user[0]
            if user[0] == 'librarian':  # Librarian has username 'librarian'
                return redirect(url_for('librarian_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user_model (username, password) VALUES (%s, %s)", (username, pwd))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/librarian_dashboard')
def librarian_dashboard():
    if 'username' not in session or session['username'] != 'librarian':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    
    # Fetch all borrowed books with their return status
    cur.execute("""
        SELECT b.id, b.book_name, b.author, b.borrow_date, b.due_date, b.returned, u.username
        FROM borrowed_books b
        JOIN user_model u ON b.user_id = u.id
    """)
    borrow_list = cur.fetchall()
    cur.close()

    return render_template('librarian_dashboard.html', borrow_list=borrow_list)





@app.route('/remove_borrowed_book/<int:book_id>', methods=['POST'])
def remove_borrowed_book(book_id):
    if 'username' not in session or session['username'] != 'librarian':
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()

    # Fetch book details from the borrowed_books table
    cur.execute("SELECT book_name, author FROM borrowed_books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    
    if book:
        book_name = book[0]
        author = book[1]

        # Add book back to books table
        cur.execute("INSERT INTO books (name, author) VALUES (%s, %s)", (book_name, author))
        
        # Remove the book from borrowed_books table
        cur.execute("DELETE FROM borrowed_books WHERE id = %s", (book_id,))
        mysql.connection.commit()
    
    cur.close()
    return redirect(url_for('librarian_dashboard'))




@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session or session['username'] != 'librarian':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        author = request.form['author']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (name, author) VALUES (%s, %s)", (name, author))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('librarian_dashboard'))
    return render_template('add_book.html')

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'username' not in session or session['username'] == 'librarian':
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    cur = mysql.connection.cursor()
    
    # Fetch available books (not borrowed by this user)
    cur.execute("""
        SELECT id, name, author 
        FROM books 
        WHERE id NOT IN (
            SELECT book_id 
            FROM borrowed_books 
            WHERE user_id = %s AND returned = FALSE
        )
    """, (user_id,))
    available_books = cur.fetchall()
    
    # Fetch borrowed books by this user
    cur.execute("""
        SELECT b.book_name, b.author, b.borrow_date, b.due_date, b.returned
        FROM borrowed_books b
        WHERE b.user_id = %s
    """, (user_id,))
    borrowed_books = cur.fetchall()
    cur.close()
    
    return render_template('user_dashboard.html', available_books=available_books, borrowed_books=borrowed_books)





@app.route('/borrow', methods=['POST'])
def borrow_book():
    if 'username' not in session or session['username'] == 'librarian':
        return redirect(url_for('login'))

    book_id = request.form['book_id']
    user_id = session['user_id']

    cur = mysql.connection.cursor()

    # Fetch the book details to get the book name and author
    cur.execute("SELECT name, author FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    
    if book:
        book_name = book[0]
        author = book[1]  # Get the author from the fetched data

        # Insert borrowed book into borrowed_books table, including book_name and author
        cur.execute("""
            INSERT INTO borrowed_books (user_id, book_id, borrow_date, due_date, returned, book_name, author)
            VALUES (%s, %s, CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 14 DAY), FALSE, %s, %s)
        """, (user_id, book_id, book_name, author))
        
        # Remove book from books table (since it's now borrowed)
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('user_dashboard'))




@app.route('/return', methods=['POST'])
def return_book():
    if 'username' not in session or session['username'] == 'librarian':
        return redirect(url_for('login'))

    book_id = request.form['book_id']
    cur = mysql.connection.cursor()

    # Fetch book details from borrowed_books table
    cur.execute("SELECT book_name, author FROM borrowed_books WHERE book_id = %s AND user_id = %s", 
                (book_id, session['user_id']))
    book = cur.fetchone()
    
    if book:
        book_name = book[0]
        author = book[1]

        # Add book back to books table
        cur.execute("INSERT INTO books (name, author) VALUES (%s, %s)", (book_name, author))

        # Mark the book as returned in borrowed_books table
        cur.execute("UPDATE borrowed_books SET returned = TRUE WHERE book_id = %s AND user_id = %s", 
                    (book_id, session['user_id']))
        mysql.connection.commit()

    cur.close()
    return redirect(url_for('user_dashboard'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
