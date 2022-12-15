from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI()
now = datetime.now()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    date: Optional[datetime] = now
    rating: Optional[int] = None


@app.get('/')
async def root():
    return {"statusUp": True}

@app.post('/posts')
async def create_post(post:Post = Body(...)):
    print(post.dict())
    return post

