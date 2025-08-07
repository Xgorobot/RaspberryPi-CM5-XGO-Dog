#!/usr/bin/env python3
import argparse
import json
import logging
import uuid

import websockets
import time
from protocols import MsgType, full_client_request, receive_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cluster(voice: str) -> str:
    if voice.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


async def main(text = '你好,我是lulu,请问有什么可以帮你',cluster = '',voice_type = 'zh_female_wanqudashu_moon_bigtts' ):
    endpoint = 'wss://openspeech.bytedance.com/api/v1/tts/ws_binary'
    appid = '3984980014'
    access_token ='dME9mE6J4NWygiMFg6vhrqQ2S49TY2FX'
    encoding = 'wav'

    # Determine cluster
    cluster = cluster if cluster else get_cluster(voice_type)

    # Connect to server
    headers = {
        "Authorization": f"Bearer;{access_token}",
    }

    logger.info(f"Connecting to {endpoint} with headers: {headers}")
    websocket = await websockets.connect(
        endpoint, additional_headers=headers, max_size=10 * 1024 * 1024
    )
    logger.info(
        f"Connected to WebSocket server, Logid: {websocket.response.headers['x-tt-logid']}",
    )

    try:
        # Prepare request payload
        request = {
            "app": {
                "appid": appid,
                "token": access_token,
                "cluster": cluster,
            },
            "user": {
                "uid": str(uuid.uuid4()),
            },
            "audio": {
                "voice_type": voice_type,
                "encoding": encoding,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "operation": "submit",
                "speed_ratio" : "1",
                "extra_param": json.dumps(
                    {
                        "disable_markdown_filter": False,
                    }
                ),
            },
        }

        # Send request
        await full_client_request(websocket, json.dumps(request).encode())

        # Receive audio data
        audio_data = bytearray()
        while True:
            msg = await receive_message(websocket)

            if msg.type == MsgType.FrontEndResultServer:
                continue
            elif msg.type == MsgType.AudioOnlyServer:
                audio_data.extend(msg.payload)
                if msg.sequence < 0:  # Last message
                    break
            else:
                raise RuntimeError(f"TTS conversion failed: {msg}")

        # Check if we received any audio data
        if not audio_data:
            raise RuntimeError("No audio data received")

        # Save audio file
        name="gptfree_speak"
        filename = f"{name}.{encoding}"
        with open(filename, "wb") as f:
            f.write(audio_data)
        logger.info(f"Audio received: {len(audio_data)}, saved to {filename}")

    finally:
        await websocket.close()
        logger.info("Connection closed")


#if __name__ == "__main__":
#    import asyncio
#
#    asyncio.run(main())
