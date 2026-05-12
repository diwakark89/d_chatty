/**
 * API utilities for the PDF QA application
 */

const API = {
    // Base URL for API calls
    baseUrl: 'http://localhost:8000',

    // API endpoints
    endpoints: {
        // PDF QA endpoints
        upload: '/api/v1/pdf/upload',
        ask: '/api/v1/pdf/ask',
        status: '/status',  // Use non-prefixed status endpoint which is properly registered

        // File management endpoints
        files: '/api/v1/files/list',
        deleteFile: '/api/v1/files/delete',

        // Model management endpoints
        models: '/api/v1/models/list',
        modelInfo: '/api/v1/models/info',
        changeModel: '/api/v1/models/change'
    },

    /**
     * Get the system status
     * @returns {Promise<Object>} Status object
     */
    async getStatus() {
        try {
            // Add timeout to prevent hanging if the server is not responding
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

            console.log('Fetching status from:', `${this.baseUrl}${this.endpoints.status}`);

            const response = await fetch(`${this.baseUrl}${this.endpoints.status}`, {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            clearTimeout(timeoutId); // Clear the timeout if the request completes

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();
            console.log('Status response data:', data);

            // Validate essential fields
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }

            // Ensure we have at least the minimal fields needed
            return {
                status: data.status || 'ok',
                pdf_uploaded: !!data.pdf_uploaded,
                qa_chain_ready: !!data.qa_chain_ready,
                vector_store: data.vector_store || null,
                ollama_model: data.ollama_model || null,
                timestamp: data.timestamp || new Date().toISOString(),
                ...data // Keep all other fields too
            };
        } catch (error) {
            console.error('Error getting status:', error);
            // Return a minimal status object instead of throwing to prevent UI breakage
            if (error.name === 'AbortError') {
                return { 
                    status: 'error', 
                    error: 'Request timeout',
                    pdf_uploaded: false,
                    qa_chain_ready: false 
                };
            }
            return { 
                status: 'error', 
                error: error.message,
                pdf_uploaded: false,
                qa_chain_ready: false 
            };
        }
    },

    /**
     * Upload a PDF file
     * @param {File} file - The file to upload
     * @returns {Promise<Object>} Upload result
     */
    async uploadPDF(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.baseUrl}${this.endpoints.upload}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error uploading PDF:', error);
            throw error;
        }
    },

    /**
     * Ask a question about the uploaded PDF
     * @param {string} query - The question to ask
     * @param {string} [model] - Optional model name to use
     * @returns {Promise<Object>} Answer object
     */
    async askQuestion(query, model = null) {
        try {
            let url = `${this.baseUrl}${this.endpoints.ask}?query=${encodeURIComponent(query)}`;
            if (model) {
                url += `&model=${encodeURIComponent(model)}`;
            }
/**
 * API service for interacting with the backend
 */

const API = {
    // API endpoints
    endpoints: {
        // PDF operations
        uploadPDF: '/api/v1/pdf/upload',
        ask: '/api/v1/pdf/ask',
        status: '/status',  // Use non-prefixed status endpoint which is properly registered

        // File management endpoints
        files: '/api/v1/files/list',
        deleteFile: '/api/v1/files/delete',

        // Model management endpoints
        models: '/api/v1/models/list',
        modelInfo: '/api/v1/models/info',
        changeModel: '/api/v1/models/change'
    },

    /**
     * Get the system status
     * @returns {Promise<Object>} Status object
     */
    async getStatus() {
        try {
            // Add timeout to prevent hanging if the server is not responding
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(this.endpoints.status, {
                method: 'GET',
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`Status check failed: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting status:', error);
            // Return a default error status
            return {
                status: 'error',
                message: error.message,
                error: true
            };
        }
    },

    /**
     * Upload a PDF file
     * @param {File} file The PDF file to upload
     * @returns {Promise<Object>} Upload result
     */
    async uploadPDF(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(this.endpoints.uploadPDF, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage;
            try {
                // Try to parse as JSON
                const errorJson = JSON.parse(errorText);
                errorMessage = errorJson.detail || errorText;
            } catch {
                // If not JSON, use the text directly
                errorMessage = errorText;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    },

    /**
     * Ask a question about the uploaded PDF
     * @param {string} question The question to ask
     * @param {string|null} model Optional model to use
     * @returns {Promise<Object>} Answer object
     */
    async askQuestion(question, model = null) {
        let url = `${this.endpoints.ask}?query=${encodeURIComponent(question)}`;
        if (model) {
            url += `&model=${encodeURIComponent(model)}`;
        }

        const response = await fetch(url, {
            method: 'GET'
        });

        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage;
            try {
                // Try to parse as JSON
                const errorJson = JSON.parse(errorText);
                errorMessage = errorJson.detail || errorText;
            } catch {
                // If not JSON, use the text directly
                errorMessage = errorText;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    },

    /**
     * Get list of available models
     * @returns {Promise<Object>} Models list
     */
    async getModels() {
        try {
            const response = await fetch(this.endpoints.models, {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error(`Failed to get models: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting models:', error);
            // Return default models as fallback
            return {
                models: [
                    {name: 'mistral', modified_at: '', size: 0},
                    {name: 'phi3', modified_at: '', size: 0}
                ]
            };
        }
    },

    /**
     * Change the active model
     * @param {string} modelName The name of the model to use
     * @returns {Promise<Object>} Result of the change
     */
    async changeModel(modelName) {
        const response = await fetch(`${this.endpoints.changeModel}?model_name=${encodeURIComponent(modelName)}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage;
            try {
                const errorJson = JSON.parse(errorText);
                errorMessage = errorJson.detail || errorText;
            } catch {
                errorMessage = errorText;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    }
};

export default API;
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error asking question:', error);
            throw error;
        }
    },

    /**
     * Get list of available models
     * @returns {Promise<Object>} Models list
     */
    async getModels() {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.models}`);
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error getting models:', error);
            throw error;
        }
    },

    /**
     * Change the active model
     * @param {string} modelName - Name of the model to use
     * @returns {Promise<Object>} Result of model change
     */
    async changeModel(modelName) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.changeModel}?model_name=${encodeURIComponent(modelName)}`, {
                method: 'POST'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error changing model:', error);
            throw error;
        }
    },

    /**
     * Get list of uploaded files
     * @param {string} [type] - Optional file type filter
     * @returns {Promise<Object>} Files list
     */
    async getFiles(type = null) {
        try {
            let url = `${this.baseUrl}${this.endpoints.files}`;
            if (type) {
                url += `?type=${encodeURIComponent(type)}`;
            }

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error getting files:', error);
            throw error;
        }
    },

    /**
     * Delete a file
     * @param {string} filename - Name of the file to delete
     * @returns {Promise<Object>} Result of deletion
     */
    async deleteFile(filename) {
        try {
            const response = await fetch(`${this.baseUrl}${this.endpoints.deleteFile}/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error deleting file:', error);
            throw error;
        }
    }
};

// Export the API object
export default API;
