import React, { useState, useEffect } from 'react';

// Define interfaces based on the expected structure from /api/v1/skills
interface ParameterSchema {
  type: string;
  description?: string;
  enum?: string[];
}

interface OperationDetails {
  description: string;
  parameters_schema: Record<string, ParameterSchema>;
  example_request_payload?: Record<string, any>;
}

interface SkillDefinition {
  skill_name: string;
  description: string;
  operations: Record<string, OperationDetails>;
  error?: string; // In case fetching capabilities for a specific skill failed
}

type SkillsApiResponse = Record<string, SkillDefinition>;

const SkillLibrary: React.FC = () => {
  const [skills, setSkills] = useState<SkillsApiResponse>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSkill, setExpandedSkill] = useState<string | null>(null);

  useEffect(() => {
    const fetchSkillsData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const apiResponse = await fetch('/api/v1/skills');
        const responseText = await apiResponse.text();

        if (!apiResponse.ok) {
          let errorDetail = `Failed to fetch skills: ${apiResponse.status} ${apiResponse.statusText}`;
          try {
            const errorData = JSON.parse(responseText);
            errorDetail = errorData.detail || JSON.stringify(errorData);
          } catch (jsonError) {
            errorDetail = responseText || errorDetail;
          }
          throw new Error(errorDetail);
        }
        try {
          const data: SkillsApiResponse = JSON.parse(responseText);
          setSkills(data);
        } catch (e) {
          console.error("Failed to parse skills JSON:", responseText, e);
          throw new Error("Received skills data is not valid JSON.");
        }
      } catch (err: any) {
        setError(err.message);
        setSkills({});
      } finally {
        setIsLoading(false);
      }
    };

    fetchSkillsData();
  }, []);

  const toggleSkillExpansion = (skillKey: string) => {
    setExpandedSkill(expandedSkill === skillKey ? null : skillKey);
  };

  if (isLoading) return <p>Loading skill library...</p>;
  if (error) return <p className="error-message">Error loading skills: {error}</p>;
  if (Object.keys(skills).length === 0) return <p>No skills found or registered.</p>;

  return (
    <div className="skill-library">
      {Object.entries(skills).map(([skillKey, skillDef]) => (
        <div key={skillKey} className="skill-card">
          <h3 onClick={() => toggleSkillExpansion(skillKey)} style={{ cursor: 'pointer' }}>
            {skillDef.skill_name || skillKey} {expandedSkill === skillKey ? '▼' : '►'}
          </h3>
          {skillDef.error && <p className="error-message">Error loading details: {skillDef.error}</p>}
          {expandedSkill === skillKey && !skillDef.error && (
            <div className="skill-details">
              <p><strong>Description:</strong> {skillDef.description}</p>
              <h4>Operations:</h4>
              {Object.entries(skillDef.operations).map(([opKey, opDetails]) => (
                <div key={opKey} className="operation-details">
                  <h5>{opKey}</h5>
                  <p>{opDetails.description}</p>
                  {opDetails.parameters_schema && Object.keys(opDetails.parameters_schema).length > 0 && (
                    <>
                      <strong>Parameters:</strong>
                      <ul>
                        {Object.entries(opDetails.parameters_schema).map(([paramKey, paramSchema]) => (
                          <li key={paramKey}>
                            <code>{paramKey}</code> (type: {paramSchema.type})
                            {paramSchema.description && `: ${paramSchema.description}`}
                            {paramSchema.enum && ` (options: ${paramSchema.enum.join(', ')})`}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                  {opDetails.example_request_payload && (
                    <div className="example-payload"><strong>Example Request:</strong> <pre>{JSON.stringify(opDetails.example_request_payload, null, 2)}</pre></div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default SkillLibrary;