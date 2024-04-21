from flask import Flask, request, jsonify
import os
import base64
import requests
import anthropic

app = Flask(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# API keys
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CLAUDE_API_KEY = os.environ["ANTHROPIC_API_KEY"]

@app.route("/upload-image", methods=["POST"])
def process_image():
    data = request.json
    base64_image = data['image']  # Expecting base64 image data in JSON body

    # Process with OpenAI
    openai_response = get_openai_response(OPENAI_API_KEY, base64_image)
    print("OpenAI Response:", openai_response)

    # Process with Claude
    claude_response = get_claude_response(CLAUDE_API_KEY, base64_image)
    print("Claude Response:", claude_response)

    return jsonify({
        "openai_response": openai_response,
        "claude_response": claude_response
    })

def get_openai_response(api_key, base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Given you image of a question paper, Write all the text in the image precisely in markdown format."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 3000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    json_out = response.json()
    return json_out['choices'][0]['message']['content']

def get_claude_response(api_key, base64_image):
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        },
                    },
                    {
                        "type": "text",
                        "text": "Given you image of a question paper, Write all the text in the image precisely in markdown format."
                    }
                ],
            }
        ],
    )
    return message.content[0].text

def write_to_markdown(text, file_name="output.md"):
    with open(file_name, "w") as f:
        f.write(text)

if __name__ == "__main__":
    app.run(debug=True)