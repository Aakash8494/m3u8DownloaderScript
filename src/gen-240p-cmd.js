/**
 * REUSABLE UTILITIES
 */
const Sanitizer = {
    // Collapses spaces and removes illegal Windows characters
    clean: (text) => {
        return text
            .replace(/वीडियो श्रृंखला|Video Series/g, "")
            .replace(/[:/"\\|*?<>]/g, "")
            .replace(/\s+/g, ' ')
            .trim();
    },
    // For filenames/video titles where underscores are preferred
    toSnakeCase: (text) => {
        return Sanitizer.clean(text).replace(/\s+/g, '_');
    }
};

const BrowserUtils = {
    sleep: (ms) => new Promise(r => setTimeout(r, ms)),

    waitForResource: (pattern, timeout = 10000) => {
        return new Promise((resolve) => {
            const start = Date.now();
            const interval = setInterval(() => {
                const logs = performance.getEntriesByType("resource");
                const found = logs.find(r => r.name.includes(pattern));
                if (found) { clearInterval(interval); resolve(found.name); }
                else if (Date.now() - start > timeout) { clearInterval(interval); resolve("TIMEOUT"); }
            }, 200);
        });
    },

    downloadTextFile: (content, filename) => {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
};

/**
 * MAIN EXTRACTION ENGINE
 */
(async function main() {
    performance.clearResourceTimings();

    const rawTitle = document.querySelector('#course-stages .z-10 > div > div > div')?.innerText || "Course";
    const courseTitle = Sanitizer.clean(rawTitle);
    const videoElements = document.querySelectorAll('[id^="video-0-"]');

    let command = `python downloader.py \\\n  --folder "${courseTitle}"`;

    // Process videos
    for (let i = videoElements.length / 2 - 1; i >= 0; i--) {
        const titleEl = videoElements[i].querySelector('div > div > p');
        if (!titleEl) continue;

        const videoTitle = Sanitizer.toSnakeCase(titleEl.innerText);

        await BrowserUtils.sleep(1500);
        titleEl.click();

        const url = await BrowserUtils.waitForResource("240p.m3u8");
        command += ` \\\n  --url "${url}|${i + 1}.${videoTitle}"`;

        await BrowserUtils.sleep(2000);
        performance.clearResourceTimings();
    }

    const filename = `${Sanitizer.toSnakeCase(courseTitle)}_command.txt`;
    BrowserUtils.downloadTextFile(command, filename);
    console.log("Extraction Complete!");
})();