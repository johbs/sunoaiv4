import json
import os
import aiohttp
import asyncio
from loguru import logger

BASE_URL = os.getenv("BASE_URL")


COMMON_HEADERS = {
    # "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://suno.com/",
    "Origin": "https://suno.com",
}


async def fetch(url, headers=None, data=None, method="POST"):
    if headers is None:
        headers = {}
    headers.update(COMMON_HEADERS)
    if data is not None:
        data = json.dumps(data)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=method, url=url, data=data, headers=headers
            ) as resp:
                return await resp.json()
        except Exception as e:
            raise Exception(resp.text)


async def get_feed(ids, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/clip/{ids}"
    response = await fetch(api_url, headers, method="GET")
    return [response]


async def get_feeds(ids, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/feed/v2?ids={ids}"
    response = await fetch(api_url, headers, method="GET")
    clips = response.get("clips")
    if clips:
        return clips
    return response


async def generate_music(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/v2/"
    response = await fetch(api_url, headers, data)
    return response


async def concat_music(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/concat/v2/"
    response = await fetch(api_url, headers, data)
    return response


async def generate_lyrics(prompt, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/lyrics/"
    data = {"prompt": prompt, "lyrics_model": "default"}
    return await fetch(api_url, headers, data)


async def get_lyrics(lid, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/lyrics/{lid}"
    return await fetch(api_url, headers, method="GET")


async def wait_for_audio(clip_id: str, token: str, max_retries: int = 60, delay: float = 2.0):
    """
    Poll for audio URL until it's available.
    
    Args:
        clip_id: The ID of the clip to check
        token: Auth token
        max_retries: Maximum number of times to check (default: 60 tries = 2 minutes)
        delay: Delay between checks in seconds (default: 2 seconds)
    """
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/clip/{clip_id}"
    
    for _ in range(max_retries):
        response = await fetch(api_url, headers, method="GET")
        
        # Check if audio_url is available
        if response.get("audio_url"):
            return response["audio_url"]
        
        # If status is failed, stop polling
        if response.get("status") == "failed":
            raise Exception(f"Generation failed for clip {clip_id}")
            
        # Wait before next check
        await asyncio.sleep(delay)
    
    raise Exception(f"Timeout waiting for audio for clip {clip_id}")


async def get_generation_audio(generation_id: str, token: str):
    """
    Get all audio URLs for a generation.
    
    Args:
        generation_id: The ID of the generation
        token: Auth token
    
    Returns:
        List of audio URLs
    """
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/feed/v2?ids={generation_id}"
    
    response = await fetch(api_url, headers, method="GET")
    clips = response.get("clips", [])
    
    audio_urls = []
    for clip in clips:
        try:
            audio_url = await wait_for_audio(clip["id"], token)
            audio_urls.append(audio_url)
        except Exception as e:
            logger.error(f"Error getting audio for clip {clip['id']}: {str(e)}")
    
    return audio_urls


# You can use this function to send notifications
def notify(message: str):
    logger.info(message)
