/**
 * Application Configuration
 * Centralized configuration for all JavaScript files
 */
const APP_CONFIG = {
    DEV: false, // Set to false for production
    LOCAL_URL: "http://127.0.0.1:5001",
    PROD_URL: "https://home-ventilation-predictor.onrender.com"
};

/**
 * Get the base URL for API calls based on DEV flag
 */
function getBaseUrl() {
    return APP_CONFIG.DEV ? APP_CONFIG.LOCAL_URL : APP_CONFIG.PROD_URL;
}