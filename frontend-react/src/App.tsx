import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import './App.css'

interface TaskFormData {
  task_type: string;
  prompt: string;
}

interface TaskFormProps {
  onSubmit: (data: TaskFormData) => void;
  isSubmitting: boolean;
}

interface InteractionRecord {
  id: number;
  request_id: string;
  timestamp: string;
  task_type: string;
  provider: string | null;
  status: string;
  latency_ms: number | null;
  // prompt and response_data can be large, so maybe not display all of it directly
}

interface ProviderStatusRecord {
  name: string;
  status: string; // "Active", "Disabled", "Error"
  details?: string;
}

function TaskForm({ onSubmit, isSubmitting }: TaskFormProps) {
  const [taskType, setTaskType] = useState<string>('default_llm_tasks');
  const [prompt, setPrompt] = useState<string>('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!taskType.trim() || !prompt.trim()) {
      alert('Task Type and Prompt cannot be empty.'); // Simple validation
      return;
    }
    onSubmit({ task_type: taskType, prompt });
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <div className="form-group">
        <label htmlFor="taskType">Task Type:</label>
        <input
          type="text"
          id="taskType"
          value={taskType}
          onChange={(e) => setTaskType(e.target.value)}
          placeholder="e.g., default_llm_tasks, echo"
          disabled={isSubmitting}
        />
      </div>
      <div className="form-group">
        <label htmlFor="prompt">Prompt:</label>
        <textarea
          id="prompt"
          rows={5}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt here..."
          disabled={isSubmitting}
        />
      </div>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit Task'}
      </button>
    </form>
  );
}

function App() {
  const [response, setResponse] = useState<any | null>(null); // Consider a more specific type for responseData
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [recentActivity, setRecentActivity] = useState<InteractionRecord[]>([]);
  const [systemStatus, setSystemStatus] = useState<ProviderStatusRecord[]>([]);

  const handleTaskSubmit = async (taskData: TaskFormData) => {
    setIsLoading(true);
    setResponse(null);
    setError(null);

    try {
      const apiResponse = await fetch('/api/v1/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });

      const responseData = await apiResponse.json();

      if (apiResponse.ok) {
        setResponse(responseData);
      } else {
        setError(responseData.detail || JSON.stringify(responseData, null, 2));
      }
    } catch (err: any) { // Catching 'any' for simplicity, can be more specific
      console.error('Error submitting task:', err);
      setError(`Network or application error: ${err.message}`);
    } finally {
      setIsLoading(false);
      // Optionally, refresh recent activity after a task submission
      fetchRecentActivity(); 
    }
  };

  const fetchRecentActivity = async () => {
    try {
      const apiResponse = await fetch('/api/v1/analytics?limit=5&offset=0'); // Fetch latest 5
      if (apiResponse.ok) {
        const data = await apiResponse.json();
        setRecentActivity(data.data || []);
      } else {
        console.error('Failed to fetch recent activity:', apiResponse.statusText);
        setRecentActivity([]); // Clear or handle error appropriately
      }
    } catch (err) {
      console.error('Error fetching recent activity:', err);
      setRecentActivity([]);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const apiResponse = await fetch('/api/v1/system-status');
      if (apiResponse.ok) {
        const data = await apiResponse.json();
        setSystemStatus(data.providers_status || []);
      } else {
        console.error('Failed to fetch system status:', apiResponse.statusText);
        setSystemStatus([{ name: "System Status", status: "Error", details: "Could not fetch status." }]);
      }
    } catch (err) {
      console.error('Error fetching system status:', err);
      setSystemStatus([{ name: "System Status", status: "Error", details: "Network error fetching status." }]);
    }
  };

  useEffect(() => {
    fetchRecentActivity();
    fetchSystemStatus();
  }, []);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Praximous Dashboard</h1>
      </header>
      <main className="dashboard-main">
        <section className="dashboard-section task-submission">
          <h2>Submit New Task</h2>
          <TaskForm onSubmit={handleTaskSubmit} isSubmitting={isLoading} />
          {isLoading && <p className="loading-message">Processing...</p>}
          {response && <div className="response-area success"><pre>{JSON.stringify(response, null, 2)}</pre></div>}
          {error && <div className="response-area error"><pre>{error}</pre></div>}
        </section>
        <section className="dashboard-section system-status">
          <h2>System Status</h2>
          {systemStatus.length > 0 ? (
            <ul className="status-list">
              {systemStatus.map((provider) => (
                <li key={provider.name} className={`status-item status-indicator-${provider.status.toLowerCase()}`}>
                  <span className="provider-name">{provider.name}:</span>
                  <span className="provider-status">{provider.status}</span>
                  {provider.details && <span className="provider-details">({provider.details})</span>}
                </li>
              ))}
            </ul>
          ) : (
            <p>Loading system status...</p>
          )}
        </section>
        <section className="dashboard-section recent-activity">
          <h2>Recent Activity</h2>
          {recentActivity.length > 0 ? (
            <ul className="activity-list">
              {recentActivity.map((activity) => (
                <li key={activity.id} className={`activity-item status-${activity.status.toLowerCase()}`}>
                  <span className="activity-timestamp">{new Date(activity.timestamp).toLocaleString()}</span>
                  <span className="activity-task">Task: {activity.task_type}</span>
                  <span className="activity-provider">Provider: {activity.provider || 'N/A'}</span>
                  <span className="activity-status">Status: {activity.status}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>No recent activity to display.</p>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
