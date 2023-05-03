import json
import os
from datetime import timedelta, datetime
from dotenv import load_dotenv, find_dotenv

from fastapi import FastAPI, Depends, Form
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from retry import retry
import openai
from openai.error import APIConnectionError

from model import OriginalText, CorrectedText, User, TokenData
from myredlines import MyRedlines

# load the openai api key from .env file
_ = load_dotenv(find_dotenv())

# load the users database from data.db, which stores the usernames and hashed passwords.

with open('data.db') as f:
    users_db = json.load(f)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PROOFREAD_SECRET_KEY = os.environ.get("PROOFREAD_SECRET_KEY") or "mysecretkey314zaw"
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    """
    Verify the password.

    Args:
        plain_password (str): The password to be verified.
        hashed_password (str): The hashed password.

    Returns:
        bool: Whether the password is verified.
    """
    
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Create an access token using the secret key.

    Args:
        data (dict): The data to be encoded.

    Returns:
        str: The access token.
    """
    to_encode = data.copy()
    token = jwt.encode(to_encode, PROOFREAD_SECRET_KEY, algorithm=ALGORITHM)
    return token


def authenticate_user(username: str, password: str):
    """
    Authenticate the user.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        user (dict): The user.
    """

    user = users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

async def get_current_user(request: Request):
    """
    Get the current user by decoding the token from cookies. If the token is invalid, the user is not authenticated.

    Args: 
        request (Request): The request.

    Returns:
        user (dict | str ): The user or the str "unauthorized" if the user is not authenticated.
    """

    token = request.cookies.get("access_token")
    if token is None:
        return 'unauthorized'
    try:
        payload = jwt.decode(token, PROOFREAD_SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("username")
        if username is None:
            return 'unauthorized'

        token_data = TokenData(username=username)
    except JWTError:
        return 'unauthorized'

    user = users_db.get(token_data.username)
    if user is None:
        return 'unauthorized'
    return user

@retry(APIConnectionError, tries=3, delay=2, backoff=2)
def get_completion(prompt, model="gpt-3.5-turbo"):
    """
    Get the completion from OpenAI's ChatGPT model.

    Args:
        prompt (str): The prompt to be completed.
        model (str): The model to be used.

    Returns:
        str: The completion.
    """

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


# Create FastAPI app and Jinja2 templates
app = FastAPI(title="Proofread from ChatGPT")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: User | str = Depends(get_current_user, use_cache=True)):
    if isinstance(current_user, dict) and current_user['username'] in users_db:
        return templates.TemplateResponse("proofread_home.html", {"request": request})
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)



@app.post("/proofread")
async def proof(original_text: OriginalText) -> CorrectedText:
    """
    Proofread the text using ChatGPT and return the corrected text and the difference.
    
    Args:
        original_text (OriginalText): The original text to be proofread.
        
    Returns:
        CorrectedText: The corrected text and the difference.
    """

    openai.api_key = os.getenv("OPENAI_API_KEY")
    original_text = original_text.text
    prompt = f"""Proofread and correct the following text that delimited in the triple backticks
    and rewrite the corrected version. Only output the corrected version. Do not add any other words. 
    Keep the number of paragraphs the same as the original text.
    ```{original_text}```"""
    response = get_completion(prompt)

    diff = MyRedlines(original_text, response)

    response_dict = {"corrected_text": response, "diff": diff.output_markdown}
    return CorrectedText(**response_dict)





@app.get("/login", response_class=HTMLResponse)
async def login(request: Request, current_user: User | str = Depends(get_current_user)):
    if isinstance(current_user, dict) and current_user['username'] in users_db:
        return templates.TemplateResponse("protected.html", {"request": request, "username": current_user['username']})
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_for_access_token(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    access_token_expires = timedelta(days=30)
    access_token = create_access_token(
        data={"username": user["username"], "exp": datetime.utcnow() + access_token_expires}
    )
    response = templates.TemplateResponse("protected.html", {"request": request, "username": user["username"]})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("access_token")
    return response


@app.get("/unauthorized", response_class=HTMLResponse)
async def unauthorized(request: Request):
    return templates.TemplateResponse("unauthorized.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("proofread_webapp:app", host="0.0.0.0", port=8000, reload=True)

