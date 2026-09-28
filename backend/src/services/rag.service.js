const axios = require("axios");

const RAG_SERVICE_URL =
  process.env.RAG_SERVICE_URL || "http://localhost:8000";


/**
 * Send a question to the RAG service.
 */
const askDocument = async ({
  documentId,
  query,
  topK = 5
}) => {

  try {

    const response = await axios.post(
      `${RAG_SERVICE_URL}/api/rag/ask`,
      {
        document_id: documentId,
        query,
        top_k: topK
      },
      {
        timeout: 120000
      }
    );

    return response.data;

  } catch (error) {

    console.error(
      "RAG Service Error:",
      error.response?.data || error.message
    );

    throw new Error(
      "RAG service is currently unavailable."
    );
  }
};


module.exports = {
  askDocument
};