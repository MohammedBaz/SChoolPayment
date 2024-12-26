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
profile_id = st.secrets["profile_id"]  # Replace with your actual Profile ID
server_key = st.secrets["server_key"]  # Replace with your actual Server Key
paytabs_api_url = "https://secure.paytabs.sa/payment/request"

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
                    "tran_type": "sale",
                    "tran_class": "ecom",
                    "cart_id":
                    f"cart_{student_id}_{datetime.now().timestamp()}",
                    "cart_description": "School Fees",
                    "cart_currency": "SAR",
                    "cart_amount": amount,
                    "customer_details": {
                        "name": student_data[student_id]['name'],
                        "email": f"{student_id}@example.com",
                        "phone": "1234567890",  # Replace with student's phone
                        "street1":
                        "Street Address 1",  # Replace with student's address
                        "city": "City Name",  # Replace with student's city
                        "state":
                        "State Name",  # Replace with student's state
                        "country": "SA",
                        "zip": "12345"  # Replace with student's zip code
                    },
                    "shipping_details": {
                        # ... (same as customer_details or omit if not needed)
                    },
                    "return":
                    "YOUR_RETURN_URL",  # Replace with your actual return URL
                    "callback":
                    "YOUR_CALLBACK_URL"  # Replace with your actual callback URL
                }

                # --- Debugging: Print request headers and data ---
                st.write("Request Headers:", headers)
                st.write("Request Data:", data)

                response = requests.post(paytabs_api_url,
                                         headers=headers,
                                         json=data)

                # --- Debugging: Print response status code and content ---
                st.write("Response Status Code:", response.status_code)
                st.write("Response Content:", response.text)

                response.raise_for_status()  # Raise an exception for bad status codes

                result = response.json()

                if "redirect_url" in result:
                    payment_url = result["redirect_url"]
                    st.write(f"Redirecting to PayTabs: {payment_url}")

                    # --- Redirect the user ---
                    st.markdown(
                        f'<meta http-equiv="refresh" content="0;URL={payment_url}">',
                        unsafe_allow_html=True)

                    # --- (In production, handle the callback to confirm payment) ---

                else:
                    st.error(f"PayTabs error: {result.get('message')}")
                    st.write(f"Full PayTabs response: {result}")

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
