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

        # Get Screenshots
        screenshotResponse = await xbl_client.screenshots.get_saved_own_screenshots(max_items = 100)

        # Iterate screenshots
        for screenshot in screenshotResponse.screenshots:
            TARGET_DIR_GAME = "%s/%s" % (TARGET_DIR, clean_game_title(screenshot.title_name))
            
            # Create Game Folder if it does not exist
            os.makedirs(TARGET_DIR_GAME, exist_ok=True)

            SCREENSHOT_DESTINATION = "%s/%s" % (TARGET_DIR_GAME, screenshot.date_taken.strftime("%Y-%m-%d_%H-%M-%S"))
            
            await download(screenshot.screenshot_uris[0].uri, SCREENSHOT_DESTINATION, True)

# RUN
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(run())