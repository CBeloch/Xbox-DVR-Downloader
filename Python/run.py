import sys
import os
import asyncio
import re

from aiohttp import ClientResponseError, ClientSession

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

from xbox.webapi.authentication.models import OAuth2TokenResponse

CLIENT_ID = ""
CLIENT_SECRET = ""
TOKEN_DIR = "/Users/cbeloch/Library/Application Support/xbox/tokens.json"

TARGET_DIR = "./Games"

def clean_game_title(title: str) -> str:
    return re.sub("[^\d\w\-_\s]", '', title)

async def download(uri: str, destination: str, appendExtension: bool = False):
    async with ClientSession() as session:
        FILE_DEST = destination

        if appendExtension:
            regex = re.compile(r"\.([\w]{3,4})")
            matchedExtensions = regex.findall(uri)
            FILE_DEST = "%s.%s" % (destination, matchedExtensions[-1])
        
        # Check if downloaded file already exists
        if os.path.exists(FILE_DEST):
            print("%s already exists" % FILE_DEST)
            return
        
        print("Downloading to %s" % FILE_DEST)

        # Send Download Request
        async with session.get(uri) as resp:
            data = await resp.read()
            with open(FILE_DEST, "wb") as f:
                f.write(data)


async def download_screenshots(xbl_client: XboxLiveClient, offset: int = 0):
    # Get Screenshots
    screenshotResponse = await xbl_client.screenshots.get_recent_own_screenshots(skip_items = offset, max_items = 100)

    # Iterate screenshots
    for idx, screenshot in enumerate(screenshotResponse.screenshots):
        TARGET_DIR_GAME = "%s/%s" % (TARGET_DIR, clean_game_title(screenshot.title_name))
        
        # Create Game Folder if it does not exist
        os.makedirs(TARGET_DIR_GAME, exist_ok=True)

        SCREENSHOT_DESTINATION = "%s/%s" % (TARGET_DIR_GAME, screenshot.date_taken.strftime("%Y-%m-%d_%H-%M-%S"))
        
        await download(screenshot.screenshot_uris[0].uri, SCREENSHOT_DESTINATION, True)

        # print("Screenshot %d downloaded" % (offset + idx + 1))
    
    # Do recursion
    amount = len(screenshotResponse.screenshots)
    # if amount > 0:
    #     await download_screenshots(xbl_client, amount + offset)
    # else:
    #     print("Downloaded %d screenshots" % offset) 
    
    print("Downloaded %d screenshots" % (offset + amount)) 

async def download_gameclips(xbl_client: XboxLiveClient, offset: int = 0):
    # Get Game Clips
    clipsResponse = await xbl_client.gameclips.get_saved_own_clips(skip_items = offset, max_items = 30)

    # Iterate Game Clips
    for idx, clip in enumerate(clipsResponse.game_clips):
        TARGET_DIR_GAME = "%s/%s" % (TARGET_DIR, clean_game_title(clip.title_name))
        
        # Create Game Folder if it does not exist
        os.makedirs(TARGET_DIR_GAME, exist_ok=True)

        CLIP_DESTINATION = "%s/%s" % (TARGET_DIR_GAME, clip.date_recorded.replace(":", "-"))
        
        await download(clip.game_clip_uris[0].uri, CLIP_DESTINATION, True)

        # print("Clip %d downloaded" % (offset + idx + 1))
    
    # Do recursion
    amount = len(clipsResponse.game_clips)
    # if amount > 0:
    #     await download_gameclips(xbl_client, amount + offset)
    # else:
    #     print("Downloaded %d gameclips" % offset) 

    print("Downloaded %d gameclips" % (offset + amount)) 


async def run(): 
    async with ClientSession() as session:
        # Setup Authentication

        auth_mgr = AuthenticationManager(
            session, CLIENT_ID, CLIENT_SECRET, ""
        )

        with open(TOKEN_DIR, mode="r") as f:
            tokens = f.read()
        auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
        try:
            await auth_mgr.refresh_tokens()
        except ClientResponseError:
            print("Could not refresh tokens")
            sys.exit(-1)

        with open(TOKEN_DIR, mode="w") as f:
            f.write(auth_mgr.oauth.json())

        # Setup Xbox API Client
        xbl_client = XboxLiveClient(auth_mgr)

        await download_screenshots(xbl_client)
        await download_gameclips(xbl_client)

# RUN
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(run())