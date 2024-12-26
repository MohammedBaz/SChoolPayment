import streamlit as st
import pandas as pd  # For data handling

# --- Data Storage (In-memory for simulation) ---
student_data = {
    "12345": {"name": "John Doe", "card_balance": 100.00},
    "67890": {"name": "Jane Smith", "card_balance": 50.00},
    # ... more student data
}
transaction_history = []  # List to store transaction dictionaries

# --- Helper Functions ---
def deposit_funds(student_id, amount, payment_method):
    """Processes deposits, updates balance, and logs transactions."""
    if student_id in student_data:
        student_data[student_id]["card_balance"] += amount
        transaction_history.append({
            "student_id": student_id,
            "timestamp": st.session_state.get("timestamp", pd.Timestamp.now()),  # Use session state or current time
            "amount": amount,
            "payment_method": payment_method
        })
        st.success(f"Deposit successful! New balance for {student_data[student_id]['name']} is ${student_data[student_id]['card_balance']:.2f}")
    else:
        st.error("Student not found.")

# --- Streamlit App ---
st.title("School NFC Payment System Simulation")

# --- NFC Card Simulation ---
st.header("NFC Card Reader")
nfc_input = st.text_input("Scan NFC Card (Enter Student ID):")

if nfc_input:
    student_id = nfc_input
    if student_id in student_data:
        st.write(f"Student Name: {student_data[student_id]['name']}")
        st.write(f"Current Balance: ${student_data[student_id]['card_balance']:.2f}")

        # --- Deposit Form ---
        st.subheader("Deposit Funds")
        amount = st.number_input("Enter deposit amount:", min_value=0.01, step=0.01)
        payment_method = st.radio("Payment Method:", ["Credit Card", "Debit Card"])
        if st.button("Deposit"):
            deposit_funds(student_id, amount, payment_method)
    else:
        st.error("Student not found.")

# --- Transaction History ---
st.header("Transaction History")
if transaction_history:
    st.dataframe(pd.DataFrame(transaction_history))
else:
    st.write("No transactions yet.")
