const puppeteer = require('puppeteer');

async function scrapeYahooNews(ticker) {
    const url = `https://finance.yahoo.com/quote/${ticker}/news?p=${ticker}`;
    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Accept cookies if present
    try {
        const agreeBtn = await page.$x("//button[contains(., 'I agree')]");
        if (agreeBtn.length > 0) {
            await agreeBtn[0].click();
            await page.waitForTimeout(1000);
        }
    } catch (e) {
        console.error("Cookie consent failed:", e);
    }

    // Scrape news headlines
    const headlines = await page.evaluate(() => {
        const articles = document.querySelectorAll('h3');
        return Array.from(articles).map(article => article.innerText.trim());
    });

    await browser.close();
    return headlines;
}

// Example usage
scrapeYahooNews('MSFT').then(console.log).catch(console.error);

