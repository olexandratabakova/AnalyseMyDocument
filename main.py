from openai import OpenAI

import fitz
import os
import base64

from config import API_KEY


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def pdf_to_img(pdf_path):
    pdf_document = fitz.open(pdf_path)
    image_list = []
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        pix = page.get_pixmap()
        image_list.append(pix)

        pix.save(f"img/page_{page_number + 1}.png")
    pdf_document.close()
    return image_list


def get_all_from_dir(folder_path):
    files = os.listdir(folder_path)

    file_paths = [os.path.join(folder_path, file).replace("\\", "/") for file in files]
    return sorted(file_paths, key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))


my_pdf_path = "MyDocument.pdf"
response_language = "Ukrainian"

pdf_to_img(my_pdf_path)

context = [
    {
        "type": "text",
        "text": f"Збери інформацію з бранку та подай у вигляді json. Тільки відповідь. Не використовуй спецсимволи. Мова відплвіді {response_language}",
    },
]

for path in get_all_from_dir("img"):
    context.append(
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"},
        }
    )

client = OpenAI(api_key=API_KEY)
response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": context
        }
    ],
    response_format={"type": "json_object" }
)

print(response.choices[0].message.content)