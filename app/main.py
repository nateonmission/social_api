from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.params import Body
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from . import schemas
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
now = datetime.now()



class Post(BaseModel):
    id: Optional[int]
    title: str
    content: str
    is_published: bool = True
    created_at: Optional[datetime] = now

try_connect = True

while try_connect:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='fapi_tutorial',
            user='postgres',
            password='postgres',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print('Successfully connected to Database')
        try_connect = False
    except Exception as error:
        print(f"Failed to connect to Database: {error}")
        print("Will try again in 5 seconds.")
        time.sleep(5)

@app.get('/')
async def root(db: Session = Depends(get_db)):
    return {"statusUp": True}


# POST objects
@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post:Post = Body(...), db: Session = Depends(get_db)):
    print('Create Post')
    new_post = models.Post( **post.dict() )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get('/posts', response_model=List[schemas.Post])
def get_posts( db: Session = Depends(get_db)):
    print('Get all Posts')
    all_posts = db.query(models.Post).all()
    return all_posts

@app.get('/posts/{id}')
def get_post_by_id(id: int,  db: Session = Depends(get_db), response_model=schemas.Post):
    this_post = db.query(models.Post).filter(models.Post.id == id).first()
    if not this_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with ID = {id} was not found')
    return this_post


@app.patch('/posts/{id}')
def patch_post(id: int, patch = Body(...),  db: Session = Depends(get_db), response_model=schemas.Post):
    print('Update Post')
    this_post = db.query(models.Post).filter(models.Post.id == id)
    if this_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with ID = {id} was not found')
    
    this_post.update(patch, synchronize_session=False)
    db.commit()
    return this_post.first()

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,  db: Session = Depends(get_db)):
    print('Delete Post')
    this_post = db.query(models.Post).filter(models.Post.id == id)
    if this_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with ID = {id} was not found')
    
    this_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

