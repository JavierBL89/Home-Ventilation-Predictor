async function displayModelMetrics() {
    try {
        const metrics = await getAllModelMetrics();
        
        // Build a table
        let metricsHTML = `
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>MAE</th>
                        <th>MSE</th>
                        <th>RMSE</th>
                        <th>R²</th>
                        <th>Adj. R²</th>
                        <th>MAPE (%)</th>
                        <th>AIC</th>
                        <th>BIC</th>
                        <th>Sample Size</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        ["arima", "prophet", "timesnet"].forEach(model => {
            const m = metrics[model];
            if (!m) return;

            metricsHTML += `
                <tr>
                    <td>${m.model_name}</td>
                    <td>${m.mae ?? "-"}</td>
                    <td>${m.mse ?? "-"}</td>
                    <td>${m.rmse ?? "-"}</td>
                    <td class="${rateMetric(m.r2, 'r2')}">${m.r2 ?? "-"}</td>
                    <td>${m.adj_r2 ?? "-"}</td>
                    <td class="${rateMetric(m.mape, 'mape')}">${m.mape ?? "-"}</td>
                    <td>${m.aic ?? "-"}</td>
                    <td>${m.bic ?? "-"}</td>
                    <td>${m.sample_size ?? "-"}</td>
                    <td class="${m.status === 'success' ? 'status-success' : 'status-error'}">
                        ${m.status}
                    </td>
                </tr>
            `;
        });

        metricsHTML += `
                </tbody>
            </table>
        `;

        return metricsHTML;
    } catch (error) {
        return `<div class="error">📊 Error loading metrics: ${error.message}</div>`;
    }
}
