# test_security.py
password = "admin123"  # Hardcoded password

def login(username, pwd):
    query = f"SELECT * FROM users WHERE name='{username}' AND pwd='{pwd}'"
    return execute(query)