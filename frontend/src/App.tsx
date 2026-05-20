import React, { useState, useEffect } from 'react';
import { Terminal, Shield, Play, Layers, MessageSquare, Database, ArrowRight, CheckCircle2, AlertCircle, Cpu } from 'lucide-react';

interface TraceLog {
  agent: string;
  action: string;
  details: string;
}

interface QueryResponse {
  trace: TraceLog[];
  data: any;
  ui_code: string;
}

// Dynamic Component Renderer using Babel-standalone
const DynamicRenderer: React.FC<{
  code: string;
  data: any;
  onAction: (actionId: string, params: any) => void;
}> = ({ code, data, onAction }) => {
  const [Component, setComponent] = useState<React.ComponentType<any> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!code) return;
    try {
      setError(null);
      
      // Check if Babel is available on the window
      // @ts-ignore
      if (!window.Babel) {
        throw new Error("Babel compiler is loading from CDN. Please wait a moment...");
      }

      // Compile JSX using Babel
      // @ts-ignore
      const compiled = window.Babel.transform(code, {
        presets: ['react'],
      }).code;

      // Safely evaluate code in a function context passing React, data, and onAction
      const renderFn = new Function('React', 'data', 'onAction', `
        ${compiled}
        try {
          return EphemeralDashboard;
        } catch(e) {
          // If the compiler renamed the component or created another structure
          return () => React.createElement('div', null, 'Component loaded but return target not found.');
        }
      `);

      const CompiledComponent = renderFn(React, data, onAction);
      setComponent(() => CompiledComponent);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'UI Generation Sandbox Error');
    }
  }, [code, data, onAction]);

  if (error) {
    return (
      <div className="p-5 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl text-sm shadow-lg backdrop-blur-sm animate-shake">
        <div className="flex items-center gap-2 mb-2 font-semibold">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <span>UI Generation Error</span>
        </div>
        <p className="font-mono text-xs text-rose-300/80 bg-black/40 p-3 rounded-lg overflow-x-auto">{error}</p>
      </div>
    );
  }

  if (!Component) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-500 text-sm italic gap-3">
        <div className="w-8 h-8 border-2 border-t-rose-500 border-rose-500/20 rounded-full animate-spin"></div>
        <span>Assembling dynamic interface...</span>
      </div>
    );
  }

  return (
    <div className="animate-fadeIn">
      <Component data={data} onAction={onAction} />
    </div>
  );
};

