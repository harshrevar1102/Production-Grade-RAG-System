const prisma = require("../config/prisma");

const createDocument = async ({
    userId,
    originalName,
    storedName,
    mimeType,
    fileSize,
    filePath
}) => {
    const document = await prisma.document.create({
        data: {
            userId,
            originalName,
            storedName,
            mimeType,
            fileSize,
            filePath,
            status: "UPLOADED"
        }
    });

    return document;
};

const getUserDocuments = async (userId) => {
    return prisma.document.findMany({
        where: {
            userId
        },
        orderBy: {
            createdAt: "desc"
        }
    });
};

const getDocumentById = async (documentId, userId) => {
    return prisma.document.findFirst({
        where: {
            id: documentId,
            userId
        }
    });
};

const deleteDocument = async (documentId, userId) => {
    return prisma.document.deleteMany({
        where: {
            id: documentId,
            userId
        }
    });
};

module.exports = {
    createDocument,
    getUserDocuments,
    getDocumentById,
    deleteDocument
};