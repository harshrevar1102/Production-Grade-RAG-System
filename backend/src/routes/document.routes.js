const express = require("express");

const router = express.Router();

const upload = require("../middleware/upload.middleware");
const authMiddleware = require("../middleware/auth.middleware");

const {
    uploadDocument,
    getDocuments,
    getDocument,
    deleteDocument
} = require("../controllers/document.controller");

// Upload document
router.post(
    "/upload",
    authMiddleware,
    upload.single("file"),
    uploadDocument
);

// Get all user's documents
router.get(
    "/",
    authMiddleware,
    getDocuments
);

// Get single document
router.get(
    "/:id",
    authMiddleware,
    getDocument
);

// Delete document
router.delete(
    "/:id",
    authMiddleware,
    deleteDocument
);

module.exports = router;