export default function App() {
  const [question, setQuestion] = useState("Show me today's anomalous transactions");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'ui' | 'trace' | 'data' | 'schema'>('ui');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [schema, setSchema] = useState<string>('');
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Fetch Database Schema from server
  const fetchSchema = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/schema');
      const data = await res.json();
      setSchema(data.schema);
    } catch (err) {
      console.error("Failed to retrieve schema info", err);
    }
  };

  // Send query request to API
  const handleQuery = async (queryText: string) => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText }),
      });
      const data = await res.json();
      setResponse(data);
      setActiveTab('ui');
      // Proactively refresh schema definitions in case of evolutionary DDL execution
      fetchSchema();
    } catch (err) {
      console.error(err);
      setNotification({ message: 'Failed to connect to ERP OS Kernel backend.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Run on mount to populate initial state and schema details
  useEffect(() => {
    // Wait slightly to ensure Babel is fully loaded
    const timer = setTimeout(() => {
      handleQuery("Show me today's anomalous transactions");
      fetchSchema();
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Handle action triggers from dynamic UI
  const handleAction = async (actionId: string, params: any) => {
    try {
      const res = await fetch('http://localhost:8000/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, params }),
      });
      const result = await res.json();
      
      if (result.status === 'success') {
        setNotification({ message: result.message, type: 'success' });
        // Re-run query to refresh database state in UI
        handleQuery(question);
      } else {
        setNotification({ message: result.message, type: 'error' });
      }
    } catch (err) {
      console.error(err);
      setNotification({ message: 'Action execution failed.', type: 'error' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans overflow-x-hidden selection:bg-rose-500/30 selection:text-white">
      {/* Background Decorators */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-rose-500/10 rounded-full blur-3xl -z-10 pointer-events-none"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -z-10 pointer-events-none"></div>

      {/* Header */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-tr from-rose-500 to-violet-600 rounded-xl shadow-lg shadow-rose-500/20 border border-rose-500/30 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                OmniGate ERP OS
              </h1>
              <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold flex items-center gap-1.5">
                <Cpu className="w-3 h-3 text-rose-500 animate-pulse" /> Agentic Kernel Interface
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-xs text-slate-400 font-medium">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></div>
              Kernel Active
            </span>
          </div>
        </div>
      </header>

      {/* Notification Toast */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 max-w-md bg-slate-900/90 backdrop-blur-md border border-slate-800 p-4 rounded-xl shadow-2xl flex items-start gap-3 animate-slideUp">
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
          )}
          <div className="flex-1">
            <p className="text-sm font-semibold text-slate-200">System Notification</p>
            <p className="text-xs text-slate-400 mt-1">{notification.message}</p>
          </div>
          <button 
            onClick={() => setNotification(null)}
            className="text-xs text-slate-500 hover:text-slate-300 ml-2"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Grid */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 w-full">
        {/* Left Column: Command & Orchestration */}
        <section className="lg:col-span-4 flex flex-col gap-6">
          <div className="bg-slate-900/40 backdrop-blur-md border border-slate-900 rounded-2xl p-6 shadow-xl space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-200">System Command</h2>
              <p className="text-xs text-slate-400">Instruct your agents directly. Evolve schema or run governed operations.</p>
            </div>

            {/* Input Bar */}
            <div className="relative">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Instruct agents..."
                className="w-full min-h-[100px] bg-slate-950 border border-slate-800/80 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/20 transition-all resize-none shadow-inner"
              />
              <button
                onClick={() => handleQuery(question)}
                disabled={loading}
                className="absolute bottom-3 right-3 p-2 bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 disabled:from-slate-800 disabled:to-slate-800 text-white rounded-lg shadow-lg hover:shadow-rose-500/20 active:scale-95 transition-all flex items-center justify-center"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-t-transparent border-white rounded-full animate-spin"></div>
                ) : (
                  <Play className="w-4 h-4" />
                )}
              </button>
            </div>

            {/* Suggestions */}
            <div className="space-y-4">
              {/* Operational Queries */}
              <div className="space-y-2">
                <span className="text-[10px] text-rose-400/80 uppercase tracking-widest font-bold font-mono">Business Operations Audits</span>
                <div className="flex flex-col gap-2">
                  {[
                    { label: "Audit Anomalous Orders", query: "Show me today's anomalous transactions" },
                    { label: "Inspect Product Inventory", query: "Inspect product stock levels" },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuestion(item.query);
                        handleQuery(item.query);
                      }}
                      className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-slate-400 hover:text-slate-200 transition-all flex items-center justify-between group"
                    >
                      <span>{item.label}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-rose-500 group-hover:translate-x-0.5 transition-all" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Evolutionary DBA Mutations */}
              <div className="space-y-2">
                <span className="text-[10px] text-indigo-400/80 uppercase tracking-widest font-bold font-mono">Evolutionary DBA Agents</span>
                <div className="flex flex-col gap-2">
                  {[
                    { label: "Add Courier details to Orders", query: "Add courier shipping details to orders table" },
                    { label: "Create Deliveries Track Table", query: "Create a shipments table to track carrier and delivery status" },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuestion(item.query);
                        handleQuery(item.query);
                      }}
                      className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-indigo-400 hover:text-indigo-200 border-indigo-950/30 hover:border-indigo-500/20 transition-all flex items-center justify-between group"
                    >
                      <span>{item.label}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-indigo-800 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Evolutionary Graph & Vector Workflows */}
              <div className="space-y-2">
                <span className="text-[10px] text-teal-400/80 uppercase tracking-widest font-bold font-mono">Evolutionary Graph & Vector Agents</span>
                <div className="flex flex-col gap-2">
                  {[
                    { label: "Evolve Graph: Express Shipping", query: "Evolve Graph: Add an Express Freight Delivery workflow to govern freight orders" },
                    { label: "Vectorize Compliance Memo", query: "Vectorize Document: Map CEO freight regulations memo to Node 3" },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuestion(item.query);
                        handleQuery(item.query);
                      }}
                      className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-teal-400 hover:text-teal-200 border-teal-950/30 hover:border-teal-500/20 transition-all flex items-center justify-between group"
                    >
                      <span>{item.label}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-teal-800 group-hover:text-teal-400 group-hover:translate-x-0.5 transition-all" />
                    </button>
                  ))}
                </div>
              </div>

              {/* FinOps Safety */}
              <div className="space-y-2">
                <span className="text-[10px] text-amber-500/80 uppercase tracking-widest font-bold font-mono">FinOps Protection Shield</span>
                <button
                  onClick={() => {
                    setQuestion("Trigger an infinite query loop test");
                    handleQuery("Trigger an infinite query loop test");
                  }}
                  className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-amber-400 hover:text-amber-200 border-amber-950/30 hover:border-amber-500/20 transition-all flex items-center justify-between group"
                >
                  <span>Simulate Loop Intercept</span>
                  <ArrowRight className="w-3.5 h-3.5 text-amber-800 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all" />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Right Column: Portal Workspace */}
        <section className="lg:col-span-8 flex flex-col gap-6">
          <div className="bg-slate-900/40 backdrop-blur-md border border-slate-900 rounded-2xl overflow-hidden shadow-xl flex flex-col h-full min-h-[550px]">
            {/* Workspace Header & Tabs */}
            <div className="px-6 py-4 bg-slate-900/60 border-b border-slate-950 flex flex-col sm:flex-row gap-4 sm:items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-rose-500" />
                <span className="text-sm font-semibold text-slate-200">Execution Workspace</span>
              </div>
              <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800/80 overflow-x-auto max-w-full">
                {[
                  { id: 'ui', label: 'Generated UI', icon: MessageSquare },
                  { id: 'trace', label: 'Agent Log Stream', icon: Terminal },
                  { id: 'schema', label: 'Schema Explorer', icon: Layers },
                  { id: 'data', label: 'Raw Payload', icon: Database },
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all shrink-0 ${
                        activeTab === tab.id
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/20 shadow'
                          : 'text-slate-400 hover:text-slate-200 border border-transparent'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {tab.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Workspace Content */}
            <div className="p-6 flex-1 flex flex-col justify-between">
              {loading ? (
                <div className="flex-1 flex flex-col justify-center items-center py-20 gap-3">
                  <div className="w-10 h-10 border-4 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-xs text-slate-500 italic">Agent Kernel routing request...</span>
                </div>
              ) : (
                <div className="flex-1">
                  {/* TAB 1: GENERATED UI */}
                  {activeTab === 'ui' && (
                    <div className="space-y-4">
                      {response && response.ui_code ? (
                        <DynamicRenderer 
                          code={response.ui_code} 
                          data={response.data} 
                          onAction={handleAction} 
                        />
                      ) : (
                        <div className="py-20 text-center text-slate-500 text-xs italic">
                          No dashboard generated yet. Submit a command to start.
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 2: AGENT TRACE LOGS */}
                  {activeTab === 'trace' && (
                    <div className="space-y-4 font-mono">
                      <div className="flex items-center gap-2 text-rose-400 text-xs font-bold uppercase tracking-wider mb-2">
                        <Terminal className="w-3.5 h-3.5 animate-pulse" />
                        <span>Real-time Multi-Agent Trajectory</span>
                      </div>
                      <div className="space-y-3 bg-black/40 border border-slate-900 p-4 rounded-xl max-h-[450px] overflow-y-auto">
                        {response && response.trace ? (
                          response.trace.map((t, idx) => (
                            <div key={idx} className="text-xs border-b border-slate-950 pb-3 last:border-0 last:pb-0">
                              <div className="flex items-center justify-between mb-1">
                                <span className={`font-bold border px-2 py-0.5 rounded text-[10px] ${
                                  t.agent.includes("Supervisor") 
                                    ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                                    : t.agent.includes("DBA")
                                      ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
                                      : t.agent.includes("Security")
                                        ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                        : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                }`}>
                                  {t.agent}
                                </span>
                                <span className="text-slate-500 text-[10px]">{t.action}</span>
                              </div>
                              <p className="text-slate-300 pl-2 border-l-2 border-slate-800 whitespace-pre-wrap">{t.details}</p>
                            </div>
                          ))
                        ) : (
                          <div className="text-center text-slate-500 italic text-xs py-10">No execution logs available.</div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* TAB 3: SCHEMA EXPLORER */}
                  {activeTab === 'schema' && (
                    <div className="space-y-4 font-mono">
                      <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
                        <Layers className="w-3.5 h-3.5" />
                        <span>Authoritative SQLite Ledger Schema Map</span>
                      </div>
                      <div className="p-5 font-mono text-xs text-emerald-400/90 bg-black/40 border border-slate-900 rounded-xl max-h-[450px] overflow-y-auto whitespace-pre-wrap leading-relaxed shadow-inner">
                        {schema ? (
                          schema
                        ) : (
                          <span className="text-slate-500 italic">Extracting schema maps from SQLite...</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* TAB 4: RAW PAYLOAD */}
                  {activeTab === 'data' && (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 text-rose-400 text-xs font-bold uppercase tracking-wider mb-2">
                        <Database className="w-3.5 h-3.5" />
                        <span>Authoritative Database Output</span>
                      </div>
                      <pre className="text-xs font-mono bg-black/40 border border-slate-900 p-4 rounded-xl max-h-[450px] overflow-y-auto text-emerald-400/90 shadow-inner">
                        {response ? (
                          JSON.stringify(response.data, null, 2)
                        ) : (
                          <span className="text-slate-500 italic">No output data retrieved yet.</span>
                        )}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
