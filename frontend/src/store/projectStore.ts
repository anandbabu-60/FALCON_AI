const SELECTED_PROJECT_KEY = 'research_selected_project';
export const getSelectedProjectId = () => localStorage.getItem(SELECTED_PROJECT_KEY);
export const setSelectedProjectId = (projectId: string | null) => projectId ? localStorage.setItem(SELECTED_PROJECT_KEY, projectId) : localStorage.removeItem(SELECTED_PROJECT_KEY);
