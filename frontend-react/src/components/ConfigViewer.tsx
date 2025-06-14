import React, { useState, useEffect } from 'react';

const ConfigViewer: React.FC = () => {
  const [providersConfig, setProvidersConfig] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProvidersConfig = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const apiResponse = await fetch('/api/v1/config/providers');
        const responseText = await apiResponse.text(); // Expecting raw text

        if (!apiResponse.ok) {
          // Try to parse as JSON for FastAPI error detail, otherwise use text
          let errorDetail = `Failed to fetch provider config: ${apiResponse.status} ${apiResponse.statusText}`;
          try {
            const errorData = JSON.parse(responseText);
            errorDetail = errorData.detail || responseText;
          } catch (jsonError) {
            // If not JSON, responseText is already the detail
            errorDetail = responseText || errorDetail;
          }
          throw new Error(errorDetail);
        }
        setProvidersConfig(responseText);
      } catch (err: any) {
        setError(err.message);
        setProvidersConfig('');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProvidersConfig();
  }, []);

  if (isLoading) return <p>Loading provider configuration...</p>;
  if (error) return <p className="error-message">Error loading configuration: {error}</p>;

  return (
    <div className="config-viewer">
      <h4><code>config/providers.yaml</code></h4>
      {providersConfig ? (
        <pre className="config-content">{providersConfig}</pre>
      ) : (
        <p>No configuration content to display.</p>
      )}
      {/* Placeholder for ModelRouter rules if we decide to add it later */}
      {/* <h4>ModelRouter Rules (Conceptual)</h4> */}
      {/* <p>Displaying ModelRouter rules would require a dedicated backend endpoint and careful consideration of how rules are defined and exposed.</p> */}
    </div>
  );
};

export default ConfigViewer;