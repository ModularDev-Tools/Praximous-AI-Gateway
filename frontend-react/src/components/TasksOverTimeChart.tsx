import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TasksOverTimeProps {
  startDate?: string;
  endDate?: string;
  granularity?: 'day' | 'month' | 'year';
}

interface ChartDataPoint {
  date_group: string;
  count: number;
}

const TasksOverTimeChart: React.FC<TasksOverTimeProps> = ({ startDate, endDate, granularity = 'day' }) => {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      let queryParams = `granularity=${granularity}`;
      if (startDate) queryParams += `&start_date=${startDate}`;
      if (endDate) queryParams += `&end_date=${endDate}`;

      try {
        const response = await fetch(`/api/v1/analytics/charts/tasks-over-time?${queryParams}`);
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || `Failed to fetch tasks over time data: ${response.statusText}`);
        }
        const result: ChartDataPoint[] = await response.json();
        setData(result);
      } catch (err: any) {
        setError(err.message);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, granularity]);

  if (loading) return <p>Loading chart data...</p>;
  if (error) return <p className="error-message">Error loading chart: {error}</p>;
  if (data.length === 0) return <p>No data available for the selected period.</p>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date_group" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="count" stroke="#8884d8" activeDot={{ r: 8 }} name="Tasks" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TasksOverTimeChart;