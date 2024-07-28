from fastapi import FastAPI, Request
from chain import chain
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

#origins = [" *.daoyidh.com"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


@app.post("/generator")
async def AISemantic(request: Request):

    inputData = await request.json()
    question = inputData.get('question')

    res = chain(question)

    answer_text = res.get("answer", "")
    start_index = answer_text.find("資料來源:")

    if start_index != -1:
        # 提取“資料來源”之前的内容
        retained_text = answer_text[:start_index].strip()
        # 提取“資料來源”后的内容
        source_text = answer_text[start_index + len("資料來源:"):]
        source_text = source_text.replace('"', '')
        parts = re.split(r'\s*(?=\d\.\s)', source_text.strip())

        # 去掉列表中的空字符串
        parts = [part for part in parts if part]
    else:
        retained_text = answer_text
        parts = ""

    res["answer"] = retained_text
    res["source"] = parts
    return res


if __name__ == "__main__":
    uvicorn.run('main:app', host=HOST, port=int(PORT))
