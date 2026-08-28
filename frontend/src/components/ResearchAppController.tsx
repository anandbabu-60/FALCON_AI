import { useEffect } from 'react';
import ResearchApp from './ResearchApp';

const researchPrompt = 'Analyze my plant disease detection research and identify the most important evidence gaps.';

export default function ResearchAppController() {
  useEffect(() => {
    const openCopilot = () => {
      window.setTimeout(() => {
        const input = document.querySelector<HTMLInputElement>('.chat-input input');
        if (!input) return;
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
        setter?.call(input, researchPrompt);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.focus();
        window.setTimeout(() => document.querySelector<HTMLButtonElement>('.chat-input button')?.click(), 80);
      }, 120);
    };

    const handleClick = (event: Event) => {
      const target = event.target as HTMLElement;
      if (target.closest('.ai-fab')) openCopilot();
    };
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, []);

  return <ResearchApp />;
}
