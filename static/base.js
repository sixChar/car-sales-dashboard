
function resize_chart(chartId) {
    const chart = document.getElementById(chartId);
    const chartHolder = document.getElementById(chartId + "-holder");
    chart.width = chartHolder.clientWidth;    
    chart.height = chartHolder.clientHeight;    
}

window.onload = () => {
    resize_chart(salesChart, salesChartHolder);
    resize_chart(unitChart, unitChartHolder);
    resize_chart(typeChart);
    resize_chart(originChart);
}











