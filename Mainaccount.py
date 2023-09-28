import tkinter as tk
import sqlite3
import yfinance as yf
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.ttk as ttk
import tkinter.font as tkfont
import requests
import pandas as pd
from Portfoliomanager1 import MDP
from Portfoliomanager1 import RWP
from Portfoliomanager1 import EWP
from Portfoliomanager1 import calculate_portfolio_statistics
from matplotlib.figure import Figure

# First balance available to the user
balance = 10000

# Store the transactions
transactions = []

# Function that connects to database
def initialize_database():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    # Create the stocks table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS stock_data
                 (symbol TEXT PRIMARY KEY, price REAL)''')
    conn.commit()
    return conn, c

# Function that displays a plot of the stock's price evolution over 1 year
def display_stock_history(parent_window, c, stock):
    
    # Download the historical data
    stock_info = yf.Ticker(stock)
    hist_data = stock_info.history(period="1y")

    history_window = tk.Toplevel(parent_window)
    history_window.title(f"{stock} - Historical Data")
    history_window.geometry("900x800")

    # Create a plot of the stock's price evolution
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(hist_data.index, hist_data["Close"])
    ax.set_title(f"{stock} Price Evolution")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    # Add the plot to the history_window using a canvas
    canvas = FigureCanvasTkAgg(fig, master=history_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Add an Entry field for the investment amount
    entry_invest = tk.Entry(history_window)
    entry_invest.pack(pady=5)

    #Function that checks if there is sufficient funds to invest in the stock
    def invest():
        global balance
        global transactions
        amount = float(entry_invest.get())
        current_stock_price = get_stock_price(c, stock)

        # If the amount is higher return an error
        if amount > balance:
            tk.messagebox.showerror("Error", "Not enough funds. Your account balance is" f"\n${balance:,.2f} USD" )

        # Otherwise take the amount out of the balance and compute the number shares bought and append it to the transactions' list
        else:
            balance -= amount
            stocks_bought = amount / current_stock_price
            transactions.append((stock, current_stock_price, stocks_bought, amount))
            history_window.destroy()

    # Add the Invest button
    button_invest = tk.Button(history_window, text="Invest", font=("Calibri", 12),
                              bg="blue", fg="white", width=10, command=invest)
    button_invest.pack(pady=5)

    # Add a close button to the history_window
    button_close = tk.Button(history_window, text="Close", font=("Calibri", 12),
                             bg="blue", fg="white", width=10, command=history_window.destroy)
    button_close.pack(side=tk.BOTTOM, pady=10)

# Function that creates a button for each stock we add to the portfolio
def create_stock_buttons(parent_window, frame, stocks_list, c):

    # Create a scrollbar for the frame
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a canvas for the frame with the scrollbar attached
    canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure the scrollbar to scroll the canvas
    scrollbar.config(command=canvas.yview)

    # Create a frame inside the canvas for the buttons
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Create the buttons inside the inner frame
    for stock in stocks_list:
        stock_price = get_stock_price(c, stock)
        button_text = f"{stock} (${stock_price:.2f})" if stock_price is not None else stock
        button_stock = tk.Button(inner_frame, text=button_text, font=("Calibri", 12),
                                 bg="blue", fg="white", width=15,
                                 command=lambda stock=stock: display_stock_history(parent_window, c, stock))

        button_stock.pack(side="top", pady=5)

    # Configure the canvas to resize when the inner frame changes size
    inner_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

# Function that opens a new window where the user's transactions and portfolio statistics are displayed 
def display_user_info(parent_window):
    user_info_window = tk.Toplevel(parent_window)
    user_info_window.title("User Information")
    user_info_window.geometry("1200x700")

    # Create the Treeview widget
    columns = ("Share Name", "Share Price", "Number of Shares Bought", "Amount Invested", "Weight")
    transactions_tree = ttk.Treeview(user_info_window, columns=columns, show="headings")

    # Configure column headings
    for col in columns:
        transactions_tree.heading(col, text=col)
        transactions_tree.column(col, minwidth=0, width=tkfont.Font().measure(col.title()) + 2)

    # Insert transaction data
    total_investment = sum(transaction[3] for transaction in transactions)
    portfolio_weights = []
    stock_names = []

    # For each transaction, show the stock's price, stock's name, amount invested, compute and show the weights
    for transaction in transactions:
        stock, stock_price, stocks_bought, amount_invested = transaction
        if stock not in stock_names:
            stock_names.append(stock)
            weight = amount_invested / total_investment
            portfolio_weights.append(weight)
        transactions_tree.insert("", "end", values=(
            stock, f"${stock_price:.2f}", f"{stocks_bought:.2f}", f"${amount_invested:.2f}", f"{weight:.2%}"))

    # Add label for transaction history
    history_label = tk.Label(user_info_window, text="History of Transactions", font=("Calibri", 14, "bold"))
    history_label.grid(row=0, column=0, pady=10, sticky="w")

    transactions_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Create a figure 
    fig = Figure(figsize=(4, 4))  
    ax = fig.add_subplot(111)

    # Create a pie chart to display the weights 
    ax.pie(portfolio_weights, labels=stock_names, autopct='%1.1f%%', startangle=90)
    ax.set_aspect('equal')  
    ax.set_title('Portfolio Weights')

    # Create a Tkinter canvas to display the chart
    canvas = FigureCanvasTkAgg(fig, master=user_info_window)
    canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    canvas.draw()

    # Calculate and display portfolio statistics
    portfolio_return, portfolio_risk, sharpe_ratio, beta = calculate_portfolio_statistics(transactions)

    # Create a frame for key statistics
    stats_frame = tk.Frame(user_info_window)
    stats_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    # Add label for key statistics
    stats_label = tk.Label(stats_frame, text="Key Statistics", font=("Calibri", 14, "bold"))
    stats_label.pack(anchor="w")

    stats_labels = [
        f"Portfolio Return: {portfolio_return * 100:.2f}%",
        f"Portfolio Risk: {portfolio_risk * 100:.2f}%",
        f"Sharpe Ratio: {sharpe_ratio:.2f}",
        f"Beta: {beta:.2f}",
    ]

    for stat in stats_labels:
        stat_label = tk.Label(stats_frame, text=stat, font=("Calibri", 12))
        stat_label.pack(anchor="w")

    # Add the 'Set Preferences' button
    select_preferences_button = tk.Button(user_info_window, text="Set Preferences", bg="blue", fg="white", width=15,
                                          command=lambda: open_preferences_window(user_info_window))
    select_preferences_button.grid(row=3, column=0, pady=10, sticky="w")

    button_close = tk.Button(user_info_window, text="Close", font=("Calibri", 12),
                             bg="blue", fg="white", width=10, command=user_info_window.destroy)
    button_close.grid(row=3, column=1, pady=10)

# Function that retrieves the new weights and investments for the chosen strategy and displays the result in a new window
def show_new_weights_and_investments(parent_window, portfolio_function):

    # Calculate new portfolio weights, investments and new key statistics
    global transactions
    new_weights, investments, portfolio_return, portfolio_risk, sharpe_ratio, beta = portfolio_function(transactions)

    # Create a new window to display the results
    results_window = tk.Toplevel(parent_window)
    results_window.title(f"New Weights and Investments ({portfolio_function.__name__})")
    results_window.geometry("800x400")

    Comment_label = tk.Label(results_window,
                             text="According to the portfolio allocation strategy selected, this will be the new performance of your portfolio:",
                             font=("Calibri", 12), fg="gray")
    Comment_label.grid(row=0, column=0, sticky='w', padx=10, pady=10, columnspan=5)

    # Display new portfolio weights
    weights_label = tk.Label(results_window, text="New Portfolio Weights:", font=("Calibri", 14, "bold"))
    weights_label.grid(row=1, column=0, sticky='w', padx=10, pady=10)
    unique_stocks = list({transaction[0] for transaction in transactions})

    for idx, (stock, weight) in enumerate(zip(unique_stocks, new_weights)):
        weight_label = tk.Label(results_window, text=f"{stock}: {weight * 100:.2f}%", font=("Calibri", 12))
        weight_label.grid(row=idx + 2, column=0, sticky='w', padx=10)

    # Display the recommended investments
    investments_label = tk.Label(results_window, text="Recommended Investments:", font=("Calibri", 14, "bold"))
    investments_label.grid(row=1, column=1, sticky='w', padx=10, pady=10)

    for idx, (stock, amount) in enumerate(investments.items()):
        investment_label = tk.Label(results_window, text=f"{stock}: ${amount:.2f}", font=("Calibri", 12))
        investment_label.grid(row=idx + 2, column=1, sticky='w', padx=10)

    # Display additional portfolio stats
    portfolio_stats_label = tk.Label(results_window, text="Portfolio Stats:", font=("Calibri", 14, "bold"))
    portfolio_stats_label.grid(row=1, column=2, sticky='w', padx=10, pady=10)

    stats_left = [('Return', portfolio_return), ('Risk', portfolio_risk)]
    for idx, (name, value) in enumerate(stats_left):
        stat_label = tk.Label(results_window, text=f"{name}: {value * 100:.2f}%", font=("Calibri", 12))
        stat_label.grid(row=idx + 2, column=2, sticky='w', padx=10)

    stats_right = [('Sharpe Ratio', sharpe_ratio), ('Beta', beta)]
    for idx, (name, value) in enumerate(stats_right):
        stat_label = tk.Label(results_window, text=f"{name}: {value:.2f}", font=("Calibri", 12))
        stat_label.grid(row=idx + 2, column=3, sticky='w', padx=10)

    # Add a Close button
    close_button = tk.Button(results_window, text="Close", font=("Calibri", 12), bg="blue", fg="white", width=10,
                             command=results_window.destroy)
    close_button.grid(row=idx + 15, column=0, pady=10, sticky="nsew")

# Function that opens a select preferences window, where the user can chose from the three strategies
def open_preferences_window(parent):

    global transactions
    preferences_window = tk.Toplevel(parent)
    preferences_window.title("Select Preferences")
    preferences_window.geometry("500x300")

    tk.Label(preferences_window, text="Preferred Portfolio Function:").pack()

    label_preferences = tk.Label(preferences_window, text="Please choose the portfolio allocation strategy that best suits your preferences:",
                            font=("Calibri", 11, "italic"), fg="gray")
    label_preferences.pack(pady=20)

    preferred_function_combobox = ttk.Combobox(preferences_window, values=["Equal-weighted portfolio (EWP)", "Return-weighted portfolio (RWP)", "Minimum Diversification Portfolio (MDP)"])
    preferred_function_combobox.pack(pady=10, expand=True, fill='x')

    # Function that sends the selected strategy to the show_new_weights_and_investments so it computes the necessary statistics
    def apply_selected_function():
        selected_function = preferred_function_combobox.get()
        if selected_function == 'Equal-weighted portfolio (EWP)':
            show_new_weights_and_investments(parent, EWP)

        elif selected_function == 'Return-weighted portfolio (RWP)':
            show_new_weights_and_investments(parent, RWP)

        elif selected_function == 'Minimum Diversification Portfolio (MDP)':
            show_new_weights_and_investments(parent, MDP)

        else:
            print("Invalid selection")

    # Create the button to select
    apply_button = tk.Button(preferences_window, text="Apply", bg="blue", fg="white", command=apply_selected_function)
    apply_button.pack(pady=10, expand=True, fill='x')

# Function that updates the stock prices each time they are selected 
def update_stock_prices(conn, c, stocks_list):
    for stock in stocks_list:
        stock_info = yf.Ticker(stock)
        todays_data = stock_info.history(period='1d')
        stock_price = todays_data['Close'][0]
        c.execute("REPLACE INTO stock_data (symbol, price) VALUES (?, ?)", (stock, stock_price))
        conn.commit()

# Function that retrieves the stock price from the database
def get_stock_price(c, stock):
    c.execute("SELECT price FROM stock_data WHERE symbol=?", (stock,))
    result = c.fetchone()
    return result[0] if result else None

# Main function 
def mainaccount():

    global balance
    # Initialize database
    conn, c = initialize_database()
    # Initialize new_stocks_list as an empty list
    stocks_list = []
    
    # Extract the S&P 500 list
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[0]
    ticker_list = df['Symbol'].tolist()

    # Update stock prices
    update_stock_prices(conn, c, stocks_list)

    # Create the main window
    window = tk.Tk()
    window.title("Uninvest - Welcome")
    window.geometry("800x800")

    sidebar = tk.Frame(window, bg="lightblue", width=200)
    sidebar.pack(fill="y", side="left")

    button_user_info = tk.Button(sidebar, text="User Information", font=("Calibri", 12),
                                 bg="blue", fg="white", width=15, command=lambda: display_user_info(window))

    button_user_info.pack(pady=10)

    content = tk.Frame(window, bg="#F0F0F0", width=600)  # Change the background color
    content.pack(fill="both", side="right", expand=True)

    label_welcome = tk.Label(content, text="Welcome to Uninvest", font=("Calibri", 18, "bold"), fg="blue")
    label_welcome.pack(pady=20)

    label_stocks = tk.Label(content, text="Please select a stock to invest in:",
                            font=("Calibri", 12, "italic"), fg="gray")
    label_stocks.pack(pady=20)

    # Function that checks if the selected stock figures already in the list or not
    def handle_selection(event):
        selected_value = combo_box.get()

        if selected_value not in stocks_list:
            stocks_list.append(selected_value)  

    # Define the list of options for the combo box
    options = ticker_list

    # Create the frame to hold the stock buttons
    frame_stocks = tk.Frame(content, bg="#F0F0F0")
    frame_stocks.pack(pady=10)

    # Create the combo box
    combo_box = ttk.Combobox(content, values=options)
    combo_box.bind("<<ComboboxSelected>>", handle_selection)
    combo_box.pack()

    # Create a button to add the stock to the list
    button_add_stock = tk.Button(content, text="Add Stock", font=("Calibri", 12),
                                 bg="blue", fg="white", width=15,
                                 command=lambda: refresh_stock_buttons(window, frame_stocks, stocks_list, c))
    button_add_stock.pack(pady=20)

    # Refresh the display
    window.update()

    # Refresh the display of the buttons and the prices everytime we press the add stock button
    def refresh_stock_buttons(window, frame, stocks_list, c):

    # Remove existing buttons
        for button in frame.winfo_children():
            button.destroy()
    # Create new buttons
        initialize_database()
        update_stock_prices(conn, c, stocks_list)
        create_stock_buttons(window, frame, stocks_list, c)

    create_stock_buttons(window, frame_stocks, stocks_list, c)

    # Function that displays the balance in a new window
    def show_balance():
        balance_window = tk.Toplevel(window)
        balance_window.title("Account Balance")
        balance_window.geometry("300x200")

        label_balance_display = tk.Label(balance_window, text=f"Your account balance is:\n${balance:,.2f} USD",
                                         font=("Calibri", 18), fg="blue")
        label_balance_display.pack(pady=20)

        button_close = tk.Button(balance_window, text="Close", font=("Calibri", 12),
                                 bg="blue", fg="white", width=10, command=balance_window.destroy)
        button_close.pack(pady=10)

    # Create the Display Balance button
    button_display_balance = tk.Button(sidebar, text="Display Balance", font=("Calibri", 12),
                                       bg="blue", fg="white", width=15, command=show_balance)
    button_display_balance.pack(pady=10)

    label_invest = tk.Label(content, text="Add funds to your account", font=("Calibri", 12), fg="gray")
    label_invest.pack(pady=10)

    invest_text = tk.StringVar()
    entry_invest = tk.Entry(content, textvariable=invest_text, font=("Calibri", 12), width=20)
    entry_invest.pack()
 
    # Function that adds money to the balance
    def addtoaccount():
        global balance
        amount=float(entry_invest.get())
        balance+=amount
    button_invest = tk.Button(content, text="Add to Balance", font=("Calibri", 12),
                          bg="blue", fg="white", width=15, command=addtoaccount)
    button_invest.pack(pady=10)

    window.mainloop()


 
