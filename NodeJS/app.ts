import XRay from "x-ray"
import { default as fs } from 'fs'
import { default as fetch } from 'node-fetch'


const TARGET_DIR = "./Games"

let x = XRay({
    filters: {
        dvrDate: function(value: string) {
            let dateString = value.trim().match(/\d{2}\/\d{2}\/\d{4}/)
            return dateString ? new Date(dateString[0]) : value
        },
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


interface ScreenshotData {
    game_title: string
    dateTime: string
    link: string
    download: string
}

function clean_game_title(title: string): string {
    let regex = /[^\d\w\-_\s]/gi
    return title.replace(regex, '')
}

async function download(urlString: string, destination: string, filename: string | null) {
    fs.mkdirSync(destination, { recursive: true })

    let url = new URL(urlString)
    let pathComponents = url.pathname.split('/')
    let baseName = pathComponents[pathComponents.length - 1]
    let baseNameParts = baseName.split('.')
    let fileExtension = baseNameParts[baseNameParts.length - 1]

    let fullfilename = filename ? `${filename}.${fileExtension}` :  baseName

    let fileDestination = `${destination}/${fullfilename}`

    if (fs.existsSync(fileDestination)) {
        console.log(`${fileDestination} already exists`)
    }

    let response = await fetch(urlString)

    if (response.ok) {

        let fileStream = fs.createWriteStream(fileDestination);
        response.body.pipe(fileStream)
        console.log(`Downloaded ${fileDestination}`)

    } else {
        console.log(`Error downloading - Status code: ${response.status}`) 
    }
}

async function getScreenshots(): Promise<[ScreenshotData]> {
    return await x('https://gamerdvr.com/gamer/cbeloch/screenshots', 'ul.slideshow-image-viewer li', [
        {
            game_title: '.top-row a',
            dateTime: x('.content-row a@href', '.toggle-details time | formattedDate'),
            link: '.content-row a@href',
            download: '@data-x-s'
        }
    ]).paginate('ul.pagination .next a@href')
    .limit(1)
}

async function run() {
    let screenshots = await getScreenshots()

    console.log(screenshots)

    for (const screen of screenshots)  {
        let save_dir = `${TARGET_DIR}/${clean_game_title(screen.game_title)}`
        await download(screen.download, save_dir, screen.dateTime)
    }
}

run()