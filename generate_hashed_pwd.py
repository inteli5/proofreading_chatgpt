from passlib.context import CryptContext

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

# write your password here.
plain_password = "a"

# Hash the password
hashed_password = get_password_hash(plain_password)

print(hashed_password)