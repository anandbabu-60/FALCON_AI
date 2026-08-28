export const isValidEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
export const isStrongPassword = (value: string) => value.length >= 8;
export const required = (value: string, label = 'This field') => value.trim() ? null : `${label} is required`;
export const validateProject = (payload: { title?: string; research_idea?: string; domain?: string }) => ({
  title: required(payload.title ?? '', 'Title'),
  research_idea: required(payload.research_idea ?? '', 'Research idea'),
  domain: required(payload.domain ?? '', 'Domain'),
});
