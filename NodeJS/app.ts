import XRay from "x-ray";

interface ScreenshotData {
    game_title: string
    link: string
    download: string
}

function clean_game_title(title: string): string {
    let regex = /[^\d\w\-_\s]/gi
    return title.replace(regex, '')
}

async function run() {
    let x = XRay()
    
    let screenshots: [ScreenshotData] = await x('https://gamerdvr.com/gamer/cbeloch/screenshots', 'ul.slideshow-image-viewer li', [
        {
            game_title: '.top-row a',
            link: '.content-row a@href',
            download: '@data-x-s'
        }
    ]).paginate('ul.pagination .next a@href')
    .limit(2)

    screenshots.forEach((screen) => {
        console.log(`${screen.game_title} <|> ${clean_game_title(screen.game_title)}`)
    })
}

run()