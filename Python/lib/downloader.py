import os
import re

import lib.helper as helper

from aiohttp import ClientResponseError, ClientSession
from xbox.webapi.api.client import XboxLiveClient

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
            # Be sure to have a valid response
            if 200 <= resp.status < 300:
                pass
            else:
                print("> Error: Status Code %d" % resp.status)
                return

            data = await resp.read()

            with open(FILE_DEST, "wb") as f:
                f.write(data)

async def screenshots(TARGET_DIR: str, xbl_client: XboxLiveClient, offset: int = 0):
    print("Will begin downloading screenshots...") 

    # Get Screenshots
    screenshotResponse = await xbl_client.screenshots.get_recent_own_screenshots(skip_items = offset, max_items = 100)

    # Iterate screenshots
    for idx, screenshot in enumerate(screenshotResponse.screenshots):
        TARGET_DIR_GAME = "%s/%s" % (TARGET_DIR, helper.clean_game_title(screenshot.title_name))
        
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
    
    print("Done downloading screenshots") 

async def gameclips(TARGET_DIR: str, xbl_client: XboxLiveClient, offset: int = 0):
    print("Will begin downloading gameclips...") 

    # Get Game Clips
    clipsResponse = await xbl_client.gameclips.get_saved_own_clips(skip_items = offset, max_items = 30)

    # Iterate Game Clips
    for idx, clip in enumerate(clipsResponse.game_clips):
        TARGET_DIR_GAME = "%s/%s" % (TARGET_DIR, helper.clean_game_title(clip.title_name))
        
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

    print("Done downloading gameclips") 

