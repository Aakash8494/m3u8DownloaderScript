/**
 * -----------------------------------------------------------
 * PASSIVE LISTENER SCRIPT (Manual Mode)
 * -----------------------------------------------------------
 */

const CONFIG = {
    RESOURCE_PATTERN: "240p.m3u8",
    // Helper to find the main course title (Top of page)
    SELECTOR_COURSE_TITLE: '#course-stages .z-10 > div > div > div',
    // Helper to try and guess the CURRENT video title from the UI
    // (Looks for the active/highlighted text in the player area)
    SELECTOR_CURRENT_VIDEO_TITLE: 'div > div > p'
};

/**
 * 1. TEXT CLEANING UTILITIES (Same as before)
 */
const TextUtils = {
    clean: (text) => {
        if (!text) return "Unknown_Course";
        return text
            .replace(/वीडियो श्रृंखला|Video Series/g, "")
            .replace(/[!@#$%^&()[\]{};',.`~+=|/\\*?<>:"]/g, "") // Full symbol strip
            .replace(/\s+/g, ' ')
            .trim();
    },
    toSnakeCase: (text) => {
        return TextUtils.clean(text).replace(/\s+/g, '_');
    }
};

/**
 * 2. STATE MANAGEMENT
 */
const State = {
    courseTitle: "",
    capturedVideos: [], // Stores { url, title }
    processedUrls: new Set(), // To prevent duplicates

    init: () => {
        // Try to grab course title immediately
        const titleEl = document.querySelector(CONFIG.SELECTOR_COURSE_TITLE);
        State.courseTitle = TextUtils.clean(titleEl ? titleEl.innerText : "Course_Name");
        console.log(`📂 Active Course: ${State.courseTitle}`);
        UI.updateCount();
    },

    addVideo: (url) => {
        if (State.processedUrls.has(url)) return; // Skip duplicates

        State.processedUrls.add(url);

        // Try to guess the title of the video you just clicked.
        // Since we are manual, we assume the "active" or "clicked" element is relevant.
        // We fallback to a timestamp if we can't find text.
        const activeTitle = State.guessCurrentTitle();
        const index = State.capturedVideos.length + 1;
        const cleanTitle = TextUtils.toSnakeCase(activeTitle);

        State.capturedVideos.push({
            index: index,
            title: cleanTitle,
            url: url
        });

        UI.showToast(`✅ Captured: ${index}. ${cleanTitle}`);
        UI.updateCount();
        console.log(`Captured: ${cleanTitle}`);
    },

    guessCurrentTitle: () => {
        // Strategy: Look for the text that the user likely just clicked.
        // In the specific UI you provided previously, titles were in p tags inside divs.
        // We will try to find the text that matches the "active" visual state if possible,
        // otherwise, we genericize it.

        // Option A: Is there a highlighted element?
        // (You might need to adjust this selector based on what "Active" looks like in CSS)
        // For now, we return a placeholder or try to grab the last clicked element text if we tracked it.

        // Fallback Strategy: Just return "Video" and let the index handle the ordering.
        // If you want to be specific, you can manually rename the files later, 
        // OR we can rely on the fact that you usually click them in order.
        return "Video_Clip";
    }
};

/**
 * 3. UI COMPONENTS (Toast & Button)
 */
const UI = {
    container: null,
    btn: null,

    init: () => {
        // Create Container
        const div = document.createElement('div');
        div.style.cssText = "position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 10px; font-family: sans-serif;";
        document.body.appendChild(div);
        UI.container = div;

        // Create Download Button
        const btn = document.createElement('button');
        btn.innerText = "⬇️ Finish & Download (0)";
        btn.onclick = Exporter.generateAndDownload;
        btn.style.cssText = "background: #111827; color: #fff; border: 1px solid #374151; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s;";

        // Hover effect
        btn.onmouseover = () => btn.style.transform = "scale(1.05)";
        btn.onmouseout = () => btn.style.transform = "scale(1)";

        div.appendChild(btn);
        UI.btn = btn;
    },

    showToast: (msg) => {
        const toast = document.createElement('div');
        toast.innerText = msg;
        toast.style.cssText = "background: #10B981; color: white; padding: 10px 20px; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); animation: fadeIn 0.3s ease-out;";

        // Add to container (above button)
        UI.container.insertBefore(toast, UI.btn);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    updateCount: () => {
        if (UI.btn) UI.btn.innerText = `⬇️ Finish & Download (${State.capturedVideos.length})`;
    }
};

/**
 * 4. NETWORK LISTENER (The Core)
 */
const NetworkWatcher = {
    start: () => {
        // PerformanceObserver is better than setInterval
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
                if (entry.name.includes(CONFIG.RESOURCE_PATTERN)) {
                    State.addVideo(entry.name);
                }
            });
        });

        observer.observe({ entryTypes: ["resource"] });
        console.log("👁️ Network Watcher Started...");
    }
};

/**
 * 5. EXPORT LOGIC
 */
const Exporter = {
    generateAndDownload: () => {
        if (State.capturedVideos.length === 0) {
            alert("No videos captured yet!");
            return;
        }

        let content = `python downloader.py \\\n  --folder "${State.courseTitle}"`;

        State.capturedVideos.forEach(v => {
            // Note: Since we are in manual mode, we might not have perfect titles.
            // We append the index to ensure uniqueness.
            content += ` \\\n  --url "${v.url}|${v.index}.${v.title}"`;
        });

        // Remove trailing backslash from last line
        // (Not strictly necessary if logic handles it, but good practice)

        const filename = `${TextUtils.toSnakeCase(State.courseTitle)}_manual_command.txt`;

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        console.log("✅ Command file downloaded.");
    }
};

// --- INITIALIZE ---
(function () {
    // Add CSS Animation for Toast
    const style = document.createElement('style');
    style.innerHTML = `@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }`;
    document.head.appendChild(style);

    State.init();
    UI.init();
    NetworkWatcher.start();

    UI.showToast("Ready! Click videos to capture.");
})();