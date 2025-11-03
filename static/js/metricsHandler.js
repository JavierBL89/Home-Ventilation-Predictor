import { getBaseUrl } from './config.js';
/**
 * Metrics Handler JavaScript
 * Handles model metrics display, rating, and API interactions
 * Requires config.js to be loaded first for APP_CONFIG
 */

/**
 * Rate a metric value and return appropriate styling and rating
 * @param {number} value - The metric value to rate
 * @param {string} type - The type of metric ('r2', 'mape', etc.)
 * @returns {object} Object with rating text and CSS class
 */
function rateMetric(value, type) {
    switch(type) {
        case 'r2':
            if (value >= 0.8) return { rating: '🟢 Excellent', class: 'good-metric' };
            if (value >= 0.6) return { rating: '🟡 Good', class: 'average-metric' };
            if (value >= 0.4) return { rating: '🟠 Fair', class: 'average-metric' };
            return { rating: '🔴 Poor', class: 'poor-metric' };
        
        case 'mape':
            if (value <= 5) return { rating: '🟢 Excellent', class: 'good-metric' };
            if (value <= 10) return { rating: '🟡 Good', class: 'average-metric' };
            if (value <= 20) return { rating: '🟠 Fair', class: 'average-metric' };
            return { rating: '🔴 Poor', class: 'poor-metric' };
        
        default:
            return { rating: '-', class: '' };
    }
}

/**
 * Update individual model metrics in the UI
 * @param {string} model - Model name (arima, prophet, timesnet)
 * @param {object} metrics - Metrics data object
 */
function updateModelMetrics(model, metrics) {
    const prefix = model.toLowerCase();
    
    if (metrics.status === 'error') {
        // Show error message
        const errorElement = document.getElementById(`${prefix}Error`);
        const metricsElement = document.getElementById(`${prefix}Metrics`);
        
        if (errorElement) {
            errorElement.textContent = `Error: ${metrics.error}`;
            errorElement.style.display = 'block';
        }
        if (metricsElement) {
            metricsElement.style.display = 'none';
        }
        return;
    }

    // Hide error and show metrics
    const errorElement = document.getElementById(`${prefix}Error`);
    const metricsElement = document.getElementById(`${prefix}Metrics`);
    
    if (errorElement) errorElement.style.display = 'none';
    if (metricsElement) metricsElement.style.display = 'block';

    // Update individual metrics
    updateElementWithRating(`${prefix}-r2`, metrics.r2, 'r2');
    updateElementWithRating(`${prefix}-adj-r2`, metrics.adj_r2, 'r2');
    updateElement(`${prefix}-mae`, metrics.mae);
    updateElement(`${prefix}-rmse`, metrics.rmse);
    updateElementWithRating(`${prefix}-mape`, metrics.mape + '%', 'mape', metrics.mape);
    updateElement(`${prefix}-aic`, metrics.aic);
    updateElement(`${prefix}-sample`, metrics.sample_size);

    // Update comparison table
    updateComparisonTable(prefix, metrics);
}

/**
 * Update an element with rating styling
 * @param {string} elementId - Element ID to update
 * @param {string} displayValue - Value to display
 * @param {string} ratingType - Type for rating calculation
 * @param {number} actualValue - Actual numeric value for rating (if different from display)
 */
function updateElementWithRating(elementId, displayValue, ratingType, actualValue = null) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = displayValue;
        const rating = rateMetric(actualValue || parseFloat(displayValue), ratingType);
        element.className = 'metric-value ' + rating.class;
        
        // Update corresponding rating element if it exists
        const ratingElement = document.getElementById(elementId.replace('Value', 'Rating'));
        if (ratingElement) {
            ratingElement.innerHTML = rating.rating;
        }
    }
}

/**
 * Update a simple element with text content
 * @param {string} elementId - Element ID to update
 * @param {string|number} value - Value to display
 */
function updateElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Update comparison table row for a model
 * @param {string} prefix - Model prefix (arima, prophet, timesnet)
 * @param {object} metrics - Metrics data
 */
function updateComparisonTable(prefix, metrics) {
    updateElementWithRating(`comp-${prefix}-r2`, metrics.r2, 'r2');
    updateElement(`comp-${prefix}-mae`, metrics.mae);
    updateElement(`comp-${prefix}-rmse`, metrics.rmse);
    updateElementWithRating(`comp-${prefix}-mape`, metrics.mape + '%', 'mape', metrics.mape);
    
    const statusElement = document.getElementById(`comp-${prefix}-status`);
    if (statusElement) {
        statusElement.textContent = '✅ Active';
        statusElement.className = 'good-metric';
    }
}

/**
 * Update the main metrics table (for single model display)
 * @param {object} metrics - Metrics data object
 */
function updateMetrics(metrics) {
    updateElement('r2Value', metrics.r2);
    updateElement('adjR2Value', metrics.adj_r2);
    updateElement('maeValue', metrics.mae);
    updateElement('rmseValue', metrics.rmse);
    updateElement('mapeValue', metrics.mape + '%');
    updateElement('aicValue', metrics.aic);
    updateElement('bicValue', metrics.bic);
    updateElement('modelOrderValue', metrics.model_order);

    // Apply ratings
    const r2Rating = rateMetric(metrics.r2, 'r2');
    const r2Element = document.getElementById('r2Value');
    const r2RatingElement = document.getElementById('r2Rating');
    
    if (r2Element) r2Element.className = 'metric-value ' + r2Rating.class;
    if (r2RatingElement) r2RatingElement.innerHTML = r2Rating.rating;

    const adjR2Rating = rateMetric(metrics.adj_r2, 'r2');
    const adjR2Element = document.getElementById('adjR2Value');
    const adjR2RatingElement = document.getElementById('adjR2Rating');
    
    if (adjR2Element) adjR2Element.className = 'metric-value ' + adjR2Rating.class;
    if (adjR2RatingElement) adjR2RatingElement.innerHTML = adjR2Rating.rating;

    const mapeRating = rateMetric(metrics.mape, 'mape');
    const mapeElement = document.getElementById('mapeValue');
    const mapeRatingElement = document.getElementById('mapeRating');
    
    if (mapeElement) mapeElement.className = 'metric-value ' + mapeRating.class;
    if (mapeRatingElement) mapeRatingElement.innerHTML = mapeRating.rating;
}

