export type Theme = 'light' | 'dark';
const THEME_KEY = 'research_theme';
export const getTheme = (): Theme => localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light';
export const setTheme = (theme: Theme) => { localStorage.setItem(THEME_KEY, theme); document.documentElement.dataset.theme = theme; };
export const toggleTheme = () => { const next = getTheme() === 'dark' ? 'light' : 'dark'; setTheme(next); return next; };
