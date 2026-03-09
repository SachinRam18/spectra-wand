/**
 * SpectraWand API Service
 *
 * Connects the React frontend to the FastAPI backend
 * running on Colab via ngrok.
 *
 * ⚠️  Update API_URL every time you restart the Colab/ngrok session.
 */

const API_URL = ""; // now using Vite proxy in vite.config.js

/**
 * Send an image + prompt to the backend for AI color grading.
 *
 * @param {File}   file   - The image file to grade
 * @param {string} prompt - Color grading description
 * @returns {Promise<{image_base64: string, width: number, height: number, processing_time: number, prompt: string}>}
 */
export async function gradeImage(file, prompt) {
    const formData = new FormData();
    formData.append("image", file);        // backend expects field name "image"
    formData.append("prompt", prompt);
    // For color grading, we need a delicate balance:
    // strength=0.15 is too low (no change made)
    // strength=0.60 is too high (completely redraws the image/face)
    // Let's use 0.45 strength with a very strong ControlNet (0.90) to hold the structure
    formData.append("strength", "0.45");
    formData.append("controlnet_scale", "0.90");

    const res = await fetch(`${API_URL}/api/v1/grade`, {
        method: "POST",
        body: formData,
        headers: {
            // Required by ngrok free tier to bypass the browser warning page
            "ngrok-skip-browser-warning": "true",
        },
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error || err.detail || `Server error ${res.status}`);
    }

    return await res.json();
}

/**
 * Check backend health / connectivity.
 *
 * @returns {Promise<{status: string, version: string, models_loaded: boolean, gpu: object}>}
 */
export async function checkHealth() {
    const res = await fetch(`${API_URL}/api/v1/health`, {
        headers: { "ngrok-skip-browser-warning": "true" },
    });

    if (!res.ok) {
        throw new Error(`Health check failed: ${res.status}`);
    }

    return await res.json();
}
