export const demoProject = {
  title: 'Early detection of plant diseases with computer vision',
  domain: 'Computer Vision / Agriculture',
  status: 'AI analysis in progress',
  objective: 'Detect foliar disease before visible symptoms spread across a crop.',
  progress: 68,
};

export const metrics = [
  ['Active projects', '03', '+1 this month'],
  ['Papers analyzed', '128', '+24 this week'],
  ['Research gaps', '07', '3 high confidence'],
  ['Datasets found', '19', '+6 recommended'],
];

export const papers = [
  { title: 'Deep learning for plant disease detection: a review', authors: 'Mohanty, Hughes, Salathe', year: '2024', venue: 'Computers & Electronics in Agriculture', score: 94, tag: 'Highly relevant', summary: 'A benchmark of visual classifiers across 14 crop disease datasets.' },
  { title: 'Few-shot crop disease recognition in the wild', authors: 'Khan, Patel, Singh', year: '2025', venue: 'ICCV Workshops', score: 91, tag: 'New research', summary: 'Adapts vision transformers to field images with sparse labels and noisy backgrounds.' },
  { title: 'Explainable AI for precision agriculture', authors: 'Rao, Chen, Williams', year: '2023', venue: 'Nature Machine Intelligence', score: 86, tag: 'Methodology', summary: 'Compares saliency methods for making agricultural predictions auditable.' },
];

export const insights = [
  ['Research theme', 'Robust field deployment', 'High signal'],
  ['Emerging trend', 'Self-supervised vision models', 'Rising'],
  ['Potential gap', 'Early symptoms under changing light', '92% confidence'],
  ['Suggested method', 'Few-shot ViT + explainability', 'Recommended'],
];

export const datasets = [
  ['PlantVillage', '54,306 images', 'Kaggle', 'License: CC BY 4.0'],
  ['PlantDoc', '2,598 field images', 'GitHub', 'License: CC BY 4.0'],
  ['Cassava Disease', '21,367 images', 'Kaggle', 'License: CC BY-SA 4.0'],
];

export const roadmap = [
  ['Research topic definition', 'Completed', 'Week 1'],
  ['Literature review', 'Completed', 'Week 2'],
  ['Research gap analysis', 'In progress', 'Week 3'],
  ['Dataset collection', 'Upcoming', 'Week 4'],
  ['Model development', 'Upcoming', 'Week 5'],
  ['Experiments and evaluation', 'Upcoming', 'Weeks 6-7'],
];

export const graphNodes = [
  ['Plant disease detection', 50, 13, 'topic'],
  ['Vision Transformer', 27, 35, 'method'],
  ['PlantVillage', 73, 35, 'dataset'],
  ['Few-shot learning', 20, 65, 'method'],
  ['Field lighting gap', 50, 73, 'gap'],
  ['Explainable predictions', 80, 65, 'innovation'],
];
