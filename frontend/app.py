import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title='App - Register / Login',layout = 'centered')

def fetch_user():
    if st.session_state.access_token:
        try:
            r = requests.get(f"{BACKEND_URL}/users/me",headers={"Authorization":f"Bearer {st.session_state.access_token}"})
            if r.status_code == 200:
                st.session_state.user = r.json()
                return True
            else:
                st.session_state.access_token = None
        except Exception as e:
            st.session_state.access_token = None
    else:
        st.session_state.access_token = None

if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    tab1,tab2 = st.tabs(['Login','Regsiter'])
    with tab1:
        st.subheader('Login')
        with st.form('login_form'):
            email = st.text_input('Email',key='login_email')
            password = st.text_input('Password',type='password',key='login_pwd')
            submit_login = st.form_submit_button('Login')
        if submit_login:
            try:
                r = requests.post(
                    f"{BACKEND_URL}/login",
                    data = {'username':email,'password':password}
                )
                if r.status_code == 200:
                    token_data = r.json()
                    st.session_state.access_token = token_data['access_token']
                    fetch_user()

            except Exception as e:
                st.error(f'Connection Error {e}')
    with tab2:
        st.subheader('Register')
        with st.form('register_form'):
            reg_email = st.text_input('Email',key='reg_email')
            reg_pw = st.text_input('Password',type='password',key='reg_pw')
            reg_pw_confirm = st.text_input('Confirm Password',type='password')
            submit_reg = st.form_submit_button('Create Account')
        
        if submit_reg:
             if reg_pw != reg_pw_confirm:
                 st.error('Passwords do not match')
             elif len(reg_pw) < 8:
                st.error("Password must be at least 8 characters")
             else:
                try:
                    r = requests.post(
                        f"{BACKEND_URL}/register",
                        json={"email": reg_email, "password": reg_pw}
                    )
                    if r.status_code == 200:
                        st.success("Account created! You can now login.")
                    elif r.status_code == 400:
                        st.error(r.json().get("detail", "Registration failed"))
                    else:
                        st.error("Server error")
                except Exception as e:
                    st.error(f"Connection error: {e}")
                
else:
    user = st.session_state.user
    print('------------------------------',user)
    st.sidebar.title(f"Welcome, {user.get('name', user['email'])}")
    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.session_state.user = None
        st.rerun()

    st.title("Claims Interview Assesment")
    st.success(f"You are logged in as {user['email']}")
    st.write(f"Role: **{user['role']}**")