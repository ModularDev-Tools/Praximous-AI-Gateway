document.addEventListener('DOMContentLoaded', () => {
    const taskTypeInput = document.getElementById('taskType');
    const promptInput = document.getElementById('prompt');
    const submitButton = document.getElementById('submitTask');
    const responseArea = document.getElementById('responseArea');

    submitButton.addEventListener('click', async () => {
        const taskType = taskTypeInput.value.trim();
        const prompt = promptInput.value.trim();

        if (!taskType || !prompt) {
            responseArea.textContent = 'Error: Task Type and Prompt cannot be empty.';
            return;
        }

        // Clear previous response and set button to loading state
        responseArea.textContent = 'Processing...';
        responseArea.className = 'processing'; // For potential styling
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';

        try {
            const apiResponse = await fetch('/api/v1/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_type: taskType,
                    prompt: prompt,
                }),
            });

            const responseData = await apiResponse.json();

            if (apiResponse.ok) {
                responseArea.textContent = JSON.stringify(responseData, null, 2);
                responseArea.className = 'success'; // For potential styling
            } else {
                let errorMessage = `Error ${apiResponse.status}: `;
                if (responseData && responseData.detail) {
                    errorMessage += responseData.detail;
                } else if (responseData) {
                    errorMessage += JSON.stringify(responseData, null, 2);
                } else {
                    errorMessage += apiResponse.statusText || "Unknown error";
                }
                responseArea.textContent = errorMessage;
                responseArea.className = 'error'; // For potential styling
            }
        } catch (error) {
            console.error('Error submitting task:', error);
            responseArea.textContent = `Network or application error: ${error.message}`;
            responseArea.className = 'error'; // For potential styling
        }
        // Re-enable button
        submitButton.disabled = false;
        submitButton.textContent = 'Submit Task';
    });
});