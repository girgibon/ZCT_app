from fastapi import FastAPI, HTTPException
from copykitt import generate_branding_snippet, generate_keywords
from pydantic import Field, BaseModel
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware
from boto3 import resource
from os import getenv
from datetime import datetime
from uuid import uuid4

app = FastAPI()
handler = Mangum(app)
MAX_INPUT_LENGTH = 32

dynamodb = resource("dynamodb",
				aws_access_key_id=getenv("AWS_ACCES_KEY_ID"),
				aws_secret_access_key=getenv("AWS_SECRET_ACCES_KEY"),
				region_name=getenv("REGION_NAME"))

table_name_snippet = "snippet"
table_name_keywords = "keywords"
table_snippet = dynamodb.Table(table_name_snippet)
table_keywords = dynamodb.Table(table_name_keywords)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/generate_snippet")
async def generate_snippet_api(prompt: str):
    validate_input_length(prompt)
    snippet = generate_branding_snippet(prompt)
    snippet_in_db = {"snippet": snippet}
    new_snippet = Snippet(**snippet_in_db).dict()
    table_snippet.put_item(Item=new_snippet)
    return {"snippet": snippet, "keywords": []}


@app.get("/generate_keywords")
async def generate_keywords_api(prompt: str):
    validate_input_length(prompt)
    keywords, keywords_string = generate_keywords(prompt)
    keywords_in_db = {"keywords": keywords_string}
    new_keywords = Keywords(**keywords_in_db).dict()
    table_keywords.put_item(Item=new_keywords)
    return {"snippet": None, "keywords": keywords}


@app.get("/generate_snippet_and_keywords")
async def generate_keywords_api(prompt: str):
    validate_input_length(prompt)
    snippet = generate_branding_snippet(prompt)
    keywords, keywords_string = generate_keywords(prompt)
    snippet_in_db = {"snippet": snippet}
    new_snippet = Snippet(**snippet_in_db).dict()
    table_snippet.put_item(Item=new_snippet)
    keywords_in_db = {"keywords": keywords_string}
    new_keywords = Keywords(**keywords_in_db).dict()
    table_keywords.put_item(Item=new_keywords)
    return {"snippet": snippet, "keywords": keywords}


def validate_input_length(prompt: str):
    if len(prompt) >= MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Input length is too long. Must be under {MAX_INPUT_LENGTH} characters.",
        )
    

def generate_date():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    return str(dt_string)

def generate_id():
    return str(uuid4())

class Snippet(BaseModel):
    id_snippet: str = Field(default_factory=generate_id)
    snippet: str

class Keywords(BaseModel):
    id_keyword: str = Field(default_factory=generate_id)
    keywords: str