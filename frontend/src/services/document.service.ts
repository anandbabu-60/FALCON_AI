import { getDocumentText, listDocuments, uploadDocument } from '../api/documents.api';

export const fetchDocuments = (projectId: string, params?: Parameters<typeof listDocuments>[1]) => listDocuments(projectId, params).then((response) => response.data);
export const uploadResearchDocument = (projectId: string, file: File) => uploadDocument(projectId, file).then((response) => response.data);
export const readDocument = (projectId: string, documentId: string) => getDocumentText(projectId, documentId).then((response) => response.data);
