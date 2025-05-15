# Conversational Bridge Backend

This is the backend service for the Conversational Bridge AI application.

## Setup

1. Make sure you have Python 3.8+ installed
2. Create and activate the virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

## Running the Server

To start the server, run:
```bash
python main.py
```

The server will start on `http://localhost:8000`.

## API Endpoints

### POST /chat
Accepts a list of messages and returns a response.

Request body:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    }
  ]
}
```

Response:
```json
{
  "role": "assistant",
  "content": "Echo: Hello!"
}
``` 