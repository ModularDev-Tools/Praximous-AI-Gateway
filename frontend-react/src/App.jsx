import React, { useState } from 'react';
import './App.css'; // We'll create this for basic styling

function TaskForm({ onSubmit, isSubmitting }) {
  const [taskType, setTaskType] = useState('default_llm_tasks');
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
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
          rows="5"
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
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleTaskSubmit = async (taskData) => {
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
    } catch (err) {
      console.error('Error submitting task:', err);
      setError(`Network or application error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

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
          <p>Status: All systems operational (Placeholder)</p>
        </section>
        <section className="dashboard-section recent-activity">
          <h2>Recent Activity</h2>
          <p>No recent activity to display (Placeholder - could fetch from /api/v1/analytics)</p>
        </section>
      </main>
    </div>
  );
}

export default App;