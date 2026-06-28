import requests
import time
import subprocess
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("Testing connection to Python Sensei API...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / response status: {response.status_code}")
        print(f"GET / response data: {response.json()}")
    except Exception as e:
        print(f"Failed to connect to API: {e}")
        return False

    # 1. Test Signup
    email = f"test_{int(time.time())}@example.com"
    signup_data = {
        "email": email,
        "password": "Password123!",
        "full_name": "Test Candidate"
    }
    
    print("\nTesting POST /signup ...")
    signup_res = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"Status: {signup_res.status_code}")
    signup_json = signup_res.json()
    print(f"Data: {signup_json}")
    
    if signup_res.status_code != 200 or not signup_json.get("success"):
        print("Signup failed")
        return False
        
    token = signup_json["data"]["access_token"]
    print("Signup successful! JWT Token acquired.")
    
    # 2. Test Login
    login_data = {
        "email": email,
        "password": "Password123!"
    }
    print("\nTesting POST /login ...")
    login_res = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {login_res.status_code}")
    login_json = login_res.json()
    print(f"Data: {login_json}")
    
    if login_res.status_code != 200 or not login_json.get("success"):
        print("Login failed")
        return False
    print("Login successful! User name returned: " + login_json["data"]["user"]["full_name"])

    # 3. Test Profile GET
    headers = {"Authorization": f"Bearer {token}"}
    print("\nTesting GET /profile ...")
    profile_res = requests.get(f"{BASE_URL}/profile", headers=headers)
    print(f"Status: {profile_res.status_code}")
    profile_json = profile_res.json()
    print(f"Data: {profile_json}")
    
    if profile_res.status_code != 200 or not profile_json.get("success"):
        print("Profile fetch failed")
        return False

    # 4. Test Profile PUT
    print("\nTesting PUT /profile ...")
    update_data = {
        "full_name": "Test Candidate Updated",
        "phone_number": "+1 555-987-6543"
    }
    update_res = requests.put(f"{BASE_URL}/profile", json=update_data, headers=headers)
    print(f"Status: {update_res.status_code}")
    update_json = update_res.json()
    print(f"Data: {update_json}")
    
    if update_res.status_code != 200 or update_json["data"]["user"]["full_name"] != "Test Candidate Updated":
        print("Profile update failed")
        return False
    print("Profile update successful!")

    # 5. Test Forgot Password
    print("\nTesting POST /forgot-password ...")
    forgot_res = requests.post(f"{BASE_URL}/forgot-password", json={"email": email})
    print(f"Status: {forgot_res.status_code}")
    forgot_json = forgot_res.json()
    print(f"Data: {forgot_json}")
    
    if forgot_res.status_code != 200 or not forgot_json.get("success"):
        print("Forgot password request failed")
        return False
        
    reset_link = forgot_json["data"]["reset_link"]
    reset_token = reset_link.split("token=")[1]
    print(f"Forgot password success! Reset link: {reset_link}")

    # 6. Test Reset Password
    print("\nTesting POST /reset-password ...")
    reset_data = {
        "token": reset_token,
        "new_password": "NewPassword123!"
    }
    reset_res = requests.post(f"{BASE_URL}/reset-password", json=reset_data)
    print(f"Status: {reset_res.status_code}")
    print(f"Data: {reset_res.json()}")
    
    if reset_res.status_code != 200 or not reset_res.json().get("success"):
        print("Reset password failed")
        return False
        
    # 7. Test Login with New Password
    print("\nTesting Login with New Password ...")
    new_login_data = {
        "email": email,
        "password": "NewPassword123!"
    }
    new_login_res = requests.post(f"{BASE_URL}/login", json=new_login_data)
    print(f"Status: {new_login_res.status_code}")
    if new_login_res.status_code != 200:
        print("Login with new password failed")
        return False
    print("Login with new password successful!")
    
    print("\nAll Backend API Verification Tests Passed successfully!")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
