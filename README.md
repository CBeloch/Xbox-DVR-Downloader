This project is targeted to download and archive screenshots and clips that you've recorded on your Xbox console and shared on Xbox Live.

I created two scripts.

1. Script one has been written in Python and uses the [`xbox-webapi-python`](https://github.com/OpenXbox/xbox-webapi-python) library and uses the official [Xbox Live REST API](https://docs.microsoft.com/en-us/gaming/xbox-live/api-ref/xbox-live-rest/atoc-xboxlivews-reference).

2. Script two has been written in TypeScript and uses [`x-ray`](https://www.npmjs.com/package/x-ray) to grab screenshots and clips from [GamerDVR](https://gamerdvr.com).

   > ⚠️ Please do not use this script as your primary archiving script ⚠️
   >
   > I created this to download a larger archive as the official API didn't returned enough media.
   >
   > But even GamerDVR doesn't keep all media references and you just create a lot of load on their server by using this script!

The scripts will download all media they can find and save them in a folder per game and names the media by the capture date and time.

You an run the scripts again, I've implemented code that will skip media if the target file already exists.

[TOC]

# Python (with official API)

This script requires Python 3

> All scripts in this sections are run inside the `Python`-folder

- Create an new application in [Azure AD](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).
  - Name your app
  - Select "Personal Microsoft accounts only" under supported account types
  - Add http://localhost/auth/callback as a Redirect URI of type "Web"
- Copy your Application (client) ID for later use
- On the App Page, navigate to "Certificates & secrets"
  - Generate a new client secret and save for later use

Everything setup? 

Then install the [`xbox-webapi-python`](https://github.com/OpenXbox/xbox-webapi-python)

```bash
pip install xbox-webapi
```

Authenticate yourself using the Client-ID and Client-Secret from above

```bash
xbox-authenticate --client-id <client-id> --client-secret <client-secret> -t token.json
```

Your browser will open to run the authentication process of your Xbox account.

The token necessary for the script are stored in the `token.json`. If you have to refresh the tokens, run the authentication command again.

Now run the script

```bash
python run.py
```

You'll find all the downloaded media in the `./Games` folder

# NodeJS

>  **Reminder**
> ⚠️ Please do not use this script as your primary archiving script ⚠️

This script requires NodeJS >= 12.19 (LTS)

> All scripts in this sections are run inside the `NodeJS`-folder

Install dependencies

```bash
yarn install
# or
npm install
```

Run the script

```bash
npm run downloadDev
```

You'll find all the downloaded media in the `./Games` folder

# Docker

> All scripts in this sections are run inside the root folder of this project

## Python Archiver

At the moment there is no Docker container for the Python script as we have to regenerate the tokens from time to time.

## NodeJS Archiver

> **Reminder**
> ⚠️ Please do not use this script as your primary archiving script ⚠️

You can build yourself the image yourself by running
```bash
docker build -f ./Dockerfile.node.prod . -t dvrdownload:1.0
```
The image will reveive the tag `dvrdownload:1.0`.
If you run the image in a container, attach a volume to `/home/app/Games` and set the environment variable `GAMERTAG` to your gamertag.

### via docker-compose
Edit [`archiver.env`](./archiver.env) and replace `MYGAMERTAG` with your own

Then run
```bash
docker-compose up
```

## Development container

I've included my development docker file ([`Dockerfile.node.dev`](./Dockerfile.node.dev)) as well. I attach to it via Visual Studio Code and can work in a controlled environment without messing with different node and typescript versions on my main machine.

If you want to launch it via `docker-compose` just run

```bash
docker-compose -f docker-compose.dev.yml up -d
```

You can then attach to the `xboxdvr-node` container