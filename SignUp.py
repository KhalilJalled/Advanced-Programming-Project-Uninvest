import tkinter as tk
import sqlite3
from LogIn import log_in
from tkinter import messagebox
import re

# Structure of the email that the user should use to enter a valid email
email_regex = "^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$"

# Function that checks if the email entered matches the structure provided above
def is_valid_email(email):
    return bool(re.match(email_regex, email))

# Function that creates the window of the sign up form
def sign_up():
    SignUp_window = tk.Tk()
    SignUp_window.title('Sign Up')

    # Add padding and spacing between widgets
    padx = 10
    pady = 5
    spacing = 10

    # Add a frame to group the widgets
    frame = tk.Frame(SignUp_window, padx=padx, pady=pady)
    frame.pack()

    # Add a title label
    title_label = tk.Label(frame, text="Create an account", font=("Calibri", 16))
    title_label.grid(row=0, column=0, columnspan=2, pady=pady)

    # Add labels and entry boxes for name
    name_label = tk.Label(frame, text="Name:", font=("Calibri", 12))
    name_label.grid(row=1, column=0, sticky="e", padx=padx, pady=pady)
    name_entry = tk.Entry(frame, font=("Calibri", 12))
    name_entry.grid(row=1, column=1, padx=padx, pady=pady)

    # Add labels and entry boxes for email
    email_label = tk.Label(frame, text="Email:", font=("Calibri", 12))
    email_label.grid(row=2, column=0, sticky="e", padx=padx, pady=pady)
    email_entry = tk.Entry(frame, font=("Calibri", 12))
    email_entry.grid(row=2, column=1, padx=padx, pady=pady)

    # Add labels and entry boxes for password
    password_label = tk.Label(frame, text="Password:", font=("Calibri", 12))
    password_label.grid(row=3, column=0, sticky="e", padx=padx, pady=pady)
    password_entry = tk.Entry(frame, font=("Calibri", 12), show="*")
    password_entry.grid(row=3, column=1, padx=padx, pady=pady)

    # Add labels and entry boxes for password verification
    password_verification_label = tk.Label(frame, text="Verify password:", font=("Calibri", 12))
    password_verification_label.grid(row=4, column=0, sticky="e", padx=padx, pady=pady)
    password_verification_entry = tk.Entry(frame, font=("Calibri", 12), show="*")
    password_verification_entry.grid(row=4, column=1, padx=padx, pady=pady)

    # Add a button to submit the form
    submit_button = tk.Button(frame, text="Sign Up", font=("Calibri", 12), command=lambda: save_user(name_entry.get(), email_entry.get(), password_entry.get(), password_verification_entry.get()))

    submit_button.grid(row=5, column=1, pady=pady)

    # Add a button to go to the login page
    login_button = tk.Button(frame, text="Already have an account? Log in here", font=("Calibri", 12), command=lambda: go_to_login())
    login_button.grid(row=6, column=0, columnspan=2, pady=pady)

    # Function to check if the data provided are acceptable before storing them in the database
    def save_user(name, email, password,verify_password):
        if not is_valid_email(email):
            messagebox.showerror("Invalid email", "Please enter a valid email address.")
            return
        if password != verify_password:
            tk.messagebox.showerror("Passwords do not match",
                                    "The passwords you entered do not match. Please try again.")
            return
        
        # Store user information in a database
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()

        # Input the user's information in the database
        c.execute('''
            CREATE TABLE IF NOT EXISTS users
            (name TEXT NOT NULL,
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL)
        ''')
        conn.commit()
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()
        go_to_login()

    # Open the log-in window when the sign-up is completed
    def go_to_login():
        SignUp_window.destroy()
        log_in()

    SignUp_window.mainloop()


