# Proofreading Web App with OpenAI ChatGPT API.

A proofreading web app that utilizes the OpenAI ChatGPT API.

## Installation

```bash
git https://github.com/inteli5/proofreading_chatgpt.git
```
create a virtual environment by, for example, 

```bash
conda create -n proofread python=3.10

```

```bash
conda activate proofread
```


Install required packages.
```bash
python -m pip install -r requirements.txt
```

Add your OPENAI_API_KEY. 
You can get a OPENAI_API_KEY by google 'openai api key' and get one from OpenAI's official website. In the root directory of the project, create a file named `.env` with the following contents. 
```bash
OPENAI_API_KEY=your_openai_api_key
```

## Usage


### Web App

In the root directory of the project, run the following command in the terminal:
```bash
python proofread_webapp.py
```
After that, open a web browser and enter the URL 127.0.0.1:8000.

We employed a simple authurization system to limit you openai account's expense if you expose the webapp to the public.
You can add user and password in the file data.db.

```json
{
    "testuser": {
        "username": "testuser",
        "password": "$2b$12$7/bfr2VvYrLxBXcBv7Me4eocdtTvHITtISi3qUTP44TxxNljEYR/a" 
    }
}
```

The default username and password are `testuser` and `testpassword`. The password in the JSON file is a hashed password.

The code will only compare the hashed password. To create a hashed password for your plain password, run `generate_hashed_pwd.py` and input your new plain password in the terminal.

 After that you can modify the data.db as 

 ```json
{
    "your_user": {
        "username": "your_user",
        "password": "your new hashed password" 
    }
}
```

Make sure you change both the key and the 'username' field to your new username and delete the entry for the 'testuser'.


### Screenshot

![screenshot](./Screenshot.png)


## License

[MIT](https://choosealicense.com/licenses/mit/)