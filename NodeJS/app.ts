import XRay from "x-ray"
import { default as fs } from 'fs'
import { default as fetch } from 'node-fetch'

import { ScreenshotData, GameClipData } from './model'

const args = process.argv.slice(2) // Remove the arguments we don't care about

const GAMERTAG = process.env.GAMERTAG ?? args[0]
const TARGET_DIR = "./Games"

// Setup x-ray
const x = XRay({
    filters: {
        // Filter to cleanup the game titles
        cleanGameTitle(title: string): string {
            // only keep digits, word characters, dashes, underscores and whitespaces
            let regex = /[^\d\w\-_\s]/gi
            return title.replace(regex, '')
        },
        // Format date for our file naming
        formattedDate: function(value: string) {
            try {
                let date = new Date(value)
                return date.toISOString()
                    .replace(/T/g, '_')
                    .replace(/:/g, '-')
                    .replace(/Z/g, '')
                    .split('.')
                    [0]
            } catch {
                return value
            }
        }
    }
})

// Download file from url
async function download(urlString: string, destination: string, filename: string | null) {
    fs.mkdirSync(destination, { recursive: true })

    let url = new URL(urlString)
    let pathComponents = url.pathname.split('/')
    let baseName = pathComponents[pathComponents.length - 1]
    let baseNameParts = baseName.split('.')
    let fileExtension = baseNameParts[baseNameParts.length - 1]

    let fullfilename = filename ? `${filename}.${fileExtension}` : baseName

    let fileDestination = `${destination}/${fullfilename}`

    if (fs.existsSync(fileDestination)) {
        console.log(`${fileDestination} already exists`)
    }

    let response = await fetch(urlString)

    if (response.ok) {
        await new Promise<void>((resolve, reject) => {
            let fileStream = fs.createWriteStream(fileDestination)
            response.body.pipe(fileStream)
            response.body.on("error", (err) => {
                reject(err);
            });
            fileStream.on('finish', () => {
                console.log(`Downloaded ${fileDestination}`)
                resolve()
            })
        })
    } else {
        console.log(`Error downloading - Status code: ${response.status}`)
    }
}

// Get screenshot data
async function getScreenshots(): Promise<[ScreenshotData]> {
    return await x(`https://gamerdvr.com/gamer/${GAMERTAG}/screenshots`, 'ul.slideshow-image-viewer li', [
        {
            gameTitle: '.top-row a',
            gameTitleSlug: '.top-row a | cleanGameTitle',
            dateTime: x('.content-row a@href', '.toggle-details time | formattedDate'),
            download: '@data-x-s'
        }
    ]).paginate('ul.pagination .next a@href')
    // .limit(1)
}

// get gameclip data
async function getGameClips(): Promise<[GameClipData]> {
    return await x(`https://gamerdvr.com/gamer/${GAMERTAG}/videos`, 'ul.filter-clips li', [
        {
            gameTitle: '.top-row a',
            gameTitleSlug: '.top-row a | cleanGameTitle',
            dateTime: x('.content-row a@href', '.toggle-details time | formattedDate'),
            download: '@data-x-s'
        }
    ]).paginate('ul.pagination .next a@href')
    // .limit(1)
}

// main run script
async function run() {
    // Do screenshots first
    console.log('Will grab screenshots...')
    let screenshots = await getScreenshots()
    for (const screen of screenshots) {
        let save_dir = `${TARGET_DIR}/${screen.gameTitleSlug}`
        console.log(`Downloading screenshot for ${screen.gameTitle}...`)
        await download(screen.download, save_dir, screen.dateTime)
        console.log('') // Log empty line
    }

    // Now do gameclips
    console.log('Will grab game clips...')
    let clips = await getGameClips()
    for (const clip of clips) {
        let save_dir = `${TARGET_DIR}/${clip.gameTitleSlug}`
        console.log(`Downloading clip for ${clip.gameTitle}...`)
        await download(clip.download, save_dir, clip.dateTime)
        console.log('') // Log empty line
    }
}

// Check if Gamertag has been passed
if (!GAMERTAG) {
    console.error('Please pass a gamertag')
    console.log('ts-node app.ts GAMERTAG')
    console.log('')
    console.log('You can also set a GAMERTAG ENV variable')
} else {
    run()
}