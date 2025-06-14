import SkillLibrary from './SkillLibrary';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';

// Mock global.fetch with improved typing
const mockFetch = jest.fn() as jest.MockedFunction<typeof fetch>;
globalThis.fetch = mockFetch; // Use globalThis for broader compatibility

const mockSkillsData = {
  echo: {
    skill_name: "Echo Skill",
    description: "A simple skill that echoes back the provided prompt.",
    operations: {
      echo_operation: {
        description: "Returns the input prompt verbatim.",
        parameters_schema: { prompt: { type: "string", description: "The text to be echoed." } },
        example_request_payload: { task_type: "echo", prompt: "Hello Praximous!" },
      },
    },
  },
  text_manipulation: {
    skill_name: "Text Manipulation Skill",
    description: "Performs various text manipulation operations.",
    operations: {
      manipulate: {
        description: "Applies a specified manipulation to the input text.",
        parameters_schema: {
          prompt: { type: "string", description: "The text to be manipulated." },
          operation: { type: "string", enum: ["uppercase", "lowercase"], description: "The manipulation to perform." },
        },
      },
    },
  },
};

describe('SkillLibrary Component', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    mockFetch.mockClear();
  });

  test('renders loading state initially', () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(JSON.stringify({})),
      json: () => Promise.resolve({}), // Added for completeness
    } as Response); // Cast to Response
    render(<SkillLibrary />);
    expect(screen.getByText(/loading skill library.../i)).toBeInTheDocument();
  });

  test('renders skill names after successful data fetch', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(JSON.stringify(mockSkillsData)),
      json: () => Promise.resolve(mockSkillsData), // Added for completeness
    } as Response); // Cast to Response

    render(<SkillLibrary />);

    // Wait for skill names to appear
    await waitFor(() => {
      expect(screen.getByText(/Echo Skill/i)).toBeInTheDocument();
      expect(screen.getByText(/Text Manipulation Skill/i)).toBeInTheDocument();
    });

    // Check that loading state is gone
    expect(screen.queryByText(/loading skill library.../i)).not.toBeInTheDocument();
  });

  test('displays an error message if fetching skills fails', async () => {
    const errorMessage = 'Network Error';
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      text: () => Promise.resolve(errorMessage),
      json: () => Promise.resolve({ detail: errorMessage }), // Mock a potential JSON error structure
    } as Response); // Cast to Response

    render(<SkillLibrary />);

    await waitFor(() => {
      // The component prepends "Error loading skills: " to the error message from fetch
      expect(screen.getByText(new RegExp(`Error loading skills: ${errorMessage}`, "i"))).toBeInTheDocument();
    });
  });

  test('displays "No skills found" message when API returns empty data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(JSON.stringify({})), // Empty skills object
      json: () => Promise.resolve({}), // Added for completeness
    } as Response); // Cast to Response

    render(<SkillLibrary />);

    await waitFor(() => {
      expect(screen.getByText(/No skills found or registered./i)).toBeInTheDocument();
    });
  });

  // Future tests could include:
  // - Clicking a skill to expand and see details
  // - Verifying operation details are rendered correctly
});
