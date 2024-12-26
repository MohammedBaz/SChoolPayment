import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Data Storage (In-memory for simulation) ---
student_data = {
    "12345": {"name": "John Doe", "card_balance": 100.00},
    "67890": {"name": "Jane Smith", "card_balance": 50.00},
    # ... more student data
}
transaction_history = []  # List to store transaction dictionaries

# --- Helper Functions ---


def deposit_funds(student_id, amount, payment_method, transaction_id):
    """Processes deposits, updates balance, and logs transactions."""
    if student_id in student_data:
        student_data[student_id]["card_balance"] += amount
        transaction_history.append({
            "student_id": student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "payment_method": payment_method,
            "transaction_id": transaction_id
        })
        st.success(
            f"Deposit successful! New balance for {student_data[student_id]['name']} is ${student_data[student_id]['card_balance']:.2f}"
        )
    else:
        st.error("Student not found.")


# --- PayTabs Configuration ---
profile_id = "116284"  # Replace with your actual Profile ID
server_key = "SGJNKHLWZ2-JKJTRKW6NJ-2TR2KRD29K"  # Replace with your actual Server Key
paytabs_api_url = "https://www.paytabs.com/apiv2/create_pay_page"

# --- Streamlit App ---
st.title("School NFC Payment System Simulation")

# --- NFC Card Simulation ---
st.header("NFC Card Reader")
nfc_input = st.text_input("Scan NFC Card (Enter Student ID):")

if nfc_input:
    student_id = nfc_input
    if student_id in student_data:
        st.write(f"Student Name: {student_data[student_id]['name']}")
        st.write(
            f"Current Balance: ${student_data[student_id]['card_balance']:.2f}"
        )

        # --- Deposit Form ---
        st.subheader("Deposit Funds")
        amount = st.number_input("Enter deposit amount:",
                                 min_value=0.01,
                                 step=0.01)

        if st.button("Deposit"):
            try:
                # Construct PayTabs payment request
                headers = {"Authorization": server_key}
                data = {
                    "profile_id": profile_id,
                    "customer_email":
                    f"{student_id}@example.com",  # Replace with actual email or generate dynamically
                    "customer_phone":
                    "1234567890",  # Replace with actual phone number
                    "amount": amount,
                    "currency": "SAR",
                    "title": "School Fees",  # Or any suitable title
                    "reference_no":
                    f"school-payment-{student_id}-{datetime.now().timestamp()}",  # Generate a unique reference
                    "site_url":
                    "YOUR_SITE_URL",  # Replace with your website or app URL
                    "return_url":
                    "YOUR_RETURN_URL",  # Replace with a URL to handle successful payments
                    "msg_lang": "en",  # Language of the payment page
                    # ... add other required parameters (see PayTabs documentation) ...
                }

                response = requests.post(paytabs_api_url,
                                         headers=headers,
                                         data=data)
                response.raise_for_status()

                result = response.json()
                if result.get("response_code") == "4012":
                    payment_url = result.get("payment_url")
                    transaction_id = result.get(
                        "tran_ref")  # Get the transaction ID
                    st.write(f"Redirecting to PayTabs: {payment_url}")

                    # --- Simulate successful payment (remove this in production) ---
                    # In a real app, you would redirect the user to payment_url
                    # and use webhooks to handle payment confirmation
                    deposit_funds(student_id, amount, "PayTabs",
                                  transaction_id)

                else:
                    st.error(f"PayTabs error: {result.get('result')}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error processing payment: {e}")
    else:
        st.error("Student not found.")

# --- Transaction History ---
st.header("Transaction History")
if transaction_history:
    st.dataframe(pd.DataFrame(transaction_history))
else:
    st.write("No transactions yet.")
