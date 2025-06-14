import React, { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import type { FilterTaskType } from '../App'; // Import the interface
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

interface AnalyticsDashboardProps {
  availableTaskTypes: FilterTaskType[];
}

interface SortConfig {
  key: keyof InteractionRecord | null;
  direction: 'ascending' | 'descending';
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ availableTaskTypes }) => {
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
  const [selectedLog, setSelectedLog] = useState<InteractionRecord | null>(null);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'timestamp', direction: 'descending' }); // key can be keyof InteractionRecord

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
    if (sortConfig.key) {
      queryParams += `&sort_by=${sortConfig.key}`;
      queryParams += `&sort_order=${sortConfig.direction}`;
    }

    try {
      const apiResponse = await fetch(`/api/v1/analytics?${queryParams}`);
      const responseText = await apiResponse.text();

      if (!apiResponse.ok) {
        let errorDetail = `Failed to fetch analytics: ${apiResponse.status} ${apiResponse.statusText}`;
        try {
          // Attempt to parse error response as JSON
          const errorData = JSON.parse(responseText);
          errorDetail = errorData.detail || JSON.stringify(errorData);
        } catch (jsonError) {
          // If not JSON, use the response text or a generic message
          errorDetail = responseText || errorDetail;
        }
        throw new Error(errorDetail);
      }
      try {
        const data: AnalyticsData = JSON.parse(responseText);
        setAnalyticsData(data);
        setOffset(currentOffset); // Update offset if fetch was successful
      } catch (e) {
        console.error("Failed to parse analytics JSON:", responseText, e);
        throw new Error("Received analytics data is not valid JSON.");
      }
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
    // Also refetch if sortConfig changes
  }, [limit, sortConfig]); // Refetch if limit or sortConfig changes

  const handleFilterSubmit = (e: FormEvent) => {
    e.preventDefault();
    fetchAnalytics(0); // Reset to first page on new filter submission, will use current sortConfig
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

  const handleRowClick = (log: InteractionRecord) => {
    setSelectedLog(log);
  };

  const requestSort = (key: keyof InteractionRecord) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction }); // This will trigger useEffect to refetch with new sort params
  };

  return (
    <div className="analytics-dashboard">
      <h3>Filters</h3>
      <form onSubmit={handleFilterSubmit} className="analytics-filters">
        <div className="filter-group">
          <label htmlFor="taskTypeFilter">Task Type:</label>
          <select
            id="taskTypeFilter"
            value={taskTypeFilter}
            onChange={(e) => setTaskTypeFilter(e.target.value)}
          >
            <option value="">All Task Types</option>
            {availableTaskTypes.map(task => (
              <option key={task.value} value={task.value}>
                {task.name}
              </option>
            ))}
          </select>
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

      {isLoading && !analyticsData && <p>Loading analytics data...</p>} 
      {error && <p className="error-message">Error: {error}</p>}
      
      {(!isLoading || analyticsData) && ( // Show table structure even if loading new page
        <>
          {analyticsData && (
            <>
              <p>Showing {analyticsData.data.length} of {analyticsData.total_matches} records. Page {Math.floor(offset / limit) + 1}.</p>
              <div className="pagination-controls">
                <button onClick={handlePreviousPage} disabled={offset === 0 || isLoading}>Previous</button>
                <button onClick={handleNextPage} disabled={!analyticsData || (offset + limit >= analyticsData.total_matches) || isLoading}>Next</button>
              </div>
            </>
          )}
          <div className="analytics-table-container">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th onClick={() => requestSort('timestamp')} className="sortable-header">
                    Timestamp {sortConfig.key === 'timestamp' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
                  </th>
                  <th onClick={() => requestSort('task_type')} className="sortable-header">
                    Task Type {sortConfig.key === 'task_type' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
                  </th>
                  <th onClick={() => requestSort('provider')} className="sortable-header">
                    Provider {sortConfig.key === 'provider' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
                  </th>
                  <th onClick={() => requestSort('status')} className="sortable-header">
                    Status {sortConfig.key === 'status' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
                  </th>
                  <th onClick={() => requestSort('latency_ms')} className="sortable-header">
                    Latency (ms) {sortConfig.key === 'latency_ms' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
                  </th>
                  <th>Prompt (snippet)</th> {/* Not making prompt sortable for now */}
                </tr>
              </thead>
              <tbody>
                {/* Display data directly from analyticsData.data as it's now sorted by backend */}
                {isLoading && (!analyticsData || analyticsData.data.length === 0) && (
                  <tr><td colSpan={6} style={{ textAlign: 'center' }}>Loading data...</td></tr>
                )}
                {!isLoading && analyticsData && analyticsData.data.length === 0 && (
                  <tr><td colSpan={6} style={{ textAlign: 'center' }}>No records found for the selected filters.</td></tr>
                )}
                {analyticsData?.data.map((record) => (
                  <tr key={record.id} onClick={() => handleRowClick(record)} className="log-row-clickable">
                    <td>{new Date(record.timestamp).toLocaleString()}</td>
                    <td>{record.task_type}</td>
                    <td>{record.provider || 'N/A'}</td>
                    <td className={`status-${record.status.toLowerCase()}`}>{record.status}</td>
                    <td>{record.latency_ms ?? 'N/A'}</td>
                    <td title={record.prompt || ''}>{record.prompt ? record.prompt.substring(0, 50) + (record.prompt.length > 50 ? '...' : '') : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {selectedLog && (
        <div className="modal-overlay" onClick={() => setSelectedLog(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close-button" onClick={() => setSelectedLog(null)}>&times;</button>
            <h4>Log Details (ID: {selectedLog.request_id})</h4>
            <div className="log-detail-grid">
              <div className="log-detail-item"><strong>Timestamp:</strong> {new Date(selectedLog.timestamp).toLocaleString()}</div>
              <div className="log-detail-item"><strong>Task Type:</strong> {selectedLog.task_type}</div>
              <div className="log-detail-item"><strong>Provider:</strong> {selectedLog.provider || 'N/A'}</div>
              <div className="log-detail-item"><strong>Status:</strong> {selectedLog.status}</div>
              <div className="log-detail-item"><strong>Latency:</strong> {selectedLog.latency_ms ?? 'N/A'} ms</div>
            </div>
            <div className="log-detail-full">
              <strong>Prompt:</strong>
              <pre>{selectedLog.prompt || 'N/A'}</pre>
            </div>
            <div className="log-detail-full">
              <strong>Response Data:</strong>
              <pre>{selectedLog.response_data || 'N/A'}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;