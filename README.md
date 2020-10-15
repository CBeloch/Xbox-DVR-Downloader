This project is targeted to download and archive screenshots and clips that you've recorded on your Xbox console and shared on Xbox Live.

I created two scripts.

1. Script one has been written in Python and uses the `xbox-webapi-python` library and uses the official [Xbox Live REST API](https://docs.microsoft.com/en-us/gaming/xbox-live/api-ref/xbox-live-rest/atoc-xboxlivews-reference).

2. Script two has been written in TypeScript and uses [x-ray](https://www.npmjs.com/package/x-ray) to grab screenshots and clips from [GamerDVR](https://gamerdvr.com).

   > ⚠️ Please do not use this script as your primary archiving script ⚠️
   >
   > I created this to download a larger archive as the official API didn't returned enough media.
   >
   > But even GamerDVR doesn't keep all media references and you just create a lot of load on their server by using this script!

[TOC]

# Python (with official API)



# Docker

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