(function () {
    const fullTitle = document.querySelector('#course-stages .z-10 > div > div > div')?.innerText || "Downloaded_Course";

    // 1. Split by colon
    // 2. Take the second part (index 1)
    // 3. Fallback to the full title if no colon exists
    let cleanTitle = fullTitle.includes(':')
        ? fullTitle.split(':')[1].trim()
        : fullTitle.trim();

    copy(cleanTitle);

    console.log("Course Title (after colon) copied:", cleanTitle);
})();