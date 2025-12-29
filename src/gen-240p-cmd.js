(async function () {
    performance.clearResourceTimings();
    console.log("Starting extraction...");

    // --- 1. CLEANING THE MAIN COURSE FOLDER NAME ---
    // Added [:/"] to the regex to catch colons, slashes, and double quotes
    let courseTitle = document.querySelector('#course-stages .z-10 > div > div > div')?.innerText || "Downloaded_Course";

    courseTitle = courseTitle
        .replace(/वीडियो श्रृंखला|Video Series/g, "") // Remove the words
        .replace(/[:/"\\|*?<>]/g, "")               // Remove all Windows-illegal characters
        .trim();

    const videoElements = document.querySelectorAll('[id^="video-0-"]');
    let command = `python downloader.py \\\n  --folder "${courseTitle}"`;

    const waitForResource = (pattern, timeout = 10000) => {
        return new Promise((resolve) => {
            const start = Date.now();
            const interval = setInterval(() => {
                const logs = performance.getEntriesByType("resource");
                const found = logs.find(r => r.name.includes(pattern));

                if (found) {
                    clearInterval(interval);
                    resolve(found.name);
                } else if (Date.now() - start > timeout) {
                    clearInterval(interval);
                    resolve("URL_NOT_FOUND_TIMEOUT");
                }
            }, 200);
        });
    };

    const sleep = (ms) => new Promise(r => setTimeout(r, ms));

    for (let i = videoElements.length / 2 - 1; i >= 0; i--) {
        const row = videoElements[i];
        const titleEl = row.querySelector('div > div > p');

        if (titleEl) {
            // --- 2. CLEANING INDIVIDUAL VIDEO TITLES ---
            // We strip quotes ("), colons (:), and slashes (/) specifically here
            let title = titleEl.innerText.trim()
                .replace(/[:/"\\|*?<>]/g, "") // Remove illegal Windows chars
                .replace(/\s+/g, '_');        // Replace spaces with underscores for CLI stability

            console.log(`Preparing to click: ${title}`);

            await sleep(1500);
            titleEl.click();
            console.log("Clicked. Waiting for resource...");

            const videoUrl = await waitForResource("240p.m3u8", 10000);
            command += ` \\\n  --url "${videoUrl}|${i + 1}.${title}"`;

            console.log("Resource found. Waiting for UI to settle...");
            await sleep(2000);

            performance.clearResourceTimings();
        }
    }

    // --- 3. EXPORT LOGIC ---
    try {
        const blob = new Blob([command], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // Ensure filename is also clean
        const safeFileName = courseTitle.replace(/\s+/g, '_');
        a.download = `${safeFileName}_command.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        console.log("Extraction complete. File downloaded.");
    } catch (err) {
        console.error("Download failed", err);
    }
})();