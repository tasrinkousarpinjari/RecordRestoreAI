
const API_BASE_URL = "https://recordrestoreai.onrender.com";

const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const restoreBtn = document.getElementById("restoreBtn");
const statusText = document.getElementById("status");

let selectedFile = null;

imageInput.addEventListener("change", function () {
    selectedFile = this.files[0];

    if (!selectedFile) return;

    if (!["image/png", "image/jpeg"].includes(selectedFile.type)) {
        statusText.textContent = "Please select JPG or PNG.";
        selectedFile = null;
        return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
        statusText.textContent = "Maximum image size is 10 MB.";
        selectedFile = null;
        return;
    }

    preview.src = URL.createObjectURL(selectedFile);
    preview.style.display = "block";
    statusText.textContent = "Image selected successfully.";
});

restoreBtn.addEventListener("click", async function () {
    if (!selectedFile) {
        statusText.textContent = "Please upload an image first.";
        return;
    }

    const formData = new FormData();
    formData.append("image", selectedFile);

    restoreBtn.disabled = true;
    statusText.textContent = "Restoring your document...";

    try {
        const response = await fetch(`${API_BASE_URL}/api/restore`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Restoration failed.");
        }

        document.getElementById("originalResult").src =
            new URL(data.original, API_BASE_URL).href;

        document.getElementById("restoredResult").src =
            new URL(data.restored, API_BASE_URL).href;

        document.getElementById("downloadBtn").href =
            new URL(data.restored, API_BASE_URL).href;

        document.getElementById("results").style.display = "block";
        statusText.textContent = data.message;

        document.getElementById("results").scrollIntoView({
            behavior: "smooth"
        });

    } catch (error) {
        statusText.textContent = error.message;
    } finally {
        restoreBtn.disabled = false;
    }
});
