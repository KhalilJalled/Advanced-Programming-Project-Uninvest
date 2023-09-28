
import tkinter as tk
import sqlite3
from SignUp import sign_up
from LogIn import log_in

# Connect to database
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Create a tkinter window
Welcome_window = tk.Tk()
Welcome_window.title("Uninvest - Welcome")
Welcome_window.geometry("500x500")

# Add a welcome message
label_welcome = tk.Label(Welcome_window, text="Welcome to Uninvest",
                          font=("Calibri", 18), fg="blue")
label_welcome.pack(pady=20)

# Add a message for new users
label_new_user = tk.Label(Welcome_window, text="If you don't have an account yet, please sign up:",
                          font=("Calibri", 12), fg="gray")
label_new_user.pack(pady=10)

# Add a sign-up button
button_sign_up = tk.Button(Welcome_window, text="Sign Up", font=("Calibri", 14),
                           bg="blue", fg="white", width=15, command=sign_up)
button_sign_up.pack(pady=10)

# Add a message for existing users
label_existing_user = tk.Label(Welcome_window, text="If you already have an account, please log in:",
                               font=("Calibri", 12), fg="gray")
label_existing_user.pack(pady=10)

# Add a log-in button
button_log_in = tk.Button(Welcome_window, text="Log In", font=("Calibri", 14),
                          bg="blue", fg="white", width=15, command=log_in)
button_log_in.pack(pady=10)

# Add a message at the bottom
label_bottom = tk.Label(Welcome_window, text="Welcome to Uninvest, your new investing platform created by Nathalie, Kamila, and Khalil.\n\n"
                                             "If you're new here, please sign up to create an account and start investing today!\n\n"
                                             "If you already have an account, simply log in to access your portfolio and make trades.",
                        font=("Calibri", 10), fg="gray")
label_bottom.pack(side="bottom", pady=20)

# Run the tkinter event loop
Welcome_window.mainloop()
