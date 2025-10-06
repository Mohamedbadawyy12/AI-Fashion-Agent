import os
import requests
import base64
from core.config import settings




def generate_image_from_prompt(prompt: str) -> bytes:
    """using text to image - image generator using stability"""
    api_host = 'https://api.stability.ai'
    engine_id = 'stable-diffusion-xl-1024-v1-0'
    api_key = settings.STABILITY_API_KEY


    response = requests.post(
    f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        },
        json={
        'text_prompts': [{'text': prompt}],
        'cfg_scale': 7,
        'height': 1024,
        'width': 1024,
        'samples': 1,
        'steps': 30,
        },
        timeout=60,
    )


    if response.status_code != 200:
        raise Exception(f"Stability API error: {response.status_code} {response.text}")


    data = response.json()
    b64 = data['artifacts'][0]['base64']
    return base64.b64decode(b64)