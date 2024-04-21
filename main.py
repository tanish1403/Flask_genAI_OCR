from openai import OpenAI
import base64
from dotenv import load_dotenv
import os
import requests
import anthropic
from flask import Flask, request


app = Flask(__name__)


load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CLAUDE_API_KEY = os.environ["ANTHROPIC_API_KEY"]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
       return base64.b64encode(image_file.read()).decode('utf-8')

# @app.get("/gpt")
@app.route("/upload-image", methods=["POST"])
def get_openai_responce( OPENAI_API_KEY, image_path="sample.jpeg"):
    image = request.files["image"]
    image_path = image.filename
    base64_image = encode_image(image_path)
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
  }

    payload = {
      "model": "gpt-4-turbo",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Given you image of a question paper, Write all the text in the image precisely in markdown format. "
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

# @app.get('/claude/<str:image_path>')
@app.route("/upload-image", methods=["POST"])
def get_claude_response( CLAUDE_API_KEY, image_path="sample.jpeg"):
    image = request.files["image"]
    image_path = image.filename
    client = anthropic.Anthropic(api_key = CLAUDE_API_KEY)
    image1_media_type = "image/jpeg"
    image1_data = encode_image(image_path)
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
                            "data": image1_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Given you image of a question paper, Write all the text in the image precisely in markdown format. "
                    }
                ],
            }
        ],
    )
    return message.content[0].text

def write_to_markdown(text, file_name="output.md"):
    with open(file_name, "w") as f:
        f.write(text)

# @app.get("/save_both/<str:image_path>")
def main():
    image_path = "sample.jpeg"
    openai_responce = get_openai_responce( OPENAI_API_KEY, image_path=image_path)
    print(openai_responce)
    write_to_markdown(openai_responce, "openai_output.md")
    print("GPT done")
    claude_response = get_claude_response(CLAUDE_API_KEY, image_path=image_path)  
    print(claude_response)
    write_to_markdown(claude_response, "claude_output.md")
    print("Claude done")

if __name__ == "__main__":
    app.run(debug=True)