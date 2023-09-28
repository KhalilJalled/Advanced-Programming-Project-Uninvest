import sqlite3
from Mainaccount import mainaccount
import tkinter as tk
from tkinter import messagebox
#Function that shows the login window with its entries
def log_in():
    LogIn_window = tk.Tk()
    LogIn_window.title('Log In')

    # Create labels and entries for user input
    label_email = tk.Label(LogIn_window, text="Email", font=("Calibri", 12))
    label_email.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    entry_email = tk.Entry(LogIn_window, font=("Calibri", 12), width=25)
    entry_email.grid(row=1, column=1, padx=20, pady=10)

    label_password = tk.Label(LogIn_window, text="Password", font=("Calibri", 12))
    label_password.grid(row=2, column=0, padx=20, pady=10, sticky='w')
    entry_password = tk.Entry(LogIn_window, show="*", font=("Calibri", 12), width=25)
    entry_password.grid(row=2, column=1, padx=20, pady=10)

    # Function to check the user's input against the database
    def check_login():
        email = entry_email.get()
        password = entry_password.get()

        # Open a connection to the database
        conn = sqlite3.connect("user_data.db")
        c = conn.cursor()

        # Execute a SELECT query to check if the email and password are in the database
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        result = c.fetchone()

        # Close the connection to the database
        conn.close()

        # If the query returned a result, the user's input is correct
        if result is not None:
            go_to_main()
        else:
            messagebox.showerror("Error", "Incorrect email or password")
    #Function to call the main window of the platform after successful login
    def go_to_main():
        LogIn_window.destroy()
        mainaccount()

    # Create a submit button that calls the check_login function when clicked
    submit_button = tk.Button(LogIn_window, text="Log In", font=("Calibri", 12), bg='#0052cc', fg='white',
                              width=15, height=2, command=check_login)
    submit_button.grid(row=3, column=1, padx=20, pady=10)

    # Add padding and configure the grid
    for i in range(4):
        LogIn_window.rowconfigure(i, weight=1)
    for i in range(2):
        LogIn_window.columnconfigure(i, weight=1)

    LogIn_window.mainloop()