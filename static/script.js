// Handles image preview and form interaction
document.getElementById('photo-input').addEventListener('change', function (e) {
    const preview = document.getElementById('photo-preview');
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (evt) {
            preview.src = evt.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        preview.src = '';
        preview.style.display = 'none';
    }
});

// Simple loader animation
function showLoader(text) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<div class="loader-heart"></div><div style="margin-top:0.7em;">${text}</div>`;
}

document.getElementById('upload-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('photo-input');
    const resultDiv = document.getElementById('result');
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = "Please select a photo first.";
        return;
    }

    showLoader("Analyzing your beauty...");

    const formData = new FormData();
    formData.append('photo', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.success) {
            // Show ratios and harmony score
            let html = `<div class="score-block"><h2>Your Golden Harmony Score: <span class="score">${(data.harmony_score*100).toFixed(0)}/100</span></h2></div>`;
            html += `<ul class="ratios">`;
            data.ratios.forEach(r => {
                html += `<li><strong>${r.name}:</strong> <span>${r.value}</span> (Score: <span>${(r.score*100).toFixed(0)}/100</span>)</li>`;
            });
            html += `</ul>`;

            // Poetic result message
            let message = "";
            let cheerType = "";
            if (data.harmony_score >= 0.8) {
                message = "Your facial proportions echo nature’s perfect harmony. You are breathtaking. ✨";
                cheerType = "confetti";
            } else if (data.harmony_score >= 0.6) {
                message = "You radiate a natural charm that transcends symmetry. The beauty of your face is unique and deeply enchanting. 💖";
                cheerType = "cheerup";
            } else {
                message = "True beauty lies in uniqueness, and your face tells a story only you can tell. You are beautiful, inside and out. 🌸";
                cheerType = "cheerup";
            }
            html += `<div class="romantic-message">${message}</div>`;

            // Show landmarked image if available
            if (data.landmarked_img) {
                html += `<div class="landmark-preview"><img src="/uploads/${data.landmarked_img}" alt="Landmarked Face" style="max-width: 98%; border-radius: 14px; margin-top: 1em; box-shadow: 0 2px 14px #eee;"></div>`;
            }

            // Add a cheer animation container
            html += `<div id="cheer-animation"></div>`;

            resultDiv.innerHTML = html;

            // Launch animation
            if (cheerType === "confetti") {
                // Confetti burst
                confetti({
                    particleCount: 150,
                    spread: 80,
                    origin: { y: 0.7 },
                    colors: ['#ff7eb9', '#fff740', '#a0e426', '#40c9ff', '#f9f871']
                });
                confetti({
                    particleCount: 100,
                    spread: 160,
                    origin: { y: 0.5 },
                    colors: ['#e05fa0', '#a36fff', '#fbc2eb', '#f68084'],
                    scalar: 1.2
                });
            } else if (cheerType === "cheerup") {
                // Cheer up animation (bouncing emoji hearts/stars)
                const cheerDiv = document.getElementById('cheer-animation');
                cheerDiv.innerHTML = `
                    <div class="cheerup-emoji">
                        <span>💖</span>
                        <span>🌟</span>
                        <span>💞</span>
                        <span>✨</span>
                        <span>🌸</span>
                    </div>
                `;
                setTimeout(() => {
                    cheerDiv.innerHTML = '';
                }, 3000);
            }
        } else {
            resultDiv.innerHTML = "Analysis failed: " + (data.error || "Unknown error");
        }
    } catch (err) {
        resultDiv.innerHTML = "An error occurred: " + err.message;
    }
});

