import React, { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import TasksOverTimeChart from './TasksOverTimeChart';
import RequestsPerProviderChart from './RequestsPerProviderChart';
import AverageLatencyChart from './AverageLatencyChart';


interface InteractionRecord {
  id: number;
  request_id: string;
  timestamp: string;
  task_type: string;
  provider: string | null;
  status: string;
  latency_ms: number | null;
  prompt: string | null;
  response_data: string | null;
}

interface AnalyticsData {
  total_matches: number;
  limit: number;
  offset: number;
  data: InteractionRecord[];
}

const AnalyticsDashboard: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [limit, setLimit] = useState<number>(10);
  const [offset, setOffset] = useState<number>(0);
  const [taskTypeFilter, setTaskTypeFilter] = useState<string>('');
  // Placeholder for date filters - backend support would be needed
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const fetchAnalytics = async (currentOffset = offset) => {
    setIsLoading(true);
    setError(null);
    let queryParams = `limit=${limit}&offset=${currentOffset}`;
    if (taskTypeFilter) {
      queryParams += `&task_type=${encodeURIComponent(taskTypeFilter)}`;
    }
    if (startDate) {
      queryParams += `&start_date=${startDate}`;
    }
    if (endDate) {
      queryParams += `&end_date=${endDate}`;
    }

    try {
      const response = await fetch(`/api/v1/analytics?${queryParams}`);
      if (!response.ok) {
        let errorDetail = `Failed to fetch analytics: ${response.status} ${response.statusText}`;
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
      const data: AnalyticsData = await response.json();
      setAnalyticsData(data);
      setOffset(currentOffset); // Update offset if fetch was successful
    } catch (err: any) {
      console.error("Error fetching analytics:", err);
      setError(err.message);
      setAnalyticsData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics(0); // Fetch initial data with offset 0
  }, [limit]); // Refetch if limit changes

  const handleFilterSubmit = (e: FormEvent) => {
    e.preventDefault();
    fetchAnalytics(0); // Reset to first page on new filter submission
  };

  const handleNextPage = () => {
    if (analyticsData && (offset + limit < analyticsData.total_matches)) {
      fetchAnalytics(offset + limit);
    }
  };

  const handlePreviousPage = () => {
    if (offset - limit >= 0) {
      fetchAnalytics(offset - limit);
    }
  };

  return (
    <div className="analytics-dashboard">
      <h3>Filters</h3>
      <form onSubmit={handleFilterSubmit} className="analytics-filters">
        <div className="filter-group">
          <label htmlFor="taskTypeFilter">Task Type:</label>
          <input
            type="text"
            id="taskTypeFilter"
            value={taskTypeFilter}
            onChange={(e) => setTaskTypeFilter(e.target.value)}
            placeholder="e.g., echo, default_llm_tasks"
          />
        </div>
        <div className="filter-group">
          <label htmlFor="limit">Limit:</label>
          <input
            type="number"
            id="limit"
            value={limit}
            onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value, 10) || 10))}
            min="1"
          />
        </div>
        {/* Placeholder Date Filters */}
        <div className="filter-group">
          <label htmlFor="startDate">Start Date:</label>
          <input type="date" id="startDate" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </div>
        <div className="filter-group">
          <label htmlFor="endDate">End Date:</label>
          <input type="date" id="endDate" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </div>
        <button type="submit" disabled={isLoading}>Apply Filters</button>
      </form>

      <div className="charts-container">
        <div className="chart-wrapper">
          <h4>Tasks Over Time</h4>
          <TasksOverTimeChart startDate={startDate} endDate={endDate} />
        </div>
        <div className="chart-wrapper">
          <h4>Requests Per Provider</h4>
          <RequestsPerProviderChart startDate={startDate} endDate={endDate} />
        </div>
        <div className="chart-wrapper">
          <h4>Average Latency Per Provider (ms)</h4>
          <AverageLatencyChart startDate={startDate} endDate={endDate} />
        </div>
      </div>

      {isLoading && <p>Loading analytics data...</p>}
      {error && <p className="error-message">Error: {error}</p>}
      
      {analyticsData && (
        <>
          <p>Showing {analyticsData.data.length} of {analyticsData.total_matches} records. Page {Math.floor(offset / limit) + 1}.</p>
          <div className="pagination-controls">
            <button onClick={handlePreviousPage} disabled={offset === 0 || isLoading}>Previous</button>
            <button onClick={handleNextPage} disabled={!analyticsData || (offset + limit >= analyticsData.total_matches) || isLoading}>Next</button>
          </div>
          <div className="analytics-table-container">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Task Type</th>
                  <th>Provider</th>
                  <th>Status</th>
                  <th>Latency (ms)</th>
                  <th>Prompt (snippet)</th>
                </tr>
              </thead>
              <tbody>
                {analyticsData.data.map((record) => (
                  <tr key={record.id}>
                    <td>{new Date(record.timestamp).toLocaleString()}</td>
                    <td>{record.task_type}</td>
                    <td>{record.provider || 'N/A'}</td>
                    <td className={`status-${record.status.toLowerCase()}`}>{record.status}</td>
                    <td>{record.latency_ms ?? 'N/A'}</td>
                    <td>{record.prompt ? record.prompt.substring(0, 50) + (record.prompt.length > 50 ? '...' : '') : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default AnalyticsDashboard;