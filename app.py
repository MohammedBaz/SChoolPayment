import streamlit as st
import sqlite3
import requests
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect("school_meal_system.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        balance REAL NOT NULL DEFAULT 0.0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        type TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(student_id) REFERENCES students(id))''')
    conn.commit()
    conn.close()

# Add student to database
def add_student(name):
    conn = sqlite3.connect("school_meal_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# Get student details
def get_student(name_or_id):
    conn = sqlite3.connect("school_meal_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE name = ? OR id = ?", (name_or_id, name_or_id))
    student = cursor.fetchone()
    conn.close()
    return student

# Update student balance
def update_balance(student_id, amount, transaction_type):
    conn = sqlite3.connect("school_meal_system.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET balance = balance + ? WHERE id = ?", (amount, student_id))
    cursor.execute("INSERT INTO transactions (student_id, amount, type) VALUES (?, ?, ?)", (student_id, amount, transaction_type))
    conn.commit()
    conn.close()

# Get transaction history
def get_transactions(student_id):
    conn = sqlite3.connect("school_meal_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE student_id = ? ORDER BY timestamp DESC", (student_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Initialize database
init_db()

# Streamlit UI
st.title("School Meal Payment System")

menu = ["Parent Portal", "Admin Portal"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Parent Portal":
    st.header("Parent Portal - Recharge Card")
    student_input = st.text_input("Enter Student Name or ID")
    amount = st.number_input("Recharge Amount", min_value=1.0, step=0.1)

    if st.button("Recharge"):
        student = get_student(student_input)
        if student:
            student_id, student_name, balance = student

            # Mocking PayTabs payment request
            payload = {
                "profile_id": 116284,
                "tran_type": "sale",
                "tran_class": "ecom",
                "cart_id": f"recharge_{student_id}",
                "cart_description": "Card Recharge",
                "cart_currency": "SAR",
                "cart_amount": amount,
                "return": "https://your-website.com/return",
                "callback": "https://your-website.com/callback"
            }
            response = requests.post("https://secure.paytabs.sa/payment/request", json=payload)
            data = response.json()

            if "redirect_url" in data:
                st.success(f"Redirect to payment: {data['redirect_url']}")
                update_balance(student_id, amount, "deposit")
                st.success(f"Successfully recharged {amount} SAR for {student_name}. New balance: {balance + amount:.2f} SAR")
            else:
                st.error("Payment failed. Please try again.")
        else:
            st.error("Student not found. Please check the name or ID.")

elif choice == "Admin Portal":
    st.header("Admin Portal")
    sub_menu = ["Add Student", "View Students", "View Transactions"]
    admin_choice = st.sidebar.radio("Admin Options", sub_menu)

    if admin_choice == "Add Student":
        st.subheader("Add a New Student")
        student_name = st.text_input("Enter Student Name")
        if st.button("Add Student"):
            add_student(student_name)
            st.success(f"Student {student_name} added successfully.")

    elif admin_choice == "View Students":
        st.subheader("List of Students")
        conn = sqlite3.connect("school_meal_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        conn.close()

        for student in students:
            st.write(f"ID: {student[0]}, Name: {student[1]}, Balance: {student[2]:.2f} SAR")

    elif admin_choice == "View Transactions":
        st.subheader("Transaction History")
        student_input = st.text_input("Enter Student Name or ID")
        if st.button("View Transactions"):
            student = get_student(student_input)
            if student:
                transactions = get_transactions(student[0])
                for txn in transactions:
                    st.write(f"{txn[4]} - {'Deposit' if txn[3] == 'deposit' else 'Purchase'}: {txn[2]:.2f} SAR")
            else:
                st.error("Student not found. Please check the name or ID.")
