import {
    CategoryScale,
    Chart as ChartJS,
    Filler,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Title,
    Tooltip,
} from 'chart.js';
import React from 'react';
import { Line } from 'react-chartjs-2';
import type { TimeseriesDataPoint } from '../types';
import { getChartColor } from '../utils/chartColors';
import { formatDate } from '../utils/dateFormat';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

interface TimeSeriesChartProps {
    data: TimeseriesDataPoint[];
    title?: string;
    height?: number;
    showPoints?: boolean;
    fill?: boolean;
    color?: string;
    onClick?: (timestamp: string) => void;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
    data,
    title,
    height = 300,
    showPoints = true,
    fill = false,
    color,
    onClick,
}) => {
    const lineColor = color || getChartColor(0);
    const chartData = {
        labels: data.map(d => formatDate(d.timestamp, 'MMM dd')),
        datasets: [
            {
                label: 'Events',
                data: data.map(d => d.count),
                borderColor: lineColor,
                backgroundColor: fill ? `${lineColor}33` : lineColor,
                tension: 0.3,
                pointRadius: showPoints ? 4 : 0,
                pointHoverRadius: 6,
                fill: fill,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (_event: any, elements: any[]) => {
            if (onClick && elements.length > 0) {
                const index = elements[0].index;
                onClick(data[index].timestamp);
            }
        },
        interaction: {
            mode: 'index' as const,
            intersect: false,
        },
        hover: {
            mode: 'index' as const,
            intersect: false,
        },
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: !!title,
                text: title,
                color: '#FFFFFF',
                font: {
                    size: 16,
                },
            },
            tooltip: {
                enabled: true,
                backgroundColor: '#1a1a1a',
                titleColor: '#FFFFFF',
                bodyColor: '#FFFFFF',
                borderColor: lineColor,
                borderWidth: 1,
                displayColors: false,
                callbacks: {
                    label: (ctx: any) => `${ctx.parsed.y} incidents`,
                },
            },
        },
        scales: {
            x: {
                grid: {
                    color: '#333333',
                },
                ticks: {
                    color: '#AAAAAA',
                },
            },
            y: {
                grid: {
                    color: '#333333',
                },
                ticks: {
                    color: '#AAAAAA',
                },
                beginAtZero: true,
            },
        },
    };

    return (
        <div style={{ height }}>
            <Line data={chartData} options={options} />
        </div>
    );
};

export default TimeSeriesChart;
