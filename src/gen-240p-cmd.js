(async function () {
    performance.clearResourceTimings();
    console.log("Starting extraction...");

    const courseTitle = document.querySelector('#course-stages .z-10 > div > div > div')?.innerText.replace(/वीडियो श्रृंखला[:/]|Video Series[:/]/g, "").trim() || "Downloaded_Course";
    const videoElements = document.querySelectorAll('[id^="video-0-"]');
    let command = `python downloader.py \\\n  --folder "${courseTitle.trim()}"`;

    // Polling function to wait for the specific resource
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
            }, 200); // Check every 200ms
        });
    };

    for (let i = videoElements.length / 2 - 1; i >= 0; i--) {
        const row = videoElements[i];
        const titleEl = row.querySelector('div > div > p');

        if (titleEl) {
            const title = titleEl.innerText.trim().replace(/[’'!?]/g, "").replace(/\s+/g, '_');

            console.log(`Processing: ${title}`);
            titleEl.click();

            // MODIFIED: Instead of sleep(3000), we wait for the specific file
            const videoUrl = await waitForResource("240p.m3u8", 8000);

            command += ` \\\n  --url "${videoUrl}|${i + 1}.${title}"`;

            performance.clearResourceTimings();
            // Small buffer to let the UI settle before the next click
            await new Promise(r => setTimeout(r, 500));
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
    } catch (err) {
        console.error("Download failed", err);
    }
})();