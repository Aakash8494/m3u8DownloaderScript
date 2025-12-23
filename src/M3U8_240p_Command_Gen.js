(async function () {
    // 1. Reset network memory for a fresh start
    performance.clearResourceTimings();

    console.log("Starting extraction... Results will be saved to a file.");

    const courseTitle = document.querySelector('#course-stages .z-10 > div > div > div')?.innerText || "Downloaded_Course";
    const videoElements = document.querySelectorAll('[id^="video-0-"]');

    // Initialize the command string
    let command = `python downloader.py \\\n  --folder "${courseTitle.trim()}"`;

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    for (let i = 0; i < videoElements.length / 2; i++) {
        const row = videoElements[i];
        const titleEl = row.querySelector('div > div > p');

        if (titleEl) {
            const title = titleEl.innerText.trim()
                .replace(/[’'!?]/g, "")
                .replace(/\s+/g, '_');

            // 2. Click the element to trigger the network request
            titleEl.click();

            // 3. Wait for the player to request the 240p.m3u8 file
            await sleep(3000);

            const logs = performance.getEntriesByType("resource");
            const targetLink = logs.find(r => r.name.includes("240p.m3u8"));

            const videoUrl = targetLink ? targetLink.name : "240p_URL_NOT_FOUND";

            command += ` \\\n  --url "${videoUrl}|${i + 1}.${title}"`;

            // 4. Clear timings so the next iteration doesn't find the same link
            performance.clearResourceTimings();
        }
    }

    // --- LOG TO FILE LOGIC ---
    try {
        // Create a data blob from our command string
        const blob = new Blob([command], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);

        // Create a hidden 'a' tag to trigger the download
        const a = document.createElement('a');
        a.href = url;
        // Use the course title as the filename
        a.download = `${courseTitle.trim().replace(/\s+/g, '_')}_command.txt`;

        // Trigger the download and clean up
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        alert("File successfully saved to your Downloads folder!");
    } catch (err) {
        // Fallback to clipboard if the file download is blocked by browser security
        copy(command);
        alert("File download failed. The command has been copied to your clipboard instead.");
    }
})();