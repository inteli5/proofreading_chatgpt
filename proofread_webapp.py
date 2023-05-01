import os
from dotenv import load_dotenv, find_dotenv
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.responses import HTMLResponse

import openai
from myredlines import MyRedlines

# load the openai api key from .env file
_ = load_dotenv(find_dotenv())


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


class OriginalText(BaseModel):
    text: str


class CorrectedText(BaseModel):
    corrected_text: str
    diff: str


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("proofread_home.html", {"request": request})


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
    prompt = f"""Proofread and correct the following text
    and rewrite the corrected version. Only output the corrected version. Do not add any other words.
    ```{original_text}```"""
    response = get_completion(prompt)

    diff = MyRedlines(original_text, response)

    response_dict = {"corrected_text": response, "diff": diff.output_markdown}
    return CorrectedText(**response_dict)


if __name__ == "__main__":
    uvicorn.run("proofread_webapp:app", host="0.0.0.0", port=8000, reload=True)
