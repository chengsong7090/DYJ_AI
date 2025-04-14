import streamlit as st

st.title("Test Streamlit")
st.write("If you can see this, Streamlit is working correctly!")

# Add a simple input
user_input = st.text_input("Enter something:")
if user_input:
    st.write(f"You entered: {user_input}") 