from flask import Flask, request, jsonify
import os
import base64
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def decode_base64_image(base64_string):
    """Decode base64 image data to bytes."""
    return base64.b64decode(base64_string)

@app.route("/upload-image", methods=["POST"])
def process_image():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.json
    base64_image = data.get('image')
    if not base64_image:
        return jsonify({"error": "No image provided in the request"}), 400
    image_bytes = decode_base64_image(base64_image)

    # Process the image with both APIs and get responses
    openai_response = get_openai_response(OPENAI_API_KEY, image_bytes)
    # claude_response = get_claude_response(CLAUDE_API_KEY, image_bytes)

    # Save responses to markdown files
    # write_to_markdown(openai_response, "openai_output.md")
    # write_to_markdown(claude_response, "claude_output.md")

    # Return responses as JSON
    return openai_response

def get_openai_response(api_key, image_bytes):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "model": "gpt-4-turbo",
        "messages": [{
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
        }],
        "max_tokens": 3000
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    json_out = response.json()
    return json_out['choices'][0]['message']['content']

def get_claude_response(api_key, image_bytes):
    client = anthropic.Anthropic(api_key=api_key)
    image1_media_type = "image/jpeg"
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
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
                            "media_type": image1_media_type,
                            "data": base64_image,
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
    return message

def write_to_markdown(text, file_name):
    with open(file_name, "w") as f:
        f.write(text)

if __name__ == "__main__":
    app.run(debug=True)
