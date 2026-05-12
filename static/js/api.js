/**
 * API utilities for the PDF QA application.
 */

const API = {
  baseUrl: window.location.origin,

  endpoints: {
    upload: "/api/v1/pdf/upload",
    ask: "/api/v1/pdf/ask",
    status: "/status",
    files: "/api/v1/files/list",
    deleteFile: "/api/v1/files/delete",
    models: "/api/v1/models/list",
    modelInfo: "/api/v1/models/info",
    changeModel: "/api/v1/models/change",
  },

  async request(path, options = {}) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });

    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const payload = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const detail =
        typeof payload === "object" && payload !== null
          ? payload.detail || payload.message
          : payload;
      const error = new Error(detail || `HTTP error: ${response.status}`);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }

    return payload;
  },

  async getStatus() {
    try {
      return await this.request(this.endpoints.status, { method: "GET" });
    } catch (error) {
      return {
        status: "error",
        error: error.message,
        pdf_uploaded: false,
        qa_chain_ready: false,
      };
    }
  },

  async uploadPDF(file) {
    const formData = new FormData();
    formData.append("file", file);

    return this.request(this.endpoints.upload, {
      method: "POST",
      body: formData,
      headers: {},
    });
  },

  async askQuestion(query, model = null) {
    let url = `${this.endpoints.ask}?query=${encodeURIComponent(query)}`;
    if (model) {
      url += `&model=${encodeURIComponent(model)}`;
    }

    return this.request(url, { method: "GET" });
  },

  async getModels() {
    return this.request(this.endpoints.models, { method: "GET" });
  },

  async getModelInfo(modelName) {
    return this.request(
      `${this.endpoints.modelInfo}/${encodeURIComponent(modelName)}`,
      {
        method: "GET",
      },
    );
  },

  async changeModel(modelName) {
    return this.request(
      `${this.endpoints.changeModel}?model_name=${encodeURIComponent(modelName)}`,
      {
        method: "POST",
      },
    );
  },

  async getFiles(type = null) {
    let url = this.endpoints.files;
    if (type) {
      url += `?type=${encodeURIComponent(type)}`;
    }
    return this.request(url, { method: "GET" });
  },

  async deleteFile(filename) {
    return this.request(
      `${this.endpoints.deleteFile}/${encodeURIComponent(filename)}`,
      {
        method: "DELETE",
      },
    );
  },
};

export default API;
