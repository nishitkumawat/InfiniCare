/**
 * Dashboard functionality for the Digital Farming platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any dashboard-specific functionality here
    
    // Example: Add responsive behavior to tables
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
    
    // Example: Add click event to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        card.addEventListener('click', function() {
            if (this.dataset.href) {
                window.location.href = this.dataset.href;
            }
        });
    });
    
    // Function to initialize custom date range picker if present
    if (document.getElementById('dateRangePicker')) {
        initDateRangePicker();
    }
    
    // Function to update dashboard stats dynamically if needed
    function updateDashboardStats() {
        // This would fetch updated stats from server in a real implementation
        console.log('Dashboard stats updated');
    }
    
    // Date range picker initialization
    function initDateRangePicker() {
        const dateRangePicker = document.getElementById('dateRangePicker');
        const dateRangeForm = document.getElementById('dateRangeForm');
        
        if (dateRangeForm) {
            dateRangeForm.addEventListener('submit', function(e) {
                e.preventDefault();
                updateDashboardStats();
            });
        }
    }
    
    // Custom chart tooltips formatting if needed
    function customTooltips(tooltip) {
        // Implementation would depend on Chart.js version and requirements
    }
    
    // Add export functionality for charts
    const exportButtons = document.querySelectorAll('.btn-export');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.dataset.chartId;
            const chartCanvas = document.getElementById(chartId);
            
            if (chartCanvas) {
                // Create an image from the chart canvas
                const image = chartCanvas.toDataURL('image/png');
                
                // Create download link
                const downloadLink = document.createElement('a');
                downloadLink.href = image;
                downloadLink.download = `${chartId}_export.png`;
                downloadLink.click();
            }
        });
    });
});
