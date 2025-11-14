import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { TimeseriesDataPoint } from '../types';
import { formatDate } from '../utils/dateFormat';
import { getChartColor } from '../utils/chartColors';

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
  onClick?: (timestamp: string) => void;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  data,
  title,
  height = 300,
  showPoints = true,
  fill = false,
  onClick,
}) => {
  const chartData = {
    labels: data.map(d => formatDate(d.timestamp, 'MMM dd')),
    datasets: [
      {
        label: 'Events',
        data: data.map(d => d.count),
        borderColor: getChartColor(0),
        backgroundColor: fill ? `${getChartColor(0)}33` : getChartColor(0),
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
    onClick: (event: any, elements: any[]) => {
      if (onClick && elements.length > 0) {
        const index = elements[0].index;
        onClick(data[index].timestamp);
      }
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
        backgroundColor: '#1a1a1a',
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        borderColor: getChartColor(0),
        borderWidth: 1,
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
