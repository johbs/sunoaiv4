from fastapi import Depends, FastAPI, HTTPException, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid

import schemas
from deps import get_token
from utils import (
    generate_lyrics,
    generate_music,
    get_feed,
    get_lyrics,
    concat_music,
    get_feeds,
)
from task_store import save_task, get_task


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def get_root():
    return schemas.Response()


async def process_generation(data: dict, token: str):
    try:
        result = await generate_music(data, token)
        save_task(data["task_id"], "completed", result)
    except Exception as e:
        save_task(data["task_id"], "failed", {"error": str(e)})


@app.post("/generate")
async def generate(
    data: schemas.CustomModeGenerateParam, 
    background_tasks: BackgroundTasks,
    token: str = Depends(get_token)
):
    task_id = str(uuid.uuid4())
    data_dict = data.dict()
    data_dict["task_id"] = task_id
    
    # Save initial task status
    save_task(task_id, "pending")
    
    # Start processing in background
    background_tasks.add_task(process_generation, data_dict, token)
    
    return {"task_id": task_id, "status": "pending"}


@app.get("/status/{task_id}")
async def get_generation_status(task_id: str):
    task_data = get_task(task_id)
    if task_data is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_data


@app.post("/generate/description-mode")
async def generate_with_song_description(
    data: schemas.DescriptionModeGenerateParam, token: str = Depends(get_token)
):
    try:
        resp = await generate_music(data.dict(), token)
        return resp
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/feed/{aid}")
async def fetch_feed(aid: str, token: str = Depends(get_token)):
    try:
        resp = await get_feed(aid, token)
        return resp
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/feeds/{aid}")
async def fetch_feeds(aid: str, token: str = Depends(get_token)):
    try:
        resp = await get_feeds(aid, token)
        return resp
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.post("/generate/lyrics/")
async def generate_lyrics_post(
    data: schemas.GenerateLyricsParam, token: str = Depends(get_token)
):
    try:
        resp = await generate_lyrics(data.prompt, token)
        return resp
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/lyrics/{lid}")
async def fetch_lyrics(lid: str, token: str = Depends(get_token)):
    try:
        resp = await get_lyrics(lid, token)
        return resp
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.post("/generate/concat")
async def concat(data: schemas.ConcatParam, token: str = Depends(get_token)):
    try:
        resp = await concat_music(data.dict(), token)
        return resp
    except Exception as e:
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