/**
 * Fetch comprehensive metrics for all models
 * @returns {Promise<object>} Metrics data for all models
 */
async function getAllModelMetrics() {
    try {
        const response = await fetch(`${getBaseUrl()}/api/model_metrics`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch metrics');
        }
        
        return data;
    } catch (error) {
        console.error("Error fetching all model metrics:", error);
        throw error;
    }
}

/**
 * Fetch metrics for a specific model
 * @param {string} modelName - Name of the model (arima, prophet, timesnet)
 * @returns {Promise<object>} Metrics data for the specified model
 */
async function getSingleModelMetrics(modelName) {
    try {
        const response = await fetch(`${getBaseUrl()}/api/model_metrics/${modelName}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `Failed to fetch ${modelName} metrics`);
        }
        
        return data;
    } catch (error) {
        console.error(`Error fetching ${modelName} metrics:`, error);
        throw error;
    }
}

/**
 * Get the best performing model
 * @returns {Promise<object>} Best model data
 */
async function getBestModel() {
    try {
        const response = await fetch(`${getBaseUrl()}/api/best_model`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch best model');
        }
        
        return data;
    } catch (error) {
        console.error("Error fetching best model:", error);
        throw error;
    }
}

/**
 * Load metrics for a single selected model and update the first table
 */
async function loadSingleModelMetrics(modelName) {
    try {
        document.getElementById('statusText').textContent = 'Loading metrics...';
        
        const metrics = await getSingleModelMetrics(modelName);
        
        if (metrics.status === 'success') {
            updateMetrics(metrics);
            document.getElementById('statusText').textContent = `${metrics.model_name} metrics loaded`;
            document.getElementById('lastTrained').textContent = new Date().toLocaleString();
        } else {
            document.getElementById('statusText').textContent = `Error loading ${modelName} metrics`;
        }
        
    } catch (error) {
        console.error(`Error loading ${modelName} metrics:`, error);
        document.getElementById('statusText').textContent = `Failed to load ${modelName} metrics`;
    }
}

/**
 * Load all model metrics and update the UI
 */
async function loadMetrics() {
    try {
        document.getElementById('statusText').textContent = 'Loading all metrics...';

        const data = await getAllModelMetrics();

        // Update comparison table
        if (data.arima) updateModelMetrics('arima', data.arima);
        if (data.prophet) updateModelMetrics('prophet', data.prophet);
        if (data.timesnet) updateModelMetrics('timesnet', data.timesnet);

        // Update status
        document.getElementById('statusText').textContent = 'All metrics loaded successfully';
        document.getElementById('lastTrained').textContent = new Date().toLocaleString();

        // Also load the currently selected model in the first table
        const selectedModel = document.getElementById('modelType')?.value || 'arima';
        const modelData = data[selectedModel];
        if (modelData && modelData.status === 'success') {
            updateMetrics(modelData);
        }

    } catch (error) {
        console.error('Error loading metrics:', error);
        document.getElementById('statusText').textContent = 'Failed to load metrics: ' + error.message;
    }
}

/**
 * Initialize metrics functionality when DOM is loaded
 */
function initializeMetrics() {
    // Set up event listeners for your actual UI elements
    const evaluateModelBtn = document.getElementById('evaluateModel');
    const modelTypeSelect = document.getElementById('modelType');
    
    if (evaluateModelBtn) {
        evaluateModelBtn.addEventListener('click', async () => {
            document.getElementById('statusText').textContent = 'Loading metrics...';
            await loadMetrics();
        });
    }
    
    // Handle model selection change
    if (modelTypeSelect) {
        modelTypeSelect.addEventListener('change', async () => {
            const selectedModel = modelTypeSelect.value;
            await loadSingleModelMetrics(selectedModel);
        });
    }
    
    // Load metrics on page load
    loadMetrics();
}

/**
 * Handle model training (placeholder - replace with actual training logic)
 */
async function handleTrainModel() {
    const statusElement = document.getElementById('statusText');
    const lastTrainedElement = document.getElementById('lastTrained');
    
    if (statusElement) statusElement.textContent = 'Training...';
    
    try {
        // Replace with your actual training endpoint
        const modelType = document.getElementById('modelType')?.value || 'arima';
        
        const response = await fetch(`${getBaseUrl()}/train_arima`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_type: modelType })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Training failed');
        }
        
        // Update metrics if returned
        if (result.metrics) {
            updateMetrics(result.metrics);
        }
        
        // Update status
        if (statusElement) statusElement.textContent = 'Training completed';
        if (lastTrainedElement) lastTrainedElement.textContent = new Date().toLocaleString();
        
        // Show chart if available
        if (result.chart_path) {
            const chartPlaceholder = document.getElementById('chartPlaceholder');
            const forecastChart = document.getElementById('forecastChart');
            
            if (chartPlaceholder) chartPlaceholder.style.display = 'none';
            if (forecastChart) {
                forecastChart.src = result.chart_path;
                forecastChart.style.display = 'block';
            }
        }
        
    } catch (error) {
        console.error('Training failed:', error);
        if (statusElement) {
            statusElement.textContent = 'Training failed: ' + error.message;
        }
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMetrics);
} else {
    initializeMetrics();
}