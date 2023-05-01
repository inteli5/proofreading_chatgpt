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

### Screenshot

![screenshot](./Screenshot.png)


## License

[MIT](https://choosealicense.com/licenses/mit/)