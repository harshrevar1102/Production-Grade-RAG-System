const fs = require("fs");

const documentService = require("../services/document.service");

// ==========================================
// UPLOAD DOCUMENT
// ==========================================

const uploadDocument = async (req, res) => {
  try {
    if (!req.userId) {
      return res.status(401).json({
        message: "Unauthorized. Please login first.",
      });
    }

    if (!req.file) {
      return res.status(400).json({
        message: "No file uploaded",
      });
    }

    const document = await documentService.createDocument({
      userId: req.userId,

      originalName: req.file.originalname,
      storedName: req.file.filename,
      mimeType: req.file.mimetype,
      fileSize: req.file.size,
      filePath: req.file.path,
    });

    return res.status(201).json({
      message: "Document uploaded successfully",
      document,
    });
  } catch (error) {
    console.error("UPLOAD DOCUMENT ERROR:", error);

    if (req.file?.path && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    return res.status(500).json({
      message: "Failed to upload document",
    });
  }
};

// ==========================================
// GET USER DOCUMENTS
// ==========================================

const getDocuments = async (req, res) => {
  try {
    const documents = await documentService.getUserDocuments(
      req.userId
    );

    return res.status(200).json({
      documents,
    });
  } catch (error) {
    console.error("GET DOCUMENTS ERROR:", error);

    return res.status(500).json({
      message: "Failed to fetch documents",
    });
  }
};

// ==========================================
// GET SINGLE DOCUMENT
// ==========================================

const getDocument = async (req, res) => {
  try {
    const document = await documentService.getDocumentById(
      req.params.id,
      req.userId
    );

    if (!document) {
      return res.status(404).json({
        message: "Document not found",
      });
    }

    return res.status(200).json({
      document,
    });
  } catch (error) {
    console.error("GET DOCUMENT ERROR:", error);

    return res.status(500).json({
      message: "Failed to fetch document",
    });
  }
};

// ==========================================
// DELETE DOCUMENT
// ==========================================

const deleteDocument = async (req, res) => {
  try {
    const document = await documentService.getDocumentById(
      req.params.id,
      req.userId
    );

    if (!document) {
      return res.status(404).json({
        message: "Document not found",
      });
    }

    // Delete physical file
    if (document.filePath && fs.existsSync(document.filePath)) {
      fs.unlinkSync(document.filePath);
    }

    await documentService.deleteDocument(
      req.params.id,
      req.userId
    );

    return res.status(200).json({
      message: "Document deleted successfully",
    });
  } catch (error) {
    console.error("DELETE DOCUMENT ERROR:", error);

    return res.status(500).json({
      message: "Failed to delete document",
    });
  }
};

module.exports = {
  uploadDocument,
  getDocuments,
  getDocument,
  deleteDocument,
};