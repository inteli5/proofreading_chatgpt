from passlib.context import CryptContext
import json

with open('data.db') as f:
    users_db = json.load(f)

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

# write your password here.
username = input("Enter your username: ")
plain_password = input("Enter your plain password: ")

# Hash the password
hashed_password = get_password_hash(plain_password)

print(f"Your hashed password is: {hashed_password}")

if 'testuser' in users_db:
    del users_db['testuser']
users_db[username] = { "username": username, "password": hashed_password }

with open('data.db', 'w') as f:
    json.dump(users_db, f, indent=4, sort_keys=True)

print(f"The username {username} and the hashed password have been added to the data.db file. testuser has been deleted. Make sure to restart uvicorn after you updated the data.db.")


