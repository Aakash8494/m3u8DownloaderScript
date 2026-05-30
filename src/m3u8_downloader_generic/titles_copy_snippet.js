let titles = Array.from(document.querySelectorAll('.tutor-course-topic-item-title'))
    .map((el, index) => `${el.innerText.trim().replace(/[/\\?%*:|"<>]/g, '-')}`);

console.log("✅ Here are your titles:");
console.log(titles.join('\n'));

// This automatically copies the text to your clipboard!
copy(titles.join('\n'));
console.log("📋 ALL TITLES COPIED TO CLIPBOARD! You can paste them in a notepad.");