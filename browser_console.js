(function() {
    const lines = [
        "In 2022, a group of people met in a room in Washington D.C.",
        "You didn't vote for any of them.",
        "You've probably never heard most of their names.",
        // ... (Include all your 80 lines here)
    ];

    let currentIndex = 0;
    console.log("%c🚀 ID-TAGGING SYSTEM ACTIVE", "color: orange; font-weight: bold;");

    document.addEventListener('keydown', (e) => {
        if (e.key.toLowerCase() === 'n' && e.target.tagName !== 'TEXTAREA') {
            if (currentIndex < lines.length) {
                const lineNum = currentIndex + 1;
                const rawText = lines[currentIndex];
                // Adding a buffer and the ID tag
                const textToCopy = `${rawText} . . . [ID:${lineNum}]`;
                
                navigator.clipboard.writeText(textToCopy).then(() => {
                    console.clear();
                    console.log(`%c📋 Line ${lineNum} copied with ID tag.`, "color: cyan;");
                    currentIndex++;
                });
            }
        }
    });
})();