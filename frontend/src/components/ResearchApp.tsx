import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowUpRight,
  Bell,
  BookOpen,
  BrainCircuit,
  Check,
  ChevronRight,
  ClipboardList,
  Database,
  FlaskConical,
  FolderKanban,
  GitBranch,
  Home,
  Lightbulb,
  LogOut,
  Menu,
  Network,
  Plus,
  Search,
  Send,
  Settings,
  Sparkles,
  Target,
  Users,
  FileText,
  Wrench,
  X,
  Zap,
} from "lucide-react";
import {
  datasets,
  graphNodes,
  papers,
  roadmap,
} from "../mock/demo";
import { askResearchCopilot, collectResearchSources, generateResearchWorkflow, uploadResearchDocument, analyzeResearchPaper } from "../services/ai.service";
import type { ResearchCollectionResponse } from "../services/ai.service";
import type { PaperSearchResult } from "../api/ai.api";
import { getProjectGraph, syncProjectGraph, type ProjectGraph } from "../api/knowledge-graph.api";
import { generateCitations, listAIArtifacts, recommendDatasets, recommendTools } from "../api/ai.api";
import { createProject, listProjects, generateProjectRoadmap, type Project, type ProjectCreate } from "../api/projects.api";
import { papersApi } from "../api/literature.api";
import { datasetsApi } from "../api/datasets.api";
import { toolsApi } from "../api/tools.api";
import { gapsApi } from "../api/research-gaps.api";
import { experimentsApi } from "../api/experiments.api";
import { getRoadmapReminders, roadmapApi, type RoadmapReminder } from "../api/roadmap.api";
import { supervisorApi } from "../api/supervisor.api";
import { citationsApi } from "../api/citations.api";
import { listDocuments, uploadDocument, type ResearchDocument } from "../api/documents.api";
import { getCurrentUser, type User } from "../api/users.api";
import { signOut } from "../services/auth.service";
import "./copilot.css";

const nav = [
  ["Overview", "overview", Home],
  ["Projects", "projects", FolderKanban],
  ["Literature", "literature", BookOpen],
  ["Datasets", "datasets", Database],
  ["Tools", "tools", Wrench],
  ["Research gaps", "gaps", Target],
  ["Experiments", "experiments", FlaskConical],
  ["Citations", "citations", ClipboardList],
  ["Roadmap", "roadmap", GitBranch],
  ["Knowledge graph", "graph", Network],
  ["Documents", "documents", FileText],
  ["Supervisor review", "supervisor", Users],
] as const;

type Screen = (typeof nav)[number][1] | "settings";
type ResourceCounts = {
  papers: number;
  datasets: number;
  tools: number;
  gaps: number;
  experiments: number;
  roadmap: number;
  reviews: number;
  citations: number;
  documents: number;
  progress: number;
};

function apiErrorMessage(error: unknown, fallback: string) {
  const detail = (error as { response?: { data?: { detail?: unknown } } }).response?.data?.detail;
  if (typeof detail === "string") {
    const message = detail.match(/message['\"]\s*:\s*['\"]([^'\"]+)/)?.[1];
    return message || detail.replace(/^\d+\s+[A-Z_]+\.\s*/, "");
  }
  if (detail && typeof detail === "object") {
    const value = detail as { message?: unknown; error?: unknown };
    if (typeof value.message === "string") return value.message;
    if (typeof value.error === "string") return value.error;
  }
  return error instanceof Error ? error.message : fallback;
}

function formatAssistantInline(text: string): React.ReactNode {
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("*") && part.endsWith("*")) return <em key={index}>{part.slice(1, -1)}</em>;
    return <span key={index}>{part}</span>;
  });
}

