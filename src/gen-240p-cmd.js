/**
 * CONFIGURATION
 * Adjust timing and patterns here.
 */
const CONFIG = {
    // Delays in milliseconds
    DELAY_AFTER_CLICK: 1500,
    DELAY_BETWEEN_VIDEOS: 2000,
    TIMEOUT_RESOURCE: 5000,

    // Search patterns
    RESOURCE_PATTERN: "240p.m3u8",
    SELECTOR_TITLE: '#course-stages .z-10 > div > div > div',
    SELECTOR_VIDEOS: '[id^="video-0-"]'
};

/**
 * TEXT UTILITIES
 * Handles string cleaning and filename formatting.
 */
const TextUtils = {
    clean: (text) => {
        if (!text) return "Unknown_Course";
        return text
            .replace(/वीडियो श्रृंखला|Video Series/g, "") // Remove specific localized text
            // Expanded regex: Removes Windows illegal chars + ! @ # $ % ^ & ( ) [ ] { } , . ; '
            .replace(/[!@#$%^&()[\]{};',.`~+=|/\\*?<>:"]/g, "")
            .replace(/\s+/g, ' ')                         // Collapse multiple spaces
            .trim();
    },

    toSnakeCase: (text) => {
        return TextUtils.clean(text).replace(/\s+/g, '_');
    }
};

/**
 * BROWSER UTILITIES
 * Handles waiting, network monitoring, and downloading.
 */
const BrowserUtils = {
    sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

    waitForNetworkResource: (pattern, timeout) => {
        return new Promise((resolve, reject) => {
            const start = Date.now();

            const checker = setInterval(() => {
                const resources = performance.getEntriesByType("resource");
                const match = resources.find(r => r.name.includes(pattern));

                if (match) {
                    clearInterval(checker);
                    resolve(match.name);
                } else if (Date.now() - start > timeout) {
                    clearInterval(checker);
                    resolve(null); // Return null on timeout instead of string "TIMEOUT"
                }
            }, 200);
        });
    },

    saveFile: (content, filename) => {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');

        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
};

/**
 * MAIN LOGIC
 */
(async function extractCourseData() {
    console.log("🚀 Starting extraction...");
    performance.clearResourceTimings();

    // 1. Get Course Title
    const rawTitle = document.querySelector(CONFIG.SELECTOR_TITLE)?.innerText;
    const courseTitle = TextUtils.clean(rawTitle);

    // 2. Initialize Command List
    const commandLines = [
        `python downloader.py \\`,
        `  --folder "${courseTitle}"`
    ];

    // 3. Identify Video Elements
    // The UI duplicates elements, so we only process the first half
    const allVideoElements = document.querySelectorAll(CONFIG.SELECTOR_VIDEOS);
    const uniqueCount = Math.floor(allVideoElements.length / 2);

    // 4. Iterate (Backwards to preserve specific UI order)
    for (let i = uniqueCount - 1; i >= 0; i--) {
        const element = allVideoElements[i];
        const titleEl = element.querySelector('div > div > p');

        if (!titleEl) continue;

        const videoTitle = TextUtils.toSnakeCase(titleEl.innerText);
        const index = i + 1;

        console.log(`Processing [${index}/${uniqueCount}]: ${videoTitle}`);

        // Click and Wait
        titleEl.click();
        await BrowserUtils.sleep(CONFIG.DELAY_AFTER_CLICK);

        // Capture URL
        const url = await BrowserUtils.waitForNetworkResource(CONFIG.RESOURCE_PATTERN, CONFIG.TIMEOUT_RESOURCE);

        if (url) {
            commandLines.push(`  --url "${url}|${index}.${videoTitle}" \\`);
        } else {
            console.warn(`⚠️ Failed to capture URL for: ${videoTitle}`);
            commandLines.push(`  # MISSING URL FOR: ${index}.${videoTitle} \\`);
        }

        // Reset for next video
        await BrowserUtils.sleep(CONFIG.DELAY_BETWEEN_VIDEOS);
        performance.clearResourceTimings();
    }

    // 5. Finalize and Download
    // Remove trailing backslash from the last item for valid syntax
    const lastLineIndex = commandLines.length - 1;
    commandLines[lastLineIndex] = commandLines[lastLineIndex].replace(' \\', '');

    const finalCommand = commandLines.join('\n');
    const filename = `${TextUtils.toSnakeCase(courseTitle)}_command.txt`;

    BrowserUtils.saveFile(finalCommand, filename);
    console.log("✅ Extraction Complete! File downloaded.");
})();