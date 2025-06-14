import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface RequestsPerProviderProps {
  startDate?: string;
  endDate?: string;
}

interface ChartDataPoint {
  provider_name: string;
  count: number;
}

const RequestsPerProviderChart: React.FC<RequestsPerProviderProps> = ({ startDate, endDate }) => {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      let queryParams = "";
      if (startDate) queryParams += `start_date=${startDate}`;
      if (endDate) queryParams += `${queryParams ? '&' : ''}end_date=${endDate}`;

      try {
        const response = await fetch(`/api/v1/analytics/charts/requests-per-provider${queryParams ? '?' + queryParams : ''}`);
        if (!response.ok) {
          let errorDetail = `Failed to fetch requests per provider data: ${response.status} ${response.statusText}`;
          try {
            // Attempt to parse error response as JSON
            const errorData = await response.json();
            errorDetail = errorData.detail || JSON.stringify(errorData);
          } catch (jsonError) {
            // If not JSON, use the response text or a generic message
            errorDetail = await response.text() || errorDetail;
          }
          throw new Error(errorDetail);
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
  }, [startDate, endDate]);

  if (loading) return <p>Loading chart data...</p>;
  if (error) return <p className="error-message">Error loading chart: {error}</p>;
  if (data.length === 0) return <p>No data available for the selected period.</p>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="provider_name" />
        <YAxis allowDecimals={false}/>
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#82ca9d" name="Requests" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default RequestsPerProviderChart;