function AssistantText({ text }: { text: string }) {
  const lines = text.replace(/\r/g, "").split("\n");
  return <div className="assistant-text">{lines.map((line, index) => {
    const trimmed = line.trim();
    if (!trimmed) return <div className="assistant-spacer" key={index} />;
    const heading = trimmed.match(/^#{1,3}\s+(.+)$/);
    if (heading) return <h4 key={index}>{formatAssistantInline(heading[1])}</h4>;
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    if (bullet) return <div className="assistant-bullet" key={index}>• <span>{formatAssistantInline(bullet[1])}</span></div>;
    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (numbered) return <div className="assistant-bullet" key={index}>{trimmed.match(/^\d+/)?.[0]}. <span>{formatAssistantInline(numbered[1])}</span></div>;
    return <p key={index}>{formatAssistantInline(line)}</p>;
  })}</div>;
}
type AssistantMessage = { role: "ai" | "user"; text: string; papers?: { title: string; year?: number | null; url?: string | null; doi?: string | null }[] };
type AIHistoryItem = { id: string; input_text: string; artifact_type: string; created_at: string };

function Badge({
  children,
  tone = "teal",
}: {
  children: React.ReactNode;
  tone?: "teal" | "orange" | "slate";
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
function SectionTitle({
  eyebrow,
  title,
  action,
}: {
  eyebrow?: string;
  title: string;
  action?: string;
}) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
      </div>
      {action && (
        <button className="text-button">
          {action}
          <ArrowUpRight size={15} />
        </button>
      )}
    </div>
  );
}
function MetricStrip({ projectCount, resourceCounts, onNavigate }: { projectCount: number; resourceCounts: ResourceCounts; onNavigate: (screen: Screen) => void }) {
  const liveMetrics = [
    ["Projects", projectCount, "research workspaces", "projects"],
    ["Saved papers", resourceCounts.papers, "in the selected project", "literature"],
    ["Research gaps", resourceCounts.gaps, "identified so far", "gaps"],
    ["Datasets", resourceCounts.datasets, "saved for evaluation", "datasets"],
  ] as const;
  return (
    <div className="metric-grid">
      {liveMetrics.map(([label, value, trend, target]) => (
        <button className="metric" key={label} onClick={() => onNavigate(target as Screen)} type="button">
          <span>{label}</span>
          <strong>{String(value).padStart(2, "0")}</strong>
          <small>
            <ArrowUpRight size={13} />
            {trend}
          </small>
        </button>
      ))}
    </div>
  );
}
function Overview({ onNavigate, project, user, projectCount, resourceCounts }: { onNavigate: (screen: Screen) => void; project: Project | null; user: User; projectCount: number; resourceCounts: ResourceCounts }) {
  const activity = [resourceCounts.papers, resourceCounts.datasets, resourceCounts.gaps, resourceCounts.experiments, resourceCounts.roadmap, resourceCounts.tools, resourceCounts.documents];
  const firstName = user.full_name.trim().split(" ")[0] || "Researcher";
  return (
    <div className="screen">
      <div className="welcome">
        <div>
          <p className="eyebrow">{new Intl.DateTimeFormat(undefined, { weekday: "long", month: "long", day: "numeric", year: "numeric" }).format(new Date())}</p>
          <h1>
            Good morning, <em>{firstName}.</em>
          </h1>
          <p>
            Continue building your research with a little help from your AI
            copilot.
          </p>
        </div>
        <button
          className="primary-button"
          onClick={() => onNavigate("projects")}
        >
          <Plus size={17} /> New project
        </button>
      </div>
      <MetricStrip projectCount={projectCount} resourceCounts={resourceCounts} onNavigate={onNavigate} />
      <div className="overview-grid">
        <section className="panel project-hero">
          <div className="hero-orbit">
            <div className="orbit-center">
              <BrainCircuit size={28} />
              <span>AI</span>
            </div>
            <span className="orbit-dot dot-one">
              <BookOpen size={14} />
            </span>
            <span className="orbit-dot dot-two">
              <Target size={14} />
            </span>
            <span className="orbit-dot dot-three">
              <FlaskConical size={14} />
            </span>
          </div>
          <div className="hero-copy">
            <Badge>{project ? project.status : "New workspace"}</Badge>
            <h2>{project ? project.title : `Welcome, ${user.full_name}`}</h2>
            <p>{project ? project.research_idea : "Create your first research project to begin."}</p>
            <div className="project-meta">
              <span>
                <span className="status-dot" />
                {project ? project.domain : "No project yet"}
              </span>
              <span>{project ? `Updated ${new Date(project.updated_at).toLocaleDateString()}` : "Start by creating a project"}</span>
            </div>
            <button
              className="dark-button"
              onClick={() => onNavigate("projects")}
            >
              Open research cockpit <ChevronRight size={16} />
            </button>
          </div>
        </section>
        <section className="panel insight-panel">
          <SectionTitle eyebrow="AI assistant" title={project ? "Your research status" : "Start your research"} />
          <div className="signal">
            <div className="signal-icon">
              <Zap size={17} />
            </div>
            <div>
              <strong>{project ? (resourceCounts.gaps ? `${resourceCounts.gaps} saved research gap${resourceCounts.gaps === 1 ? "" : "s"}` : "No research gaps saved yet") : "Create a project to unlock AI planning"}</strong>
              <p>
                {project ? `${resourceCounts.papers} papers, ${resourceCounts.datasets} datasets, ${resourceCounts.experiments} experiment plans, and ${resourceCounts.roadmap} roadmap milestones are saved.` : "Create a project, then ask Gemini for a gap analysis, methodology, and milestone roadmap."}
              </p>
            </div>
          </div>
          <div className="mini-chart">
            <span style={{ height: "34%" }} />
            <span style={{ height: "46%" }} />
            <span style={{ height: "40%" }} />
            <span style={{ height: "63%" }} />
            <span style={{ height: "57%" }} />
            <span style={{ height: "78%" }} />
            <span style={{ height: "92%" }} />
          </div>
          <small className="muted">Research momentum · last 7 days</small>
        </section>
      </div>
      <SectionTitle
        eyebrow="Your workbench"
        title="Continue where you left off"
        action="View all projects"
      />
      <div className="project-cards">
        {project ? <ProjectCard name={project.title} domain={project.domain} progress={project.status === "completed" ? 100 : resourceCounts.progress} status={project.status} onClick={() => onNavigate("projects")} /> : <p>No projects found for this account.</p>}
      </div>
    </div>
  );
}
function NewResearch({ onNavigate }: { onNavigate: (screen: Screen) => void }) {
  const [topic, setTopic] = useState("");
  const [searched, setSearched] = useState(false);
  return (
    <div className="screen new-research">
      <div className="new-research-head">
        <div>
          <p className="eyebrow">Start a new research thread</p>
          <h1>What are you curious about?</h1>
          <p>
            Search a topic and thesisflow will map the papers, datasets, notes,
            and research gaps around it.
          </p>
        </div>
        <div className="research-constellation" aria-hidden="true">
          <span className="constellation-core">
            <BrainCircuit size={28} />
          </span>
          <span className="constellation-ring ring-a" />
          <span className="constellation-ring ring-b" />
          <span className="constellation-star star-a">
            <BookOpen size={14} />
          </span>
          <span className="constellation-star star-b">
            <Database size={14} />
          </span>
          <span className="constellation-star star-c">
            <Target size={14} />
          </span>
        </div>
      </div>
      <form
        className="research-search"
        onSubmit={(event) => {
          event.preventDefault();
          setSearched(true);
        }}
      >
        <Search size={21} />
        <input
          autoFocus
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
          placeholder="Try: early detection of plant diseases with computer vision"
        />
        <button className="primary-button" type="submit">
          <Sparkles size={16} /> Find research
        </button>
      </form>
      {searched ? (
        <div className="research-results">
          <div className="result-intro">
            <Badge>Research map ready</Badge>
            <h2>Evidence around “{topic || "plant disease detection"}”</h2>
            <p>
              We found a connected starting point across papers, datasets, and
              open research questions.
            </p>
          </div>
          <div className="result-cards">
            <article>
              <BookOpen size={19} />
              <strong>128 papers</strong>
              <span>Relevant literature and notes</span>
            </article>
            <article>
              <Database size={19} />
              <strong>19 datasets</strong>
              <span>Available public data sources</span>
            </article>
            <article>
              <Target size={19} />
              <strong>7 research gaps</strong>
              <span>Signals worth investigating</span>
            </article>
          </div>
          <button
            className="dark-button"
            onClick={() => onNavigate("projects")}
          >
            View research cockpit <ArrowUpRight size={15} />
          </button>
        </div>
      ) : (
        <div className="search-prompts">
          <span>Popular starting points</span>
          {[
            "Plant disease detection",
            "RAG for scientific literature",
            "Sustainable urban mobility",
          ].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => {
                setTopic(suggestion);
                setSearched(true);
              }}
            >
              {suggestion}
              <ArrowUpRight size={14} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
function ProjectCard({
  name,
  domain,
  progress,
  status,
  onClick,
}: {
  name: string;
  domain: string;
  progress: number;
  status: string;
  onClick: () => void;
}) {
  return (
    <article className="project-card">
      <div className="card-top">
        <Badge tone={status === "AI analysis" ? "teal" : "orange"}>
          {status}
        </Badge>
        <button className="icon-button">
          <ArrowUpRight size={17} />
        </button>
      </div>
      <h3>{name}</h3>
      <p>{domain}</p>
      <div className="progress-label">
        <span>Research progress</span>
        <strong>{progress}%</strong>
      </div>
      <div className="progress">
        <i style={{ width: `${progress}%` }} />
      </div>
      <div className="card-footer">
        <span>Updated today</span>
        <button className="link-button" onClick={onClick}>
          Continue <ChevronRight size={14} />
        </button>
      </div>
    </article>
  );
}
function CreateProjectPanel({ onCreate, onCancel }: { onCreate: (payload: ProjectCreate) => Promise<void>; onCancel?: () => void }) {
  const [title, setTitle] = useState("");
  const [researchIdea, setResearchIdea] = useState("");
  const [domain, setDomain] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (title.trim().length < 2 || researchIdea.trim().length < 10 || domain.trim().length < 2) { setError("Add a title, a research idea (at least 10 characters), and a domain."); return; }
    setSaving(true); setError("");
    try { await onCreate({ title: title.trim(), research_idea: researchIdea.trim(), domain: domain.trim(), description: description.trim() || null, status: "draft" }); }
    catch (requestError) { setError((requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Unable to create the project."); }
    finally { setSaving(false); }
  };
  return <section className="panel" style={{ padding: 24, marginBottom: 24 }}><div className="section-title"><div><p className="eyebrow">New research project</p><h2>Turn an idea into a workspace.</h2></div>{onCancel && <button className="icon-button" type="button" onClick={onCancel}><X size={18} /></button>}</div><form className="research-search" onSubmit={submit} style={{ display: "grid", gap: 12, padding: 0, border: 0, background: "transparent" }}><input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Project title" required /><input value={domain} onChange={(event) => setDomain(event.target.value)} placeholder="Research domain" required /><textarea value={researchIdea} onChange={(event) => setResearchIdea(event.target.value)} placeholder="What do you want to investigate?" rows={3} required /><textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Optional description" rows={2} /><div>{error && <p className="auth-error">{error}</p>}<button className="primary-button" disabled={saving}>{saving ? "Creating…" : "Create project"}</button></div></form></section>;
}
function Workspace({
  onNavigate,
  onOpenCopilot,
  onGenerateWorkflow,
  project,
  onCreateProject,
  resourceCounts,
  projects,
  onSelectProject,
}: {
  onNavigate: (screen: Screen) => void;
  onOpenCopilot: (prompt?: string) => void;
  onGenerateWorkflow: () => void;
  project: Project | null;
  onCreateProject: (payload: ProjectCreate) => Promise<void>;
  resourceCounts: { papers: number; datasets: number; tools: number; gaps: number; experiments: number; roadmap: number; reviews: number; progress: number };
  projects: Project[];
  onSelectProject: (projectId: string) => void;
}) {
  const [createOpen, setCreateOpen] = useState(false);
  if (!project) return <div className="screen"><CreateProjectPanel onCreate={onCreateProject} /><button className="secondary-button" onClick={() => onNavigate("overview")}><ChevronRight size={17} /> Back to overview</button></div>;
  return (
    <div className="screen">
      {createOpen && <CreateProjectPanel onCreate={async (payload) => { await onCreateProject(payload); setCreateOpen(false); }} onCancel={() => setCreateOpen(false)} />}
      <div className="workspace-heading">
        <div>
          <div className="crumb">
            Projects <ChevronRight size={13} /> {project.title}
          </div>
          <h1>{project.title}</h1>
          <div className="project-meta">
            <Badge>{project.status}</Badge>
            <span>Updated {new Date(project.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>{projects.length > 1 && <select aria-label="Select research project" value={project.id} onChange={(event) => onSelectProject(event.target.value)} style={{ padding: "10px 12px", borderRadius: 8 }} >{projects.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select>}<button className="secondary-button" onClick={() => setCreateOpen(true)}><Plus size={16} /> New project</button><button
          className="primary-button"
          onClick={() =>
            onGenerateWorkflow()
          }
        >
          <Sparkles size={17} /> Generate AI roadmap
        </button></div>
      </div>
      <div className="cockpit-grid">
        <section className="panel overview-card">
          <SectionTitle
            eyebrow="Research overview"
            title="A clearer path from idea to evidence"
          />
          <p className="large-copy">{project.research_idea}</p>
          <div className="objective">
            <span>Research objective</span>
            <strong>
              {project.description || "No additional project description has been added."}
            </strong>
          </div>
          <div className="progress-summary">
            <div>
              <span>Overall progress</span>
              <strong>{project.status === "completed" ? 100 : resourceCounts.progress}%</strong>
            </div>
            <div className="progress">
              <i style={{ width: `${project.status === "completed" ? 100 : resourceCounts.progress}%` }} />
            </div>
          </div>
        </section>
        <section className="panel assistant-teaser">
          <div className="assistant-glow">
            <Sparkles size={25} />
          </div>
          <p className="eyebrow">Research copilot</p>
          <h3>Ask better questions. Move faster.</h3>
          <p>
            Explore your literature, gaps, and next steps in one conversation.
          </p>
          <button
            className="dark-button"
            onClick={() =>
              onOpenCopilot(
                `Analyze my current research project (${project.title}) and suggest the next best step. Research idea: ${project.research_idea}`,
              )
            }
          >
            <Send size={15} /> Ask the copilot
          </button>
        </section>
      </div>
      <SectionTitle
        eyebrow="Intelligence layer"
        title="Signals worth your attention"
        action="View all insights"
      />
      <div className="insight-grid">
        {[["Literature", `${resourceCounts.papers} saved paper${resourceCounts.papers === 1 ? "" : "s"}`, resourceCounts.papers ? "Ready for AI analysis" : "Add papers or ask AI"], ["Research gaps", `${resourceCounts.gaps} identified gap${resourceCounts.gaps === 1 ? "" : "s"}`, resourceCounts.gaps ? "Review the saved gaps" : "Generate a gap analysis"], ["Datasets", `${resourceCounts.datasets} saved dataset${resourceCounts.datasets === 1 ? "" : "s"}`, resourceCounts.datasets ? "Ready for experiments" : "Ask AI for recommendations"], ["Roadmap", `${resourceCounts.roadmap} milestone${resourceCounts.roadmap === 1 ? "" : "s"}`, resourceCounts.roadmap ? "Track progress here" : "Generate an AI roadmap"]].map(([label, value, status], index) => (
          <article className="insight-card" key={label}>
            <div className={`insight-number n-${index}`}>0{index + 1}</div>
            <p>{label}</p>
            <h3>{value}</h3>
            <span>{status}</span>
          </article>
        ))}
      </div>
      <SectionTitle eyebrow="Research flow" title="From idea to experiment" />
      <div className="flow">
        <FlowItem icon={BookOpen} title="Literature" value={`${resourceCounts.papers} papers`} done={resourceCounts.papers > 0} />
        <FlowItem icon={Target} title="Gap analysis" value={`${resourceCounts.gaps} signals`} done={resourceCounts.gaps > 0} />
        <FlowItem icon={FlaskConical} title="Experiments" value={`${resourceCounts.experiments} planned`} done={resourceCounts.experiments > 0} />
        <FlowItem icon={GitBranch} title="Roadmap" value={`${resourceCounts.roadmap} milestones`} done={resourceCounts.roadmap > 0} />
      </div>
    </div>
  );
}
function FlowItem({
  icon: Icon,
  title,
  value,
  done,
}: {
  icon: typeof BookOpen;
  title: string;
  value: string;
  done?: boolean;
}) {
  return (
    <div className="flow-item">
      <div className={`flow-icon ${done ? "done" : ""}`}>
        {done ? <Check size={17} /> : <Icon size={17} />}
      </div>
      <div>
        <strong>{title}</strong>
        <span>{value}</span>
      </div>
      {title !== "Roadmap" && <ChevronRight className="flow-arrow" size={16} />}
    </div>
  );
}
function Literature({ projectId, initialQuery }: { projectId?: string; initialQuery?: string }) {
  const [topic, setTopic] = useState(initialQuery || "plant disease detection field images");
  const [results, setResults] = useState<PaperSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState<Record<string, string>>({});
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  useEffect(() => {
    const requested = initialQuery?.trim();
    if (!requested || requested.length < 2) return;
    setTopic(requested); setLoading(true); setError("");
    collectResearchSources(requested, projectId, 12, Boolean(projectId)).then((response) => setResults(response.items || [])).catch(() => setError("Scholarly search failed. Check the backend connection.")).finally(() => setLoading(false));
  }, [initialQuery, projectId]);
  const search = async (event?: React.FormEvent) => {
    event?.preventDefault();
    if (topic.trim().length < 2 || loading) return;
    setLoading(true); setError("");
    try { const response = await collectResearchSources(topic.trim(), projectId, 12, Boolean(projectId)); setResults(response.items || []); }
    catch (requestError) { const detail = (requestError as { response?: { data?: { detail?: string | { message?: string } } } }).response?.data?.detail; setError(typeof detail === "string" ? detail : detail?.message || "Scholarly search failed. Check the backend connection."); }
    finally { setLoading(false); }
  };
  const analyze = async (paper: PaperSearchResult) => {
    const key = paper.external_id || paper.doi || paper.title;
    if (!paper.abstract || analyzing) return;
    setAnalyzing(key); setError("");
    try {
      const response = await analyzeResearchPaper(paper.title, paper.abstract, projectId);
      setAnalysis((current) => ({ ...current, [key]: JSON.stringify(response.result, null, 2) }));
    } catch (requestError) { setError(apiErrorMessage(requestError, "Paper analysis failed. Check GEMINI_API_KEY and try again.")); }
    finally { setAnalyzing(null); }
  };
  return (
    <div className="screen">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Literature intelligence</p>
          <h1>Find the signal in the noise.</h1>
          <p>
            Search across your research landscape with semantic understanding.
          </p>
        </div>
        <button className="secondary-button" type="button">
          <BookOpen size={16} /> Saved papers
        </button>
      </div>
      <form className="search-box" onSubmit={search}>
        <Search size={19} />
        <input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="Search papers, methods, datasets, or concepts..." />
        <kbd>⌘ K</kbd>
        <button type="submit" disabled={loading} aria-label="Search scholarly papers">
          {loading ? "…" : <ArrowUpRight size={17} />}
        </button>
      </form>
      {error && <p className="auth-error">{error}</p>}
      {/* Results are rendered in the literature layout below.
      {results.length > 0 && <section className="panel" style={{ padding: 18, marginBottom: 18 }}><div className="section-title"><div><p className="eyebrow">OpenAlex / Crossref</p><h3>{results.length} relevant scholarly papers</h3></div><Badge>{projectId ? "Saved to project" : "Search results"}</Badge></div><div className="paper-list">{results.map((paper) => <article className="paper-card" key={paper.external_id || paper.doi || paper.title}><div className="paper-icon"><BookOpen size={18} /></div><div className="paper-content"><div className="card-top"><Badge tone="teal">{paper.source}</Badge><span className="paper-year">{paper.year || "Year unavailable"}</span></div><h3>{paper.title}</h3><p className="authors">{paper.authors || "Authors unavailable"} · {paper.publication || "Publication unavailable"}</p><p>{paper.abstract ? `${paper.abstract.slice(0, 260)}${paper.abstract.length > 260 ? "…" : ""}` : "Abstract unavailable from the index."}</p><div className="paper-bottom"><span className="muted">{paper.doi ? `DOI: ${paper.doi.replace("https://doi.org/", "")}` : "No DOI listed"}</span><div>{(paper.pdf_url || paper.url) && <a className="link-button" href={paper.pdf_url || paper.url || "#"} target="_blank" rel="noreferrer">Open paper <ArrowUpRight size={14} /></a>}</div></div></div></article>)}</div></section>}
      */}
      <div className="filter-row">
        <Badge>Semantic search</Badge>
        <button>
          2021–2026 <ChevronRight size={14} />
        </button>
        <button>
          All authors <ChevronRight size={14} />
        </button>
        <button>
          All domains <ChevronRight size={14} />
        </button>
        <span className="result-count">{results.length ? `${results.length} results` : "Search to load results"}</span>
      </div>
      <div className="literature-layout">
        <div className="paper-list">
          {results.length ? results.map((paper) => (
            <article className="paper-card" key={paper.external_id || paper.doi || paper.title}><div className="paper-icon"><BookOpen size={18} /></div><div className="paper-content"><div className="card-top"><Badge tone="teal">{paper.source}</Badge><span className="paper-year">{paper.year || "Year unavailable"}</span></div><h3>{paper.title}</h3><p className="authors">{paper.authors || "Authors unavailable"} · {paper.publication || "Publication unavailable"}</p><p>{paper.abstract ? `${paper.abstract.slice(0, 280)}${paper.abstract.length > 280 ? "…" : ""}` : "Abstract unavailable from the index."}</p><div className="paper-bottom"><span className="muted">{paper.doi ? `DOI: ${paper.doi.replace("https://doi.org/", "")}` : "No DOI listed"}</span>{(paper.pdf_url || paper.url) && <a className="link-button" href={paper.pdf_url || paper.url || "#"} target="_blank" rel="noreferrer">Open paper <ArrowUpRight size={14} /></a>}</div></div></article>
          )) : <p className="muted">Search a topic above to retrieve real scholarly papers and links.</p>}
        </div>
         {results.some((paper) => paper.abstract) && <section className="panel" style={{ padding: 18, marginTop: 16 }}><p className="eyebrow">Paper analysis</p><h3>Understand the evidence</h3>{results.filter((paper) => paper.abstract).slice(0, 5).map((paper) => { const key = paper.external_id || paper.doi || paper.title; return <div className="citation-row" key={`analysis-${key}`}><div><strong>{paper.title}</strong>{analysis[key] && <pre style={{ whiteSpace: "pre-wrap", marginTop: 8, fontSize: 11 }}>{analysis[key]}</pre>}</div><button className="link-button" type="button" onClick={() => void analyze(paper)}>{analyzing === key ? "Analyzing..." : "Analyze with AI"}</button></div>; })}</section>}
         <aside className="panel literature-aside">
          <p className="eyebrow">Topic map</p>
          <h3>{topic || "Your research topic"}</h3>
          <div className="topic-map">
            <span className="topic-main">{topic || "Search topic"}</span>
            <span className="topic t1">Methods</span>
            <span className="topic t2">Datasets</span>
            <span className="topic t3">Evaluation</span>
            <span className="topic t4">Open gaps</span>
          </div>
          <p className="muted">
            Search results come from OpenAlex and Crossref. Select a project to save them automatically.
          </p>
        </aside>
      </div>
    </div>
  );
}
function PaperCard({ paper }: { paper: (typeof papers)[number] }) {
  return (
    <article className="paper-card">
      <div className="paper-icon">
        <BookOpen size={18} />
      </div>
      <div className="paper-content">
        <div className="card-top">
          <Badge tone={paper.tag === "New research" ? "orange" : "teal"}>
            {paper.tag}
          </Badge>
          <span className="paper-year">{paper.year}</span>
        </div>
        <h3>{paper.title}</h3>
        <p className="authors">
          {paper.authors} · {paper.venue}
        </p>
        <p>{paper.summary}</p>
        <div className="paper-bottom">
          <span className="relevance">
            <span>AI relevance</span>
            <strong>{paper.score}%</strong>
            <i>
              <b style={{ width: `${paper.score}%` }} />
            </i>
          </span>
          <div>
            <button className="link-button">Summarize</button>
            <button className="icon-button">
              <Plus size={16} />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
type LiveKind = "papers" | "datasets" | "tools" | "gaps" | "experiments" | "roadmap" | "reviews" | "citations";
function DocumentsView({ projectId }: { projectId?: string }) {
  const [documents, setDocuments] = useState<ResearchDocument[]>([]);
  const [error, setError] = useState("");
  const load = () => { if (projectId) listDocuments(projectId).then((response) => setDocuments(response.data.items)).catch(() => setError("Unable to load documents.")); };
  useEffect(() => { load(); }, [projectId]);
  const upload = async (file: File) => { if (!projectId) return; setError(""); try { await uploadDocument(projectId, file); load(); } catch (requestError) { setError((requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Document upload failed."); } };
  return <div className="screen"><div className="panel" style={{ padding: 20, marginBottom: 18 }}><p className="eyebrow">Project knowledge base</p><h2>Documents</h2><p className="muted">Upload PDF or TXT files to extract text and make them available to the research copilot.</p><label className="primary-button" style={{ display: "inline-flex", cursor: "pointer" }}> <FileText size={16} /> Upload document<input type="file" hidden accept=".pdf,.txt,application/pdf,text/plain" onChange={(event) => { const file = event.target.files?.[0]; if (file) void upload(file); }} /></label>{error && <p className="auth-error">{error}</p>}</div><div className="panel" style={{ padding: 20 }}>{documents.length ? documents.map((document) => <div className="citation-row" key={document.id}><div><strong>{document.file_name}</strong><span>{document.status} · {document.page_count} page(s) · {document.indexed ? "indexed for RAG" : "text extracted"}</span></div><Badge tone={document.status === "ready" ? "teal" : "orange"}>{document.status}</Badge></div>) : <p className="muted">No documents uploaded for this project yet.</p>}</div></div>;
}
function ResourceCreateForm({ projectId, kind, onDone }: { projectId: string; kind: LiveKind; onDone: () => void }) {
  const examples: Record<LiveKind, Record<string, unknown>> = {
    papers: { title: "Paper title", authors: "Author names", abstract: "Abstract", year: 2026, keywords: "keyword" },
    datasets: { name: "Dataset name", description: "How it supports the project", source: "Official source", domain: "AI" },
    tools: { name: "Tool name", category: "Research", description: "How it will be used" },
    gaps: { problem: "Observed problem", research_gap: "Potential research gap", proposed_innovation: "Proposed innovation" },
    experiments: { methodology: "Methodology", algorithms: "Baseline and proposed algorithms", evaluation_metrics: "F1, accuracy", workflow: "Experiment steps", expected_results: "Expected result" },
    roadmap: { week_number: 1, task: "First milestone", status: "pending", remarks: "Notes" },
    reviews: { supervisor_name: "Supervisor name", comments: "Feedback", approval_status: "pending", suggestions: "Suggestions" },
    citations: { apa: "APA citation", ieee: "IEEE citation", bibtex: "BibTeX", paper_id: null },
  };
  const [value, setValue] = useState(JSON.stringify(examples[kind], null, 2));
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const payload = JSON.parse(value) as Record<string, unknown>;
      setSaving(true); setError("");
      const creators: Record<LiveKind, (id: string, body: Record<string, unknown>) => Promise<unknown>> = { papers: papersApi.create as never, datasets: datasetsApi.create as never, tools: toolsApi.create as never, gaps: gapsApi.create as never, experiments: experimentsApi.create as never, roadmap: roadmapApi.create as never, reviews: supervisorApi.create as never, citations: citationsApi.create as never };
      await creators[kind](projectId, payload); onDone();
    } catch (requestError) { setError(requestError instanceof SyntaxError ? "Enter valid JSON." : (requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Unable to save this item."); }
    finally { setSaving(false); }
  };
  return <form className="panel" style={{ padding: 18, marginBottom: 18 }} onSubmit={submit}><div className="section-title"><div><p className="eyebrow">Add {kind}</p><h3>Save a research record</h3></div><button className="icon-button" type="button" onClick={onDone}><X size={18} /></button></div><textarea value={value} onChange={(event) => setValue(event.target.value)} rows={10} style={{ width: "100%", fontFamily: "monospace", padding: 12, borderRadius: 8, border: "1px solid #d9dfda" }} />{error && <p className="auth-error">{error}</p>}<button className="primary-button" disabled={saving}>{saving ? "Saving…" : "Save record"}</button></form>;
}
function LiveResourceSummary({ projectId, kind, refresh = 0 }: { projectId?: string; kind: LiveKind; refresh?: number }) {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  useEffect(() => {
    if (!projectId) return;
    const loaders: Record<LiveKind, (id: string) => Promise<{ data: { items: Record<string, unknown>[]; total: number } }>> = { papers: papersApi.list, datasets: datasetsApi.list, tools: toolsApi.list, gaps: gapsApi.list, experiments: experimentsApi.list, roadmap: roadmapApi.list, reviews: supervisorApi.list, citations: citationsApi.list };
    loaders[kind](projectId).then((response) => { setItems(response.data.items); setTotal(response.data.total); }).catch(() => { setItems([]); setTotal(0); });
  }, [projectId, kind, refresh]);
  if (!projectId) return <div className="panel" style={{ padding: 18, marginBottom: 18 }}>Create a project to save {kind}.</div>;
  return <section className="panel" style={{ padding: 18, marginBottom: 18 }}><div className="section-title"><div><p className="eyebrow">Saved in this project</p><h3>{total} {kind}</h3></div></div>{items.length ? <div className="citation-list">{items.slice(0, 20).map((item, index) => { const title = String(item.title ?? item.name ?? item.task ?? item.supervisor_name ?? item.research_gap ?? item.methodology ?? "Saved item"); const description = String(item.abstract ?? item.description ?? item.problem ?? item.comments ?? item.remarks ?? item.expected_results ?? ""); const link = typeof item.url === "string" ? item.url : typeof item.download_link === "string" ? item.download_link : null; return <div className="citation-row" key={String(item.id ?? index)}><div><strong>{title}</strong><span>{String(item.status ?? item.approval_status ?? item.domain ?? item.category ?? "Saved record")}{description ? ` · ${description.slice(0, 180)}` : ""}</span></div>{link && <a className="link-button" href={link} target="_blank" rel="noreferrer">Open link <ArrowUpRight size={14} /></a>}</div>; })}</div> : <p className="muted">No saved {kind} yet. Use “New entry” or generate an AI workflow for this project.</p>}</section>;
}
function RoadmapTracker({ projectId, refresh = 0, onChanged }: { projectId?: string; refresh?: number; onChanged?: () => void }) {
  const [items, setItems] = useState<{ id: string; week_number: number; task: string; deadline?: string | null; status: "pending" | "in_progress" | "completed" | "blocked"; remarks?: string | null }[]>([]);
  const [total, setTotal] = useState(0);
  const [updating, setUpdating] = useState<string | null>(null);
  useEffect(() => { if (!projectId) return; const load = async () => { try { await generateProjectRoadmap(projectId); const response = await roadmapApi.list(projectId, { size: 100 }); setItems(response.data.items as typeof items); setTotal(response.data.total); } catch { setItems([]); setTotal(0); } }; void load(); }, [projectId, refresh]);
  const updateStatus = async (id: string, status: typeof items[number]["status"]) => { if (!projectId) return; setUpdating(id); try { const response = await roadmapApi.update(projectId, id, { status }); setItems((current) => current.map((item) => item.id === id ? { ...item, ...(response.data as typeof item) } : item)); onChanged?.(); } finally { setUpdating(null); } };
  if (!projectId) return <div className="panel" style={{ padding: 18 }}>Create a project to build its roadmap.</div>;
  return <section className="panel" style={{ padding: 18 }}><div className="section-title"><div><p className="eyebrow">Saved in this project</p><h3>{total} roadmap milestones</h3></div><span className="badge">Update automatically when opened</span></div>{items.length ? <div className="citation-list">{items.sort((a, b) => a.week_number - b.week_number).map((item) => <div className="citation-row" key={item.id}><div><strong>Week {item.week_number}: {item.task}</strong><span>{item.deadline ? `Deadline ${item.deadline}` : "No deadline"}{item.remarks ? ` · ${item.remarks}` : ""}</span></div><select aria-label={`Status for week ${item.week_number}`} value={item.status} disabled={updating === item.id} onChange={(event) => void updateStatus(item.id, event.target.value as typeof item.status)}><option value="pending">Pending</option><option value="in_progress">In progress</option><option value="completed">Completed</option><option value="blocked">Blocked</option></select></div>)}</div> : <p className="muted">No milestones yet. Open this page again after selecting a project.</p>}</section>;
}
function SupervisorReviewTracker({ projectId, refresh = 0, onChanged }: { projectId?: string; refresh?: number; onChanged?: () => void }) {
  const [items, setItems] = useState<Awaited<ReturnType<typeof supervisorApi.list>>["data"]["items"]>([]);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState<string | null>(null);
  useEffect(() => {
    if (!projectId) return;
    setLoading(true);
    supervisorApi.list(projectId, { size: 100 }).then((response) => setItems(response.data.items)).catch(() => setItems([])).finally(() => setLoading(false));
  }, [projectId, refresh]);
  const updateStatus = async (id: string, approval_status: "pending" | "approved" | "changes_requested") => {
    if (!projectId) return;
    setUpdating(id);
    try { const response = await supervisorApi.update(projectId, id, { approval_status }); setItems((current) => current.map((item) => item.id === id ? response.data : item)); onChanged?.(); }
    finally { setUpdating(null); }
  };
  if (!projectId) return <div className="panel" style={{ padding: 18 }}>Create a project before adding supervisor reviews.</div>;
  return <section className="panel" style={{ padding: 18 }}><div className="section-title"><div><p className="eyebrow">Supervisor feedback</p><h3>{items.length} review{items.length === 1 ? "" : "s"} recorded</h3></div><span className="badge">Approval tracking</span></div>{loading ? <p className="muted">Loading supervisor reviews...</p> : items.length ? <div className="citation-list">{items.map((item) => <div className="citation-row" key={item.id}><div><strong>{item.supervisor_name}</strong><span>{item.meeting_date ? `Meeting ${item.meeting_date}` : "Meeting date not provided"}{item.comments ? ` · ${item.comments}` : ""}{item.suggestions ? ` · Suggestion: ${item.suggestions}` : ""}</span></div><select aria-label={`Approval status for ${item.supervisor_name}`} value={item.approval_status} disabled={updating === item.id} onChange={(event) => void updateStatus(item.id, event.target.value as "pending" | "approved" | "changes_requested")}><option value="pending">Pending</option><option value="approved">Approved</option><option value="changes_requested">Changes requested</option></select></div>)}</div> : <p className="muted">No supervisor review recorded yet. Use New entry to add feedback.</p>}</section>;
}
function LiveGraphView({ projectId }: { projectId?: string }) {
  const [graph, setGraph] = useState<ProjectGraph | null>(null);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState(false);
  useEffect(() => {
    if (!projectId) return;
    getProjectGraph(projectId).then((response) => { setGraph(response.data); setError(""); }).catch((requestError) => setError(apiErrorMessage(requestError, "Neo4j is not configured or the graph is unavailable.")));
  }, [projectId]);
  if (!projectId) return <div className="panel" style={{ padding: 18 }}>Create or select a project to view its knowledge graph.</div>;
  const sync = async () => { if (!projectId || syncing) return; setSyncing(true); setError(""); try { const response = await syncProjectGraph(projectId); setGraph(response.data.graph); } catch (requestError) { setError(apiErrorMessage(requestError, "Graph synchronization failed.")); } finally { setSyncing(false); } };
  if (error && !graph) return <section className="panel" style={{ padding: 18 }}><div className="section-title"><div><p className="eyebrow">Project graph</p><h3>Generate your knowledge graph</h3></div><button className="primary-button" type="button" onClick={() => void sync()} disabled={syncing}>{syncing ? "Generating..." : "Generate graph"}</button></div><p className="muted">{error} Click Generate graph to sync this project’s papers, authors, themes, and research gaps.</p></section>;
  if (!graph) return <div className="panel" style={{ padding: 18 }}>Loading project knowledge graph...</div>;
  const groups = [{ label: "Papers", items: graph.papers }, { label: "Authors", items: graph.authors }, { label: "Themes", items: graph.themes }, { label: "Research gaps", items: graph.gaps }];
  return <div className="graph-layout"><section className="panel" style={{ padding: 18 }}><div className="section-title"><div><p className="eyebrow">Live Neo4j graph</p><h2>{graph.project.title || graph.project.name || "Project"}</h2></div><button className="primary-button" type="button" onClick={() => void sync()} disabled={syncing}>{syncing ? "Generating..." : "Generate graph"}</button></div><p className="muted">Generate concepts from saved papers, authors, title keywords, and research gaps.</p>{error && <p className="auth-error">{error}</p>}{groups.map((group) => <div key={group.label} style={{ marginTop: 18 }}><h3>{group.label} ({group.items.length})</h3>{group.items.length ? <div className="citation-list">{group.items.map((item) => <div className="citation-row" key={`${group.label}-${item.id}`}><strong>{item.title || item.name || item.id}</strong><span>{item.description || item.abstract || "Connected research node"}</span></div>)}</div> : <p className="muted">No {group.label.toLowerCase()} nodes synced yet.</p>}</div>)}</section></div>;
}
function InsightsScreen({
  kind,
  projectId,
  onResourceChange,
}: {
  kind:
    | "gaps"
    | "datasets"
    | "tools"
    | "experiments"
    | "roadmap"
    | "graph"
    | "supervisor"
    | "projects"
    | "citations"
    | "documents";
  projectId?: string;
  onResourceChange?: () => void;
}) {
  const titles = {
    gaps: [
      "Research gap intelligence",
      "See where the unanswered questions are.",
      "gaps",
    ],
    datasets: [
      "Dataset discovery",
      "The right evidence makes the difference.",
      "datasets",
    ],
    tools: ["Tool recommendations", "Keep the research stack reproducible.", "tools"],
    experiments: [
      "Experiment planner",
      "Turn a hypothesis into a testable workflow.",
      "experiments",
    ],
    roadmap: [
      "Research roadmap",
      "A thoughtful sequence for meaningful progress.",
      "roadmap",
    ],
    graph: [
      "Knowledge graph",
      "See the ideas, methods, and evidence connected.",
      "graph",
    ],
    supervisor: [
      "Supervisor review",
      "Keep feedback close to the work.",
      "supervisor",
    ],
    projects: [
      "Your research projects",
      "Everything you are building, in one place.",
      "projects",
    ],
    citations: [
      "Citation intelligence",
      "Keep your evidence organized and ready to share.",
      "citations",
    ],
    documents: ["Research documents", "Extract and search your source material.", "documents"],
  } as const;
  const [title, subtitle] = titles[kind];
  const [creating, setCreating] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState("");
  const liveKind: LiveKind | null = kind === "projects" || kind === "graph" || kind === "documents" ? null : kind === "supervisor" ? "reviews" : kind;
  const runResourceAction = async () => {
    if (!projectId || actionLoading) return;
    setActionLoading(true); setActionMessage("");
    try {
      if (kind === "datasets") {
        const response = await recommendDatasets(projectId);
        setActionMessage(`${response.data.saved_count} dataset recommendation(s) saved.`);
      } else if (kind === "tools") {
        const response = await recommendTools(projectId);
        setActionMessage(`${response.data.saved_count} tool recommendation(s) saved.`);
      } else if (kind === "citations") {
        const response = await generateCitations(projectId);
        setActionMessage(`${response.data.created_count} citation record(s) generated from ${response.data.paper_count} saved paper(s).`);
      }
      setRefresh((value) => value + 1); onResourceChange?.();
    } catch (error) {
      setActionMessage(apiErrorMessage(error, "Unable to generate this resource right now."));
    } finally { setActionLoading(false); }
  };
  return (
    <div className="screen">
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            {kind === "gaps" ? "AI analysis" : "Research workspace"}
          </p>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        <div className="page-actions">
          {(kind === "datasets" || kind === "tools" || kind === "citations") && <button className="primary-button" onClick={() => void runResourceAction()} disabled={!projectId || actionLoading}>{actionLoading ? "Generating..." : kind === "citations" ? "Generate citations" : kind === "datasets" ? "Recommend datasets" : "Recommend tools"}</button>}
          <button className="secondary-button" onClick={() => liveKind && projectId && setCreating(true)} disabled={!liveKind || !projectId}>
            <Sparkles size={16} />{" "}
            {kind === "gaps" ? "Analyze gaps" : "New entry"}
          </button>
        </div>
      </div>
      {actionMessage && <p className="action-message">{actionMessage}</p>}
      {creating && liveKind && projectId && <ResourceCreateForm projectId={projectId} kind={liveKind} onDone={() => { setCreating(false); setRefresh((value) => value + 1); }} />}
      {kind === "documents" ? (
        <DocumentsView projectId={projectId} />
      ) : kind === "gaps" ? (
        <LiveResourceSummary projectId={projectId} kind="gaps" refresh={refresh} />
      ) : kind === "datasets" ? (
        <LiveResourceSummary projectId={projectId} kind="datasets" refresh={refresh} />
      ) : kind === "tools" ? (
        <><LiveResourceSummary projectId={projectId} kind="tools" refresh={refresh} /></>
      ) : kind === "experiments" ? (
        <LiveResourceSummary projectId={projectId} kind="experiments" refresh={refresh} />
      ) : kind === "roadmap" ? (
        <RoadmapTracker projectId={projectId} refresh={refresh} onChanged={onResourceChange} />
      ) : kind === "graph" ? (
        <LiveGraphView projectId={projectId} />
      ) : kind === "supervisor" ? (
        <SupervisorReviewTracker projectId={projectId} refresh={refresh} onChanged={onResourceChange} />
      ) : kind === "projects" ? (
        <div className="project-cards">
          <ProjectCard
            name="Plant disease detection"
            domain="Computer Vision / Agriculture"
            progress={68}
            status="AI analysis"
            onClick={() => {}}
          />
          <ProjectCard
            name="Low-resource NLP evaluation"
            domain="Natural Language Processing"
            progress={31}
            status="Literature review"
            onClick={() => {}}
          />
          <div className="empty-project">
            <Plus size={20} />
            <strong>Start a new direction</strong>
            <span>Create a research workspace</span>
          </div>
        </div>
      ) : (
        <LiveResourceSummary projectId={projectId} kind="citations" refresh={refresh} />
      )}
    </div>
  );
}
function GapView() {
  return (
    <>
      <div className="gap-flow">
        {[
          "Existing research",
          "Known limitations",
          "Unsolved problems",
          "Research gap",
          "Your innovation",
        ].map((x, i) => (
          <div key={x} className={`gap-step step-${i}`}>
            <span>0{i + 1}</span>
            <strong>{x}</strong>
            {i < 4 && <ChevronRight size={16} />}
          </div>
        ))}
      </div>
      <div className="gap-grid">
        {[
          [
            "Problem",
            "Models perform well in curated images but fail in the field.",
          ],
          [
            "Existing solution",
            "Transfer learning with large labeled datasets.",
          ],
          [
            "Research gap",
            "Early symptoms under changing light remain underrepresented.",
          ],
          [
            "Proposed innovation",
            "Few-shot adaptation with uncertainty-aware explanations.",
          ],
        ].map(([x, y]) => (
          <article className="panel gap-card" key={x}>
            <p className="eyebrow">{x}</p>
            <h3>{y}</h3>
            <Badge tone={x === "Research gap" ? "orange" : "teal"}>
              {x === "Research gap" ? "92% confidence" : "AI extracted"}
            </Badge>
          </article>
        ))}
      </div>
    </>
  );
}
function DatasetView() {
  return (
    <>
      <div className="recommend-banner">
        <div className="assistant-glow">
          <Sparkles size={21} />
        </div>
        <div>
          <strong>Recommended for your research</strong>
          <p>
            These datasets match your domain, image modality, and current gap
            analysis.
          </p>
        </div>
        <ArrowUpRight />
      </div>
      <div className="dataset-grid">
        {datasets.map(([name, size, source, license]) => (
          <article className="dataset-card" key={name}>
            <div className="dataset-mark">
              <Database size={19} />
            </div>
            <Badge>{source}</Badge>
            <h3>{name}</h3>
            <p>
              Field-ready image collection for plant health classification and
              detection.
            </p>
            <div className="dataset-meta">
              <span>{size}</span>
              <span>{license}</span>
            </div>
            <button className="dark-button">
              View dataset <ArrowUpRight size={15} />
            </button>
          </article>
        ))}
      </div>
    </>
  );
}
function ExperimentView() {
  return (
    <div className="experiment-layout">
      <section className="panel experiment-main">
        <SectionTitle
          eyebrow="Active plan"
          title="Field robustness benchmark"
          action="Edit plan"
        />
        <div className="pipeline">
          {[
            "Dataset",
            "Preprocessing",
            "Features",
            "ViT model",
            "Training",
            "Evaluation",
          ].map((x, i) => (
            <div className="pipeline-step" key={x}>
              <div className={i < 3 ? "pipeline-node active" : "pipeline-node"}>
                {i + 1}
              </div>
              <strong>{x}</strong>
              {i < 5 && <div className="pipeline-line" />}
            </div>
          ))}
        </div>
        <div className="experiment-table">
          <div>
            <span>Methodology</span>
            <strong>Few-shot transfer learning</strong>
          </div>
          <div>
            <span>Evaluation metrics</span>
            <strong>F1 · mAP · calibration error</strong>
          </div>
          <div>
            <span>Expected result</span>
            <strong>10% lift on unseen field conditions</strong>
          </div>
        </div>
      </section>
      <aside className="panel status-panel">
        <p className="eyebrow">Experiment status</p>
        <div className="status-ring">
          <strong>01</strong>
          <span>planned</span>
        </div>
        <button className="primary-button">
          Run experiment <Zap size={15} />
        </button>
        <p className="muted">
          Connect your training environment to sync live runs.
        </p>
      </aside>
    </div>
  );
}
function RoadmapView() {
  return (
    <div className="roadmap-layout">
      <div className="timeline">
        {roadmap.map(([title, status, week], i) => (
          <div className="timeline-item" key={title}>
            <div
              className={`timeline-dot ${status === "Completed" ? "complete" : status === "In progress" ? "current" : ""}`}
            >
              {status === "Completed" ? <Check size={14} /> : i + 1}
            </div>
            <div className="timeline-copy">
              <span>{week}</span>
              <h3>{title}</h3>
              <Badge
                tone={
                  status === "Upcoming"
                    ? "slate"
                    : status === "In progress"
                      ? "orange"
                      : "teal"
                }
              >
                {status}
              </Badge>
            </div>
          </div>
        ))}
      </div>
      <aside className="panel roadmap-summary">
        <p className="eyebrow">Progress</p>
        <strong>38%</strong>
        <div className="progress">
          <i style={{ width: "38%" }} />
        </div>
        <p>
          On track to complete your first research milestone by September 12.
        </p>
        <button className="dark-button">
          Add milestone <Plus size={15} />
        </button>
      </aside>
    </div>
  );
}
function GraphView() {
  return (
    <div className="graph-layout">
      <section className="panel graph-canvas">
        <div className="graph-lines" />
        {graphNodes.map(([label, left, top, type]) => (
          <button
            className={`graph-node node-${type}`}
            style={{ left: `${left}%`, top: `${top}%` }}
            key={label as string}
          >
            <span>
              {type === "gap" ? (
                <Lightbulb size={15} />
              ) : type === "dataset" ? (
                <Database size={15} />
              ) : (
                <Network size={15} />
              )}
            </span>
            {label}
          </button>
        ))}
      </section>
      <aside className="panel node-detail">
        <p className="eyebrow">Selected node</p>
        <div className="detail-icon">
          <Lightbulb size={20} />
        </div>
        <h2>Field lighting gap</h2>
        <Badge tone="orange">Research gap</Badge>
        <p>
          Only 8% of reviewed papers evaluate early symptoms across multiple
          natural lighting conditions.
        </p>
        <div className="detail-row">
          <span>Connected papers</span>
          <strong>23</strong>
        </div>
        <div className="detail-row">
          <span>Confidence</span>
          <strong>92%</strong>
        </div>
        <button className="dark-button">
          Explore connections <ArrowUpRight size={15} />
        </button>
      </aside>
    </div>
  );
}
function SupervisorView() {
  return (
    <div className="supervisor-layout">
      <section className="panel review-card">
        <div className="review-header">
          <div className="avatar">AM</div>
          <div>
            <h3>Dr. Ananya Mehta</h3>
            <p>Supervisor · Computer Vision Lab</p>
          </div>
          <Badge tone="orange">Pending review</Badge>
        </div>
        <div className="review-quote">
          “The research direction is promising. Please strengthen the field
          validation plan and clarify the expected contribution versus existing
          few-shot methods.”
        </div>
        <div className="review-actions">
          <button className="secondary-button">Reply to review</button>
          <button className="dark-button">
            Submit update <Send size={15} />
          </button>
        </div>
      </section>
      <section className="panel history">
        <SectionTitle eyebrow="Review history" title="A clear feedback trail" />
        {[
          "Initial project proposal submitted",
          "Literature scope refined",
          "Field validation requested",
        ].map((x, i) => (
          <div className="history-row" key={x}>
            <div className={`history-dot ${i === 2 ? "active" : ""}`} />
            <div>
              <strong>{x}</strong>
              <span>
                {i === 2 ? "Today, 10:42 AM" : `August ${18 - i}, 2026`}
              </span>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
function CitationView() {
  return (
    <div className="citation-layout">
      <section className="panel citation-main">
        <div className="citation-stat">
          <span>Total references</span>
          <strong>42</strong>
          <small>+8 this month</small>
        </div>
        <div className="citation-stat">
          <span>Recent papers</span>
          <strong>18</strong>
          <small>Across 3 projects</small>
        </div>
        <div className="citation-stat">
          <span>Highly cited</span>
          <strong>12</strong>
          <small>Impact score &gt; 80</small>
        </div>
        <div className="citation-list">
          {papers.map((paper) => (
            <div className="citation-row" key={paper.title}>
              <div>
                <strong>{paper.title}</strong>
                <span>
                  {paper.authors} · {paper.year}
                </span>
              </div>
              <Badge>IEEE</Badge>
              <button className="icon-button">
                <ClipboardList size={16} />
              </button>
            </div>
          ))}
        </div>
      </section>
      <aside className="panel format-panel">
        <p className="eyebrow">Export format</p>
        <h3>Ready to cite</h3>
        {["APA 7th edition", "IEEE", "BibTeX", "MLA"].map((x, i) => (
          <button
            key={x}
            className={`format-option ${i === 1 ? "selected" : ""}`}
          >
            <span>{x}</span>
            <ChevronRight size={15} />
          </button>
        ))}
        <button className="dark-button">
          Export citations <ArrowUpRight size={15} />
        </button>
      </aside>
    </div>
  );
}
function SettingsScreen({ user, remindersEnabled, onRemindersEnabledChange, onLogout }: { user: User; remindersEnabled: boolean; onRemindersEnabledChange: (enabled: boolean) => void; onLogout: () => void }) {
  return (
    <div className="screen settings-screen">
      <div className="page-heading">
        <div><p className="eyebrow">Workspace preferences</p><h1>Settings</h1><p>Manage your account and research workspace preferences.</p></div>
      </div>
      <div className="settings-grid">
        <section className="panel settings-card">
          <p className="eyebrow">Account</p><h2>Profile</h2>
          <div className="settings-profile"><div className="avatar large">{user.full_name.slice(0, 2).toUpperCase()}</div><div><strong>{user.full_name}</strong><span>{user.email}</span></div></div>
          <dl className="settings-details"><div><dt>Institution</dt><dd>{user.institution || "Not provided"}</dd></div><div><dt>Account status</dt><dd>{user.is_active ? "Active" : "Inactive"}</dd></div></dl>
        </section>
        <section className="panel settings-card">
          <p className="eyebrow">Research workflow</p><h2>Notifications</h2>
          <label className="setting-toggle"><span><strong>Roadmap deadline reminders</strong><small>Show overdue and upcoming milestones in the notification bell.</small></span><input type="checkbox" checked={remindersEnabled} onChange={(event) => onRemindersEnabledChange(event.target.checked)} /><i /></label>
          <div className="setting-note"><Bell size={15} /> Reminders are checked automatically when you open the workspace and roadmap.</div>
        </section>
        <section className="panel settings-card">
          <p className="eyebrow">AI services</p><h2>Research copilot</h2>
          <div className="service-status"><span className="status-dot" /> Gemini provider configured through the backend</div>
          <p className="muted">AI answers use your selected project, saved papers, datasets, gaps, and uploaded documents as context.</p>
        </section>
        <section className="panel settings-card danger-card">
          <p className="eyebrow">Session</p><h2>Sign out</h2><p className="muted">End this session on the current device.</p><button className="logout-button" onClick={onLogout}><LogOut size={16} /> Log out</button>
        </section>
      </div>
    </div>
  );
}
export type ResearchScreen = Screen;

export default function ResearchApp({ initialScreen = "overview" }: { initialScreen?: Screen } = {}) {
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [screen, setScreen] = useState<Screen>(initialScreen);
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [reminders, setReminders] = useState<RoadmapReminder[]>([]);
  const [remindersEnabled, setRemindersEnabled] = useState(() => localStorage.getItem("roadmap_reminders_enabled") !== "false");
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [literatureQuery, setLiteratureQuery] = useState("");
  const [assistantDraft, setAssistantDraft] = useState("");
  const [assistantMessages, setAssistantMessages] = useState<AssistantMessage[]>([
    { role: "ai", text: "I’m ready to connect the dots across your research. Ask me about gaps, papers, datasets, or your next experiment." },
  ]);
  const chatRef = useRef<HTMLDivElement>(null);
  const hasAutoPrompted = useRef(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyQuery, setHistoryQuery] = useState("");
  const [aiHistory, setAiHistory] = useState<AIHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [assistantMode, setAssistantMode] = useState<"ask" | "sources" | "report">("ask");
  const [resourceVersion, setResourceVersion] = useState(0);
  const [resourceCounts, setResourceCounts] = useState<ResourceCounts>({ papers: 0, datasets: 0, tools: 0, gaps: 0, experiments: 0, roadmap: 0, reviews: 0, citations: 0, documents: 0, progress: 0 });
  useEffect(() => {
    if (!assistantOpen || !chatRef.current) return;
    chatRef.current.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [assistantMessages, assistantLoading, assistantOpen]);
  useEffect(() => {
    const token = localStorage.getItem("research_access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
    Promise.all([getCurrentUser(), listProjects()])
      .then(([userResponse, projectResponse]) => {
        setUser(userResponse.data);
        setProjects(projectResponse.data.items);
        setSelectedProjectId(projectResponse.data.items[0]?.id ?? null);
      })
      .catch(() => {
        localStorage.removeItem("research_access_token");
        localStorage.removeItem("research_refresh_token");
        setLoadError("Your session has expired. Please sign in again.");
      })
      .finally(() => setLoading(false));
  }, []);
  const project = projects.find((item) => item.id === selectedProjectId) || projects[0] || null;
  useEffect(() => {
    if (!project?.id || !remindersEnabled) { setReminders([]); return; }
    const loadReminders = () => getRoadmapReminders(project.id).then((response) => setReminders(response.data.items || [])).catch(() => setReminders([]));
    void loadReminders();
    const timer = window.setInterval(loadReminders, 60_000);
    return () => window.clearInterval(timer);
  }, [project?.id, resourceVersion, remindersEnabled]);
  useEffect(() => {
    if (!historyOpen || !project?.id) return;
    setHistoryLoading(true);
    listAIArtifacts(project.id, { page: 1, size: 100 }).then((response) => {
      const items = (response.data.items || []).filter((item) => typeof item.input_text === "string").map((item) => ({ id: String(item.id), input_text: String(item.input_text), artifact_type: String(item.artifact_type || "chat"), created_at: String(item.created_at || "") }));
      setAiHistory(items);
    }).catch(() => setAiHistory([])).finally(() => setHistoryLoading(false));
  }, [historyOpen, project?.id, assistantMessages.length]);
  useEffect(() => {
    if (!project) { setResourceCounts({ papers: 0, datasets: 0, tools: 0, gaps: 0, experiments: 0, roadmap: 0, reviews: 0, citations: 0, documents: 0, progress: 0 }); return; }
    Promise.all([papersApi.list(project.id, { size: 1 }), datasetsApi.list(project.id, { size: 1 }), toolsApi.list(project.id, { size: 1 }), gapsApi.list(project.id, { size: 1 }), experimentsApi.list(project.id, { size: 1 }), roadmapApi.list(project.id, { size: 100 }), supervisorApi.list(project.id, { size: 1 }), citationsApi.list(project.id, { size: 1 }), listDocuments(project.id, { size: 1 })]).then(([papersResponse, datasetsResponse, toolsResponse, gapsResponse, experimentsResponse, roadmapResponse, reviewsResponse, citationsResponse, documentsResponse]) => { const completed = roadmapResponse.data.items.filter((item) => item.status === "completed").length; const progress = roadmapResponse.data.total ? Math.round((completed / roadmapResponse.data.total) * 100) : 0; setResourceCounts({ papers: papersResponse.data.total, datasets: datasetsResponse.data.total, tools: toolsResponse.data.total, gaps: gapsResponse.data.total, experiments: experimentsResponse.data.total, roadmap: roadmapResponse.data.total, reviews: reviewsResponse.data.total, citations: citationsResponse.data.total, documents: documentsResponse.data.total, progress }); }).catch(() => undefined);
  }, [project?.id, resourceVersion]);
  const handleCreateProject = async (payload: ProjectCreate) => {
    const response = await createProject(payload);
    setProjects((current) => [response.data, ...current]);
    setSelectedProjectId(response.data.id);
    setScreen("projects");
    // Seed the new workspace with real scholarly results in the background.
    void collectResearchSources(response.data.research_idea, response.data.id, 10, true)
      .then(() => setResourceVersion((value) => value + 1))
      .catch(() => undefined);
  };
  const handleGenerateWorkflow = async () => {
    if (!project) {
      setAssistantOpen(true);
      return;
    }
    setAssistantOpen(true);
    setAssistantLoading(true);
    setAssistantMessages((messages) => [...messages, { role: "user", text: "Generate a complete evidence-based research roadmap for this project." }]);
    try {
      const response = await generateResearchWorkflow(project.research_idea, [], project.id);
      const persisted = response.persisted || {};
      const summary = Object.entries(persisted).filter(([, count]) => count > 0).map(([name, count]) => `${count} ${name}`).join(", ");
      setAssistantMessages((messages) => [...messages, { role: "ai", text: `Research workflow generated successfully. ${summary ? `Saved ${summary} to this project.` : "Review the generated workflow in the AI response."}` }]);
      setResourceVersion((value) => value + 1);
    } catch (error) {
      // Keep the roadmap usable during Gemini outages/rate limits. The
      // backend derives an evidence-aware baseline from the saved project
      // records, so the student is never left with an empty roadmap.
      try {
        await generateProjectRoadmap(project.id);
        setResourceVersion((value) => value + 1);
        setAssistantMessages((messages) => [...messages, { role: "ai", text: `The AI service is temporarily unavailable (${apiErrorMessage(error, "temporary error")}). I updated the roadmap from your saved papers, datasets, and research gaps. You can retry AI enrichment later.` }]);
      } catch {
        setAssistantMessages((messages) => [...messages, { role: "ai", text: apiErrorMessage(error, "Unable to update the roadmap. Check the backend connection.") }]);
      }
    } finally {
      setAssistantLoading(false);
    }
  };
  if (loading) return <div className="app-frame"><main className="main"><div className="screen"><h1>Loading your workspace...</h1></div></main></div>;
  if (loadError || !user) return <div className="app-frame"><main className="main"><div className="screen"><h1>{loadError || "Unable to load your workspace."}</h1><button className="primary-button" onClick={() => { window.location.href = "/login"; }}>Sign in again</button></div></main></div>;
  const navigate = (next: Screen) => {
    setScreen(next);
    setMenuOpen(false);
    if (next === "roadmap" && project) {
      // Roadmap is the primary workflow: refresh it from current papers,
      // datasets, and gaps whenever the user opens the page.
      void generateProjectRoadmap(project.id).then(() => setResourceVersion((value) => value + 1)).catch(() => undefined);
    }
  };
  const sendToCopilot = async (message = assistantDraft, mode = assistantMode) => {
    const trimmed = message.trim();
    if (!trimmed || assistantLoading) return;
    setAssistantDraft("");
    setAssistantMessages((messages) => [...messages, { role: "user", text: trimmed }]);
    setAssistantLoading(true);
    try {
      const response = mode === "sources" ? await collectResearchSources(trimmed, project?.id, 10, Boolean(project?.id)) : await askResearchCopilot(mode === "report" ? `Create a structured research report with executive summary, key papers, datasets, research gaps, methodology, and roadmap for: ${trimmed}` : trimmed, project?.id);
      setAssistantMessages((messages) => [...messages, { role: "ai", text: response.answer, papers: response.related_papers }]);
      const sourceItems = (response as ResearchCollectionResponse).items;
      if (sourceItems?.some((item) => item.url || item.pdf_url)) {
        const links = sourceItems.filter((item) => item.url || item.pdf_url).map((item) => `${item.title}: ${item.pdf_url || item.url}`).join("\n");
        setAssistantMessages((messages) => [...messages, { role: "ai", text: `Paper links:\n${links}` }]);
      }
      if (sourceItems?.length) setAssistantMessages((messages) => [...messages, { role: "ai", text: sourceItems.map((item) => `${item.title} — ${item.source}`).join("\n") }]);
    } catch (error) {
      setAssistantMessages((messages) => [...messages, { role: "ai", text: apiErrorMessage(error, "The AI service is unavailable. Check the backend configuration.") }]);
    }
    setAssistantLoading(false);
  };
  const openCopilot = (prompt?: string) => {
    setAssistantOpen(true);
    // Natural language and greeting messages must always use chat. The
    // sources mode is reserved for the explicit Gather papers action.
    setAssistantMode("ask");
    if (prompt) {
      setAssistantDraft(prompt);
      void sendToCopilot(prompt, "ask");
    } else if (!hasAutoPrompted.current) {
      hasAutoPrompted.current = true;
      const defaultPrompt = project
        ? `Analyze my current research project (${project.title}) and identify the most important evidence gap. Research idea: ${project.research_idea}`
        : "Help me create an M.Tech research project and identify the first evidence gap to investigate.";
      setAssistantDraft(defaultPrompt);
      void sendToCopilot(defaultPrompt, "ask");
    }
  };
  const startNewChat = () => {
    hasAutoPrompted.current = true;
    setAssistantMessages([{ role: "ai", text: "New chat started. Ask me anything about your research project." }]);
    setAssistantDraft("");
    setHistoryOpen(false);
    setHistoryQuery("");
  };
  const logout = () => {
    void signOut().finally(() => {
      localStorage.removeItem("research_user");
      window.location.href = "/login";
    });
  };
  const setReminderPreference = (enabled: boolean) => {
    setRemindersEnabled(enabled);
    localStorage.setItem("roadmap_reminders_enabled", String(enabled));
  };
  const handleDocument = async (file: File) => {
    setAssistantLoading(true);
    setAssistantMessages((messages) => [...messages, { role: "user", text: `Extract notes from ${file.name}` }]);
    try {
      const response = await uploadResearchDocument(file, project?.id);
      setAssistantMessages((messages) => [...messages, { role: "ai", text: response.answer }]);
    } catch (error) {
      setAssistantMessages((messages) => [...messages, { role: "ai", text: (error as Error).message || "Document upload failed." }]);
    }
    setAssistantLoading(false);
  };
  const current = nav.find((item) => item[1] === screen);
  return (
    <div className="app-frame">
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="brand">
          <button className="brand-home" onClick={() => navigate("overview")} aria-label="Go to home">
            <div className="brand-mark">
              <Sparkles size={16} />
            </div>
            <strong>
              thesis<span>flow</span>
            </strong>
          </button>
          <button className="close-menu" onClick={() => setMenuOpen(false)}>
            <X size={18} />
          </button>
        </div>
        <button className="new-button" onClick={() => navigate("projects")}>
          <Plus size={17} /> New research
        </button>
        <nav>
          {nav.map(([label, path, Icon]) => (
            <button
              className={screen === path ? "active" : ""}
              key={path}
              onClick={() => navigate(path)}
            >
              <Icon size={17} />
              <span>{label}</span>
              {path === "gaps" && resourceCounts.gaps > 0 && <i>{resourceCounts.gaps}</i>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button onClick={() => navigate("settings")} className={screen === "settings" ? "active" : ""}>
            <Settings size={17} /> Settings
          </button>
          <button className="profile" onClick={() => setProfileOpen(true)}>
            <div className="avatar small">{user.full_name.slice(0, 2).toUpperCase()}</div>
            <div>
              <strong>{user.full_name}</strong>
              <span>{user.institution || "Researcher"}</span>
            </div>
            <ChevronRight size={15} />
          </button>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMenuOpen(true)}>
            <Menu size={20} />
          </button>
          <div className="breadcrumbs">
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>{current?.[0] || (screen === "settings" ? "Settings" : "Workspace")}</strong>
          </div>
          <div className="top-actions">
            <div className="global-search">
              <Search size={16} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(event) => { if (event.key === "Enter" && query.trim().length >= 2) { setLiteratureQuery(query.trim()); navigate("literature"); } }}
                placeholder="Search research..."
              />
              <kbd>⌘ K</kbd>
            </div>
            <button className="notification" onClick={() => setNotificationsOpen((value) => !value)} aria-label={`Notifications${reminders.length ? `, ${reminders.length} reminders` : ""}`}>
              <Bell size={18} />
              {reminders.length > 0 && <i>{reminders.length > 9 ? "9+" : reminders.length}</i>}
            </button>
            {notificationsOpen && <section className="notification-panel"><div className="notification-head"><strong>Deadline reminders</strong><button className="icon-button" onClick={() => setNotificationsOpen(false)} aria-label="Close notifications"><X size={14} /></button></div>{!remindersEnabled ? <p className="muted">Reminders are disabled in Settings.</p> : reminders.length ? <div className="notification-list">{reminders.map((reminder) => <button className="notification-item" key={reminder.id} onClick={() => { setNotificationsOpen(false); navigate("roadmap"); }}><strong>Week {reminder.week_number}: {reminder.kind === "overdue" ? "Overdue" : reminder.kind === "due_today" ? "Due today" : "Due soon"}</strong><span>{reminder.message}</span></button>)}</div> : <p className="muted">No overdue or upcoming roadmap deadlines.</p>}</section>}
            <button className="avatar profile-trigger" onClick={() => setProfileOpen(true)} aria-label="Open profile details">
              {user.full_name.slice(0, 2).toUpperCase()}
            </button>
          </div>
        </header>
        <AnimatePresence mode="wait">
          <motion.div
            key={screen}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            {screen === "overview" ? (
              <Overview onNavigate={navigate} project={project} user={user} projectCount={projects.length} resourceCounts={resourceCounts} />
            ) : screen === "projects" ? (
              <Workspace onNavigate={navigate} onOpenCopilot={openCopilot} onGenerateWorkflow={handleGenerateWorkflow} project={project} onCreateProject={handleCreateProject} resourceCounts={resourceCounts} projects={projects} onSelectProject={setSelectedProjectId} />
            ) : screen === "literature" ? (
              <><LiveResourceSummary projectId={project?.id} kind="papers" /><Literature projectId={project?.id} initialQuery={literatureQuery} /></>
            ) : screen === "settings" ? (
              <SettingsScreen user={user} remindersEnabled={remindersEnabled} onRemindersEnabledChange={setReminderPreference} onLogout={logout} />
            ) : (
              <InsightsScreen
                kind={screen as Exclude<Screen, "overview" | "literature" | "settings">}
                projectId={project?.id}
                onResourceChange={() => setResourceVersion((value) => value + 1)}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>
      <button className="ai-fab" onClick={() => openCopilot()}>
        <Sparkles size={19} />
        <span>Ask AI</span>
      </button>
      <AnimatePresence>
        {profileOpen && (
          <motion.div className="profile-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setProfileOpen(false)}>
            <motion.section className="profile-modal" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 12 }} onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="profile-title">
              <div className="profile-modal-head">
                <div><p className="eyebrow">Account</p><h2 id="profile-title">Profile details</h2></div>
                <button className="icon-button" onClick={() => setProfileOpen(false)} aria-label="Close profile details"><X size={18} /></button>
              </div>
              <div className="profile-identity">
                <div className="avatar large">{user.full_name.slice(0, 2).toUpperCase()}</div>
                <div><strong>{user.full_name}</strong><span>{user.institution || "Researcher"}</span></div>
              </div>
              <dl className="profile-details">
                <div><dt>Email</dt><dd>{user.email}</dd></div>
                <div><dt>Institution</dt><dd>{user.institution || "Not provided"}</dd></div>
                <div><dt>Status</dt><dd>{user.is_active ? "Active" : "Inactive"}</dd></div>
                <div><dt>Account ID</dt><dd>{user.id}</dd></div>
              </dl>
              <button className="logout-button" onClick={logout}><LogOut size={16} /> Log out</button>
            </motion.section>
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {assistantOpen && (
          <motion.aside
            className="ai-drawer"
            initial={{ x: 420 }}
            animate={{ x: 0 }}
            exit={{ x: 420 }}
          >
            <div className="drawer-head">
              <div>
                <p className="eyebrow">Research copilot</p>
                <h2>What are you exploring?</h2>
              </div>
              <div className="drawer-actions"><button className="text-button" type="button" onClick={startNewChat}><Plus size={14} /> New chat</button><button className="text-button" type="button" onClick={() => setHistoryOpen((value) => !value)}>Search history</button><button className="icon-button" onClick={() => setAssistantOpen(false)} aria-label="Close copilot"><X size={18} /></button></div>
            </div>
            {historyOpen && <section className="history-panel"><div className="history-search"><Search size={14} /><input value={historyQuery} onChange={(event) => setHistoryQuery(event.target.value)} placeholder="Search previous questions..." /></div>{historyLoading ? <p className="muted">Loading history...</p> : aiHistory.filter((item) => item.input_text.toLowerCase().includes(historyQuery.toLowerCase())).length ? <div className="history-list">{aiHistory.filter((item) => item.input_text.toLowerCase().includes(historyQuery.toLowerCase())).map((item) => <button type="button" className="history-item" key={item.id} onClick={() => { setAssistantDraft(item.input_text); setHistoryOpen(false); }}><span>{item.input_text}</span><small>{new Date(item.created_at).toLocaleString()}</small></button>)}</div> : <p className="muted">No previous AI searches found.</p>}</section>}
            <div className="chat" ref={chatRef}>
              {assistantMessages.map((message, index) => <div className={`ai-message ${message.role === "user" ? "user-message" : ""}`} key={`${message.role}-${index}`}><Sparkles size={16} /><AssistantText text={message.text} />{message.papers?.length ? <div className="assistant-paper-links"><strong>Related saved papers</strong>{message.papers.map((paper) => { const href = paper.url || (paper.doi ? `https://doi.org/${paper.doi}` : ""); return href ? <a href={href} target="_blank" rel="noreferrer" key={paper.title}>{paper.title}{paper.year ? ` (${paper.year})` : ""} <ArrowUpRight size={12} /></a> : <span key={paper.title}>{paper.title}</span>; })}</div> : null}</div>)}
              {assistantLoading && <div className="ai-message search-state"><Sparkles size={16} /><div className="search-state-copy"><p className="typing">Searching<span>.</span><span>.</span><span>.</span></p><div className="search-progress" aria-label="Search in progress"><i /></div></div></div>}
              <div className="copilot-tools"><button className={assistantMode === "sources" ? "selected" : ""} onClick={() => { setAssistantMode("sources"); void sendToCopilot(project ? `Find relevant scholarly papers for my project: ${project.research_idea}` : "Find relevant scholarly papers for my research topic.", "sources"); }}><BookOpen size={14} /> Gather papers</button><button className={assistantMode === "report" ? "selected" : ""} onClick={() => { setAssistantMode("report"); void sendToCopilot(project ? project.research_idea : "Create an M.Tech research report", "report"); }}><ClipboardList size={14} /> Make report</button><label><Database size={14} /> Add PDF<input type="file" accept=".pdf,.doc,.docx,.txt" onChange={(event) => { const file = event.target.files?.[0]; if (file) void handleDocument(file); }} /></label></div>
              <div className="suggestions">
                {[
                  "What are the major gaps?",
                  "Suggest a dataset",
                  "Compare these papers",
                ].map((x) => (
                  <button key={x} onClick={() => openCopilot(x)}>
                    {x}
                    <ArrowUpRight size={14} />
                  </button>
                ))}
              </div>
            </div>
            <form className="chat-input" onSubmit={(event) => { event.preventDefault(); void sendToCopilot(assistantDraft, "ask"); }}>
              <input value={assistantDraft} onChange={(event) => setAssistantDraft(event.target.value)} placeholder="Ask anything about your research..." />
              <button type="submit" disabled={assistantLoading}>
                <Send size={17} />
              </button>
            </form>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
}
