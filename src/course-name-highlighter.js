// Paste your list between the backticks
const missingNames = `
आत्मज्ञान की ओर पहले कदम
जाति प्रथा का सच
मन, वासनाएँ और आज़ादी
सबसे बड़ा धोख़ा
समय का सही उपयोग
सम्पूर्ण कामनाओं की पूर्ति का सरल मार्ग
सही कर्म का चुनाव कैसे करें?
सही राह पर चलने का डर
सही संग, मुक्त जीवन
`.split('\n').map(name => name.trim()).filter(name => name.length > 0);

// Find all course spans
const courseSpans = document.querySelectorAll('span.font-hi');

courseSpans.forEach(span => {
    const text = span.innerText.trim();
    if (missingNames.includes(text)) {
        // Highlight the background of the entire card
        const card = span.closest('a') || span;
        card.style.border = "4px solid #FFD700"; // Gold border
        card.style.backgroundColor = "rgba(255, 215, 0, 0.2)"; // Light yellow tint
        span.style.fontWeight = "bold";
    }
});

console.log(`Highlighted ${missingNames.length} items!`);