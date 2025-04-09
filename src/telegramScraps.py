from telethon.sync import TelegramClient
import asyncio
from telethon.tl.types import PeerChannel
from datetime import datetime, timezone
import os, sys

# Replace with your own API credentials
API_ID = '28071491'
API_HASH = '693b1d3487399cf82661753ac3f95acf'
PHONE_NUMBER = '+351963828380'  # Only needed for first-time login

# Chat/Group/Channel username or ID
CHAT_ID = '1347596868'

def fetch():
    return asyncio.run(corvo_bets())

async def corvo_bets():
    bets = []
    try:
        async with TelegramClient('session_name', API_ID, API_HASH) as client:
            # Ensure we're logged in
            await client.start(PHONE_NUMBER)

            entity = await client.get_entity('t.me/Corvo_bets')
            #entity = PeerChannel(channel_id=-1002094086801)

            # Get messages since START_DATE
            async for message in client.iter_messages(entity, offset_date=datetime(2023, 6, 30), reverse=True):
                # print('---')
                # print(message.text)
                if message.date >= datetime(2023, 7, 1, tzinfo=timezone.utc):
                    continue
                if message.date < datetime(2023, 6, 30, tzinfo=timezone.utc):
                    break
                if message.text is not None and "PRÉ-LIVE" in message.text and '📊' in message.text:
                    bet = {}
                    filtered_msg = message.text.split('📊')[1].split('\n')[0]
                    bet['date'] = f"{message.date}"
                    bet['odd'] = filtered_msg.split(' ')[1].strip()
                    bet['stake %'] = filtered_msg.split(' ')[-1:][0]
                    if '✅' in message.text:
                        bet['outcome'] = "GREEN"
                    else:
                        bet['outcome'] = "RED"

                    bets.append(bet)
    except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    return bets

async def corvo_bets_nba():
    bets = []
    try:
        async with TelegramClient('session_name', API_ID, API_HASH) as client:
            # Ensure we're logged in
            await client.start(PHONE_NUMBER)

            entity = PeerChannel(channel_id=-1002094086801)

            # Get messages since START_DATE
            async for message in client.iter_messages(entity, offset_date=datetime(2024, 10, 1), reverse=True):
                # print('---')
                # print(message.text)
                if message.text is not None and "@" in message.text :
                    bet = {}
                    bet['date'] = f"{message.date}"
                    bet['odd'] = message.text.split('@')[1].split(' ')[0]
                    #bet['stake %'] = filtered_msg.split(' ')[-1:][0]
                    if '✅' in message.text:
                        bet['outcome'] = "GREEN"
                    else:
                        bet['outcome'] = "RED"

                    bets.append(bet)
    except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    return bets