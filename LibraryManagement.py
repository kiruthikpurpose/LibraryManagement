import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# Database connection and cursor
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Database table creation
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        password TEXT,
                        role TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        author TEXT,
                        price REAL,
                        available INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS borrow (
                        borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        book_id INTEGER,
                        borrow_date TEXT,
                        return_date TEXT,
                        returned INTEGER,
                        penalty REAL,
                        FOREIGN KEY(user_id) REFERENCES users(user_id),
                        FOREIGN KEY(book_id) REFERENCES books(book_id))''')
    conn.commit()

# User management
def add_user(username, password, role):
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

def login(username, password, role):
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
    return cursor.fetchone()

# Book management
def add_book(title, author, price):
    cursor.execute("INSERT INTO books (title, author, price, available) VALUES (?, ?, ?, ?)", (title, author, price, 1))
    conn.commit()

def view_books():
    cursor.execute("SELECT * FROM books")
    return cursor.fetchall()

def borrow_book(user_id, book_id):
    cursor.execute("SELECT available FROM books WHERE book_id = ?", (book_id,))
    available = cursor.fetchone()[0]
    
    if available:
        borrow_date = datetime.now().strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO borrow (user_id, book_id, borrow_date, return_date, returned, penalty) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, book_id, borrow_date, return_date, 0, 0))
        cursor.execute("UPDATE books SET available = 0 WHERE book_id = ?", (book_id,))
        conn.commit()
        messagebox.showinfo("Success", f"Book borrowed! Return date: {return_date}")
    else:
        messagebox.showwarning("Unavailable", "Book is not available.")

def view_member_borrowed_books(user_id):
    cursor.execute('''SELECT books.title, borrow.borrow_date, borrow.return_date, borrow.penalty 
                      FROM borrow 
                      JOIN books ON borrow.book_id = books.book_id 
                      WHERE borrow.user_id = ? AND borrow.returned = 0''', (user_id,))
    return cursor.fetchall()

def check_overdue_penalties():
    cursor.execute('''SELECT borrow.borrow_id, borrow.user_id, borrow.book_id, borrow.return_date, books.price 
                      FROM borrow
                      JOIN books ON borrow.book_id = books.book_id
                      WHERE borrow.returned = 0''')
    
    borrows = cursor.fetchall()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for borrow in borrows:
        if borrow[3] < today:
            overdue_days = (datetime.now() - datetime.strptime(borrow[3], "%Y-%m-%d")).days
            penalty = overdue_days * 1
            cursor.execute("UPDATE borrow SET penalty = ? WHERE borrow_id = ?", (penalty, borrow[0]))
            conn.commit()

# UI functions
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def login_screen():
    clear_screen()
    tk.Label(root, text="Login", font=("Arial", 20)).pack(pady=10)
    
    tk.Label(root, text="Username:").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()
    
    tk.Label(root, text="Password:").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()
    
    role_var = tk.StringVar(value="member")
    tk.Radiobutton(root, text="Member", variable=role_var, value="member").pack()
    tk.Radiobutton(root, text="Admin", variable=role_var, value="admin").pack()
    
    def login_action():
        username = username_entry.get()
        password = password_entry.get()
        role = role_var.get()
        
        user = login(username, password, role)
        if user:
            if role == "admin":
                admin_panel()
            else:
                member_panel(user[0])
        else:
            messagebox.showwarning("Login Failed", "Invalid credentials")
    
    tk.Button(root, text="Login", command=login_action).pack(pady=10)

def admin_panel():
    clear_screen()
    tk.Label(root, text="Admin Panel", font=("Arial", 20)).pack(pady=10)
    
    tk.Button(root, text="View All Books", command=show_books).pack(pady=5)
    tk.Button(root, text="Add Book", command=add_book_screen).pack(pady=5)
    tk.Button(root, text="Check Penalties", command=check_overdue_penalties_screen).pack(pady=5)
    tk.Button(root, text="Logout", command=login_screen).pack(pady=5)

def member_panel(user_id):
    clear_screen()
    tk.Label(root, text="Member Panel", font=("Arial", 20)).pack(pady=10)
    
    tk.Button(root, text="View Borrowed Books", command=lambda: view_borrowed_books_screen(user_id)).pack(pady=5)
    tk.Button(root, text="Borrow Book", command=lambda: borrow_book_screen(user_id)).pack(pady=5)
    tk.Button(root, text="Logout", command=login_screen).pack(pady=5)

def show_books():
    clear_screen()
    tk.Label(root, text="All Books", font=("Arial", 20)).pack(pady=10)
    
    books = view_books()
    for book in books:
        tk.Label(root, text=f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Price: {book[3]}, Available: {book[4]}").pack()
    
    tk.Button(root, text="Back", command=admin_panel).pack(pady=10)

def add_book_screen():
    clear_screen()
    tk.Label(root, text="Add Book", font=("Arial", 20)).pack(pady=10)
    
    tk.Label(root, text="Title:").pack()
    title_entry = tk.Entry(root)
    title_entry.pack()
    
    tk.Label(root, text="Author:").pack()
    author_entry = tk.Entry(root)
    author_entry.pack()
    
    tk.Label(root, text="Price:").pack()
    price_entry = tk.Entry(root)
    price_entry.pack()
    
    def add_book_action():
        title = title_entry.get()
        author = author_entry.get()
        price = float(price_entry.get())
        add_book(title, author, price)
        messagebox.showinfo("Success", "Book added successfully!")
        admin_panel()
    
    tk.Button(root, text="Add Book", command=add_book_action).pack(pady=10)
    tk.Button(root, text="Back", command=admin_panel).pack(pady=10)

def borrow_book_screen(user_id):
    clear_screen()
    tk.Label(root, text="Borrow Book", font=("Arial", 20)).pack(pady=10)
    
    books = view_books()
    for book in books:
        tk.Label(root, text=f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Price: {book[3]}, Available: {book[4]}").pack()
    
    tk.Label(root, text="Enter Book ID:").pack()
    book_id_entry = tk.Entry(root)
    book_id_entry.pack()
    
    def borrow_action():
        book_id = int(book_id_entry.get())
        borrow_book(user_id, book_id)
    
    tk.Button(root, text="Borrow", command=borrow_action).pack(pady=10)
    tk.Button(root, text="Back", command=lambda: member_panel(user_id)).pack(pady=10)

def view_borrowed_books_screen(user_id):
    clear_screen()
    tk.Label(root, text="Your Borrowed Books", font=("Arial", 20)).pack(pady=10)
    
    borrowed_books = view_member_borrowed_books(user_id)
    for book in borrowed_books:
        tk.Label(root, text=f"Book: {book[0]}, Borrowed on: {book[1]}, Return by: {book[2]}, Penalty: {book[3]}").pack()
    
    tk.Button(root, text="Back", command=lambda: member_panel(user_id)).pack(pady=10)

def check_overdue_penalties_screen():
    check_overdue_penalties()
    messagebox.showinfo("Penalties Updated", "Overdue penalties have been updated!")
    admin_panel()

# Initialize database and create default users
create_tables()

cursor.execute("SELECT * FROM users")
if not cursor.fetchall():
    add_user("admin", "password123", "admin")
    add_user("member", "12345678", "member")

# Initialize GUI
root = tk.Tk()
root.title("Library Management System")
root.geometry("500x400")

login_screen()
root.mainloop()

# Close database connection
conn.close()
