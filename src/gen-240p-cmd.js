(async function () {
    performance.clearResourceTimings();
    console.log("Starting extraction...");

    const courseTitle = document.querySelector('#course-stages .z-10 > div > div > div')?.innerText.replace(/वीडियो श्रृंखला[:/]|Video Series[:/]/g, "").trim() || "Downloaded_Course";
    const videoElements = document.querySelectorAll('[id^="video-0-"]');
    let command = `python downloader.py \\\n  --folder "${courseTitle.trim()}"`;

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

    // Helper for manual delays
    const sleep = (ms) => new Promise(r => setTimeout(r, ms));

    for (let i = videoElements.length / 2 - 1; i >= 0; i--) {
        const row = videoElements[i];
        const titleEl = row.querySelector('div > div > p');

        if (titleEl) {
            const title = titleEl.innerText.trim().replace(/[’'!?]/g, "").replace(/\s+/g, '_');

            console.log(`Preparing to click: ${title}`);

            // --- 1. WAIT BEFORE CLICK ---
            // Gives the browser time to breathe before the next action
            await sleep(1500);

            titleEl.click();
            console.log("Clicked. Waiting for resource...");

            // 2. Wait for the specific resource to appear in network logs
            const videoUrl = await waitForResource("240p.m3u8", 10000);

            command += ` \\\n  --url "${videoUrl}|${i + 1}.${title}"`;

            // --- 3. WAIT AFTER RESOURCE FOUND ---
            // Ensures the UI has finished any "loading" animations 
            // before we clear logs and move to the next item
            console.log("Resource found. Waiting for UI to settle...");
            await sleep(2000);

            performance.clearResourceTimings();
        }
    }

    // --- LOG TO FILE LOGIC ---
    try {
        const blob = new Blob([command], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${courseTitle.replace(/\s+/g, '_')}_command.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        console.log("Extraction complete. File downloaded.");
    } catch (err) {
        console.error("Download failed", err);
    }
})();