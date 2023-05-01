import pytest
from fastapi.testclient import TestClient
from proofread_webapp import app, get_completion, OriginalText

client = TestClient(app)


@pytest.fixture
def mock_get_completion(mocker):
    # define a mock response
    mock_response = "This is the corrected text."

    # replace the get_completion function with a mock function
    mocker.patch("proofread_webapp.get_completion", return_value=mock_response)

    yield mock_response


def test_proofread(mock_get_completion):
    # send a POST request to /proofread with some text
    response = client.post("/proofread", json={"text": "This is the text."})
    # assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # assert that the response contains the mock response
    assert mock_get_completion in response.json()["corrected_text"]
    assert 'This is the <span style="color:red;font-weight:700;">corrected </span>text.' in response.json()['diff']


def test_proofread_wrong_request():
    # send a GET request to /proofread (wrong method)
    response = client.get("/proofread")
    
    # assert that the response status code is 405 (Method Not Allowed)
    assert response.status_code == 405

    # send a POST request to /proofread with wrong payload
    response = client.post("/proofread", json={"incorrect_field_name": "Some text to proofread."})
    
    # assert that the response status code is 422 (Unprocessable Entity)
    assert response.status_code == 422

def test_home():
    """
    Test the home page.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Text Proofreading" in response.text


 


