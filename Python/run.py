import sys
import os
import asyncio

import lib.helper as helper
import lib.downloader as downloader

from aiohttp import ClientResponseError, ClientSession

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

from xbox.webapi.authentication.models import OAuth2TokenResponse

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TOKEN_DIR = "./token.json"
TARGET_DIR = "../Games" if len(sys.argv) == 1 else sys.argv[1]

TARGET_DIR_ABS = os.path.abspath(TARGET_DIR)

async def run(): 
    # Check for Token
    if not os.path.exists(TOKEN_DIR):
        print("Can't find token.json in the current folder")
        sys.exit(-1)

    print("All media will be downloaded to")
    print("> %s" % TARGET_DIR_ABS)

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

        await downloader.screenshots(TARGET_DIR_ABS, xbl_client)
        await downloader.gameclips(TARGET_DIR_ABS, xbl_client)

# RUN
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(run())