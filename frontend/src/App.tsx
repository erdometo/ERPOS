import React, { useState, useEffect } from 'react';
import { Terminal, Shield, Play, Layers, MessageSquare, Database, ArrowRight, CheckCircle2, AlertCircle, Cpu, Network, RefreshCw, AlertTriangle } from 'lucide-react';

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

      // Wrap code in a parent function to avoid top-level return issues in Babel parser
      const wrappedCode = `const __componentWrapper = (React, data, onAction) => {
        ${code}
      };`;

      // Compile JSX using Babel
      // @ts-ignore
      const compiled = window.Babel.transform(wrappedCode, {
        presets: ['react'],
      }).code || '';

      // Strip ES6 export statements which are not valid inside a function evaluator block
      const cleanCompiled = compiled
        .replace(/export\s+default\s+[\w\d_]+;?/g, '')
        .replace(/export\s+/g, '');

      // Safely evaluate code in a function context passing React, data, and onAction
      const renderFn = new Function('React', 'data', 'onAction', `
        ${cleanCompiled}
        try {
          return __componentWrapper(React, data, onAction);
        } catch(e) {
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

const EntrancePortal: React.FC<{
  onLoginSuccess: (token: string, user: any) => void;
}> = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('customer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const endpoint = isLogin ? 'login' : 'register';
      const body = isLogin 
        ? { email, password } 
        : { name, email, password, role };

      const res = await fetch(`http://localhost:8000/api/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();

      if (res.ok) {
        onLoginSuccess(data.access_token, data.user);
      } else {
        setError(data.detail || data.message || 'Authentication failed.');
      }
    } catch (err) {
      console.error(err);
      setError('Connection to security gateway failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string) => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: demoEmail, password: 'password123' }),
      });
      const data = await res.json();
      if (res.ok) {
        onLoginSuccess(data.access_token, data.user);
      } else {
        setError(data.detail || data.message || 'Demo authentication failed.');
      }
    } catch (err) {
      console.error(err);
      setError('Connection to security gateway failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans relative overflow-hidden">
      {/* Background Decorators */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-rose-500/10 rounded-full blur-3xl -z-10 animate-pulse pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-3xl -z-10 animate-pulse pointer-events-none"></div>

      <div className="max-w-md w-full bg-slate-900/40 backdrop-blur-xl border border-slate-800/80 rounded-3xl p-8 shadow-2xl space-y-6 animate-fadeIn relative">
        {/* Glow Header */}
        <div className="flex flex-col items-center text-center gap-2">
          <div className="p-3.5 bg-gradient-to-tr from-rose-500 to-violet-600 rounded-2xl shadow-xl shadow-rose-500/20 border border-rose-500/30 flex items-center justify-center mb-2">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            OmniGate ERP OS
          </h1>
          <p className="text-[10px] text-rose-400 uppercase tracking-widest font-semibold font-mono">
            Identity Security Gateway
          </p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl text-xs flex items-center gap-2 animate-shake">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block font-mono">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full Name"
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/20 transition-all shadow-inner"
              />
            </div>
          )}
          <div className="space-y-1">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block font-mono">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/20 transition-all shadow-inner"
            />
          </div>
          <div className="space-y-1">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block font-mono">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/20 transition-all shadow-inner"
            />
          </div>
          {!isLogin && (
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block font-mono">Assign Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/20 transition-all cursor-pointer"
              >
                <option value="customer">Customer</option>
                <option value="employee">Employee</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 disabled:from-slate-800 disabled:to-slate-800 text-white rounded-xl font-semibold shadow-lg shadow-rose-950/20 active:scale-95 transition-all text-sm flex items-center justify-center gap-2 mt-6"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-t-transparent border-white rounded-full animate-spin"></div>
            ) : (
              <span>{isLogin ? 'Sign In to Kernel' : 'Create Account'}</span>
            )}
          </button>
        </form>

        <div className="text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-xs text-slate-400 hover:text-slate-200 transition-all"
          >
            {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Log In'}
          </button>
        </div>

        {/* Demo Accounts Panel */}
        <div className="border-t border-slate-800/80 pt-6 space-y-3">
          <span className="text-[9px] uppercase tracking-wider text-slate-500 font-bold font-mono block text-center">
            🔐 Developer Sandbox Credentials
          </span>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleDemoLogin('alice@example.com')}
              disabled={loading}
              className="px-3 py-2 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-rose-500/20 rounded-xl text-[10px] text-rose-400 font-semibold font-mono text-left transition-all active:scale-95 flex flex-col gap-0.5"
            >
              <span>Alice Smith</span>
              <span className="text-[8px] text-slate-500 font-normal uppercase">Role: admin</span>
            </button>
            <button
              onClick={() => handleDemoLogin('bob@example.com')}
              disabled={loading}
              className="px-3 py-2 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-indigo-500/20 rounded-xl text-[10px] text-indigo-400 font-semibold font-mono text-left transition-all active:scale-95 flex flex-col gap-0.5"
            >
              <span>Bob Jones</span>
              <span className="text-[8px] text-slate-500 font-normal uppercase">Role: employee</span>
            </button>
            <button
              onClick={() => handleDemoLogin('charlie@example.com')}
              disabled={loading}
              className="px-3 py-2 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-emerald-500/20 rounded-xl text-[10px] text-emerald-400 font-semibold font-mono text-left transition-all active:scale-95 flex flex-col gap-0.5"
            >
              <span>Charlie Brown</span>
              <span className="text-[8px] text-slate-500 font-normal uppercase">Role: customer</span>
            </button>
            <button
              onClick={() => handleDemoLogin('diana@example.com')}
              disabled={loading}
              className="px-3 py-2 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-emerald-500/20 rounded-xl text-[10px] text-emerald-400 font-semibold font-mono text-left transition-all active:scale-95 flex flex-col gap-0.5"
            >
              <span>Diana Prince</span>
              <span className="text-[8px] text-slate-500 font-normal uppercase">Role: customer</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const PROGRESS_MESSAGES = [
  "Agent supervisor routing request...",
  "Running ReAct reasoning loop...",
  "Compiling UI widget...",
  "Auditing schema boundaries...",
  "Verifying ledger cryptography...",
  "Synthesizing visual components..."
];

const PremiumLoader: React.FC<{ message: string }> = ({ message }) => {
  return (
    <div className="relative w-full min-h-[400px] rounded-2xl bg-zinc-950 border border-zinc-800/80 p-8 flex flex-col items-center justify-center overflow-hidden shadow-2xl">
      {/* Glowing background highlights */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none animate-pulse"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none animate-pulse" style={{ animationDelay: '1s' }}></div>

      {/* Decorative Glowing Borders */}
      <div className="absolute inset-0 rounded-2xl border border-rose-500/20 pointer-events-none animate-pulse"></div>
      <div className="absolute inset-0.5 rounded-2xl border border-indigo-500/10 pointer-events-none animate-pulse" style={{ animationDelay: '0.5s' }}></div>

      <div className="relative flex flex-col items-center max-w-md text-center space-y-6 z-10">
        {/* Animated Custom Loader */}
        <div className="relative w-20 h-20">
          {/* Outer rotating ring */}
          <div className="absolute inset-0 border-4 border-rose-500/25 border-t-rose-500 rounded-full animate-spin"></div>
          {/* Inner counter-rotating ring */}
          <div className="absolute inset-2 border-4 border-indigo-500/25 border-b-indigo-500 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
          {/* Center glowing dot */}
          <div className="absolute inset-6 bg-gradient-to-tr from-rose-500 to-indigo-500 rounded-full shadow-lg shadow-rose-500/50 animate-pulse"></div>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-semibold tracking-wider text-rose-400 uppercase font-mono animate-pulse">
            Executing Agentic Task
          </h3>
          <p className="text-slate-200 text-base font-medium h-6 transition-all duration-300">
            {message}
          </p>
        </div>

        {/* Fancy loading dots/bar */}
        <div className="flex gap-1.5 justify-center">
          <span className="w-2.5 h-2.5 bg-rose-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
          <span className="w-2.5 h-2.5 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
          <span className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
        </div>
      </div>
    </div>
  );
};

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('erp_token'));
  const [user, setUser] = useState<{ name: string; email: string; role: string } | null>(
    localStorage.getItem('erp_user') ? JSON.parse(localStorage.getItem('erp_user')!) : null
  );

  const [question, setQuestion] = useState("Show me today's anomalous transactions");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'ui' | 'trace' | 'schema' | 'ledger' | 'data'>('ui');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [schema, setSchema] = useState<string>('');
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [ledgerData, setLedgerData] = useState<{
    is_verified: boolean;
    tampered_indices: number[];
    events: any[];
  } | null>(null);
  const [graphData, setGraphData] = useState<{
    nodes: any[];
    edges: any[];
  } | null>(null);
  const [selectedGraphNode, setSelectedGraphNode] = useState<any>(null);
  const [isVerifyingLedger, setIsVerifyingLedger] = useState(false);

  const [pendingTaskId, setPendingTaskId] = useState<string | null>(null);
  const [taskError, setTaskError] = useState<string | null>(null);
  const [progressMessageIdx, setProgressMessageIdx] = useState(0);

  const getHeaders = (hasBody = true) => {
    const headers: any = {};
    if (hasBody) {
      headers['Content-Type'] = 'application/json';
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  };

  const handleLogout = () => {
    localStorage.removeItem('erp_token');
    localStorage.removeItem('erp_user');
    setToken(null);
    setUser(null);
    setResponse(null);
  };

  // Cycle through progress messages while task is pending
  useEffect(() => {
    if (!pendingTaskId) return;
    const interval = setInterval(() => {
      setProgressMessageIdx((prev) => (prev + 1) % PROGRESS_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [pendingTaskId]);

  // Poll task status from /api/tasks/{task_id}
  useEffect(() => {
    if (!pendingTaskId) return;
    
    let isMounted = true;
    let intervalId: any = null;

    const pollTask = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/tasks/${pendingTaskId}`, {
          headers: getHeaders(false),
        });
        if (!res.ok) {
          if (res.status === 401) {
            handleLogout();
            setPendingTaskId(null);
            return;
          }
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        if (!isMounted) return;

        if (data.status === 'completed') {
          setResponse(data.result);
          setPendingTaskId(null);
          setNotification({ message: 'Task completed successfully.', type: 'success' });
          fetchSchema();
          fetchLedger();
          fetchGraph();
        } else if (data.status === 'failed') {
          setPendingTaskId(null);
          const errMsg = data.error || 'Agentic task execution failed.';
          setTaskError(errMsg);
          setNotification({ 
            message: errMsg, 
            type: 'error' 
          });
        }
      } catch (err: any) {
        console.error("Error polling task:", err);
      }
    };

    pollTask();
    intervalId = setInterval(pollTask, 1500);

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [pendingTaskId]);

  // Fetch Database Schema from server
  const fetchSchema = async () => {
    if (!token) return;
    try {
      const res = await fetch('http://localhost:8000/api/schema', {
        headers: getHeaders(false),
      });
      const data = await res.json();
      if (res.ok) {
        setSchema(data.schema);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch (err) {
      console.error("Failed to retrieve schema info", err);
    }
  };

  // Fetch Database Ledger from server
  const fetchLedger = async (showSpinner = false) => {
    if (!token) return;
    if (showSpinner) setIsVerifyingLedger(true);
    try {
      const res = await fetch('http://localhost:8000/api/ledger', {
        headers: getHeaders(false),
      });
      const data = await res.json();
      if (res.ok) {
        setLedgerData(data);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch (err) {
      console.error("Failed to retrieve ledger info", err);
    } finally {
      if (showSpinner) setIsVerifyingLedger(false);
    }
  };

  // Fetch Governance Graph from server
  const fetchGraph = async () => {
    if (!token) return;
    try {
      const res = await fetch('http://localhost:8000/api/graph', {
        headers: getHeaders(false),
      });
      const data = await res.json();
      if (res.ok) {
        setGraphData(data);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch (err) {
      console.error("Failed to retrieve graph info", err);
    }
  };

  // Send query request to API
  const handleQuery = async (queryText: string) => {
    if (!token) return;
    setLoading(true);
    setTaskError(null);
    setResponse(null); // Clear previous response
    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ question: queryText }),
      });
      const data = await res.json();
      if (res.ok) {
        if (data.task_id) {
          setPendingTaskId(data.task_id);
          setActiveTab('ui');
        } else if (data.status === 'completed') {
          setResponse(data.result);
          setActiveTab('ui');
          fetchSchema();
          fetchLedger();
          fetchGraph();
        } else {
          // Fallback if data is the old synchronous format
          setResponse(data);
          setActiveTab('ui');
          fetchSchema();
          fetchLedger();
          fetchGraph();
        }
      } else if (res.status === 401) {
        handleLogout();
      } else {
        setNotification({ message: data.detail || 'Failed to execute query.', type: 'error' });
      }
    } catch (err) {
      console.error(err);
      setNotification({ message: 'Failed to connect to ERP OS Kernel backend.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Run on mount to populate initial state and schema details
  useEffect(() => {
    if (!token) return;
    // Wait slightly to ensure Babel is fully loaded
    const timer = setTimeout(() => {
      handleQuery("Show me today's anomalous transactions");
      fetchSchema();
      fetchLedger();
      fetchGraph();
    }, 1000);
    return () => clearTimeout(timer);
  }, [token]);

  // Handle action triggers from dynamic UI
  const handleAction = async (actionId: string, params: any) => {
    try {
      let body: any = {};
      if (actionId === 'approve_waiver') {
        let orderId = null;
        if (params !== null && params !== undefined) {
          if (typeof params === 'object') {
            orderId = params.order_id ?? params.id ?? Object.values(params)[0];
          } else {
            orderId = params;
          }
        }
        if (orderId === null || orderId === undefined || orderId === '') {
          const inputId = window.prompt("Order ID was not specified by the UI. Please enter the Order ID to approve:");
          if (inputId) {
            orderId = parseInt(inputId, 10);
            if (isNaN(orderId)) {
              setNotification({ message: 'Invalid Order ID entered.', type: 'error' });
              return;
            }
          } else {
            return;
          }
        }
        body = {
          query: "UPDATE orders SET status = 'approved' WHERE id = :id",
          params: { id: orderId },
          governing_node_id: 2 // High Value Transaction Policy governance node
        };
      } else if (actionId === 'reorder_stock') {
        let productName = null;
        if (params !== null && params !== undefined) {
          if (typeof params === 'object') {
            productName = params.product_name ?? params.name ?? Object.values(params)[0];
          } else {
            productName = params;
          }
        }
        if (productName === null || productName === undefined || productName === '') {
          const inputName = window.prompt("Product Name was not specified by the UI. Please enter the Product Name to reorder:");
          if (inputName) {
            productName = inputName;
          } else {
            return;
          }
        }
        body = {
          query: "UPDATE products SET stock_quantity = stock_quantity + 50 WHERE name = :name",
          params: { name: productName },
          governing_node_id: 3 // Automated Inventory Replenishment node
        };
      } else if (actionId === 'flag_anomalies' || actionId === 'flag_all') {
        body = {
          query: "UPDATE orders SET status = 'flagged' WHERE total_amount > 500",
          params: {},
          governing_node_id: 2 // High Value Transaction Policy governance node
        };
      } else {
        // Generalized action query execution passed from the sandbox
        body = {
          query: params?.query || actionId,
          params: params?.params || params || {},
          governing_node_id: params?.governing_node_id
        };
      }

      const res = await fetch('http://localhost:8000/api/action/execute', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(body),
      });
      const result = await res.json();
      
      if (res.ok) {
        setNotification({ message: result.message || 'Action executed successfully.', type: 'success' });
        // Re-run query to refresh database state in UI, as well as ledger & graph
        handleQuery(question);
        fetchLedger();
        fetchGraph();
      } else if (res.status === 401) {
        handleLogout();
      } else {
        setNotification({ message: result.detail || result.message || 'Action execution failed.', type: 'error' });
      }
    } catch (err) {
      console.error(err);
      setNotification({ message: 'Action execution failed.', type: 'error' });
    }
  };

  if (!token) {
    return (
      <EntrancePortal
        onLoginSuccess={(jwtToken, userData) => {
          localStorage.setItem('erp_token', jwtToken);
          localStorage.setItem('erp_user', JSON.stringify(userData));
          setToken(jwtToken);
          setUser(userData);
        }}
      />
    );
  }

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
            {user && (
              <div className="flex items-center gap-3 bg-slate-900/60 border border-slate-800/80 px-3 py-1.5 rounded-xl text-xs">
                <div className="flex flex-col text-right">
                  <span className="text-slate-200 font-semibold">{user.name}</span>
                  <span className="text-[9px] uppercase tracking-wider text-rose-400 font-bold font-mono">{user.role}</span>
                </div>
                <div className="w-px h-6 bg-slate-800" />
                <button
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-rose-400 active:scale-95 transition-all font-semibold hover:underline"
                >
                  Log Out
                </button>
              </div>
            )}
            <span className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-xs text-slate-400 font-medium">
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
                disabled={loading || !!pendingTaskId}
                className="w-full min-h-[100px] bg-slate-950 border border-slate-800/80 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/20 transition-all resize-none shadow-inner disabled:opacity-50"
              />
              <button
                onClick={() => handleQuery(question)}
                disabled={loading || !!pendingTaskId}
                className="absolute bottom-3 right-3 p-2 bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 disabled:from-slate-800 disabled:to-slate-800 text-white rounded-lg shadow-lg hover:shadow-rose-500/20 active:scale-95 transition-all flex items-center justify-center"
              >
                {loading || pendingTaskId ? (
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
                      disabled={loading || !!pendingTaskId}
                      onClick={() => {
                        setQuestion(item.query);
                        handleQuery(item.query);
                      }}
                      className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-slate-400 hover:text-slate-200 transition-all flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed"
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
                      disabled={loading || !!pendingTaskId}
                      onClick={() => {
                        setQuestion(item.query);
                        handleQuery(item.query);
                      }}
                      className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-indigo-400 hover:text-indigo-200 border-indigo-950/30 hover:border-indigo-500/20 transition-all flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed"
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
                      disabled={loading || !!pendingTaskId}
                      onClick={() => {
                        setQuestion(item.query);
                        handleQuery(item.query);
                      }}
                      className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-teal-400 hover:text-teal-200 border-teal-950/30 hover:border-teal-500/20 transition-all flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed"
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
                  disabled={loading || !!pendingTaskId}
                  onClick={() => {
                    setQuestion("Trigger an infinite query loop test");
                    handleQuery("Trigger an infinite query loop test");
                  }}
                  className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-amber-400 hover:text-amber-200 border-amber-950/30 hover:border-amber-500/20 transition-all flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span>Simulate Loop Intercept</span>
                  <ArrowRight className="w-3.5 h-3.5 text-amber-800 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all" />
                </button>
              </div>

              {/* Cryptographic Compliance Chain */}
              <div className="space-y-2">
                <span className="text-[10px] text-emerald-400/80 uppercase tracking-widest font-bold font-mono">Compliance & Ledger Verification</span>
                <button
                  disabled={loading || !!pendingTaskId}
                  onClick={() => {
                    setActiveTab('ledger');
                    fetchLedger(true);
                  }}
                  className="w-full text-left px-4 py-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-900 hover:border-slate-800/80 rounded-xl text-xs text-emerald-400 hover:text-emerald-200 border-emerald-950/30 hover:border-emerald-500/20 transition-all flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span>Verify Ledger Cryptography</span>
                  <ArrowRight className="w-3.5 h-3.5 text-emerald-800 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
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
                  { id: 'ledger', label: 'Ledger Audit', icon: Shield },
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
                      {pendingTaskId ? (
                        <PremiumLoader message={PROGRESS_MESSAGES[progressMessageIdx]} />
                      ) : taskError ? (
                        <div className="p-5 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl text-sm shadow-lg backdrop-blur-sm animate-shake">
                          <div className="flex items-center gap-2 mb-2 font-semibold">
                            <AlertCircle className="w-4 h-4 text-rose-400 animate-pulse" />
                            <span>Task Execution Failed</span>
                          </div>
                          <p className="font-mono text-xs text-rose-300/80 bg-black/40 p-3 rounded-lg overflow-x-auto">{taskError}</p>
                        </div>
                      ) : response && response.ui_code ? (
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

                  {/* TAB 3: SCHEMA EXPLORER (UPGRADED) */}
                  {activeTab === 'schema' && (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between flex-wrap gap-3">
                        <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
                          <Network className="w-4 h-4 text-indigo-400 animate-pulse" />
                          <span>Governance Topology & SQL Schema Map</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
                        {/* Interactive Graph (xl:col-span-7) */}
                        <div className="xl:col-span-7 space-y-4">
                          <div className="bg-slate-950 border border-slate-900 rounded-2xl p-4 shadow-inner flex flex-col relative min-h-[360px]">
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-3">Live Active Directory Graph Nodes</span>
                            
                            {graphData && graphData.nodes && graphData.nodes.length > 0 ? (
                              <svg viewBox="0 0 500 320" className="w-full h-[280px] bg-black/35 rounded-xl border border-slate-950/50">
                                <defs>
                                  <marker id="arrow-governs" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f43f5e" />
                                  </marker>
                                  <marker id="arrow-depends" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#818cf8" />
                                  </marker>
                                  <marker id="arrow-default" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#3b82f6" />
                                  </marker>
                                </defs>

                                {/* Render Edges */}
                                {(() => {
                                  // Base coords mapping
                                  const baseCoords: { [key: number]: { x: number; y: number } } = {
                                    1: { x: 250, y: 220 },
                                    2: { x: 120, y: 80 },
                                    3: { x: 380, y: 80 },
                                  };
                                  
                                  const nodeMap: { [key: number]: { x: number; y: number } } = {};
                                  graphData.nodes.forEach((n, idx) => {
                                    if (baseCoords[n.id]) {
                                      nodeMap[n.id] = baseCoords[n.id];
                                    } else {
                                      const angle = (idx * 2 * Math.PI) / (graphData.nodes.length || 1);
                                      nodeMap[n.id] = {
                                        x: 250 + 130 * Math.cos(angle),
                                        y: 150 + 90 * Math.sin(angle)
                                      };
                                    }
                                  });

                                  return (
                                    <>
                                      {graphData.edges.map((edge) => {
                                        const src = nodeMap[edge.source];
                                        const tgt = nodeMap[edge.target];
                                        if (!src || !tgt) return null;
                                        
                                        const markerId = edge.type === 'GOVERNS' ? 'arrow-governs' : edge.type === 'DEPENDS_ON' ? 'arrow-depends' : 'arrow-default';
                                        const isGovern = edge.type === 'GOVERNS';
                                        
                                        return (
                                          <g key={edge.id} className="group">
                                            <line
                                              x1={src.x}
                                              y1={src.y}
                                              x2={tgt.x}
                                              y2={tgt.y}
                                              stroke={isGovern ? '#f43f5e' : '#818cf8'}
                                              strokeWidth={isGovern ? 2 : 1.5}
                                              strokeDasharray={edge.type === 'DEPENDS_ON' ? '4 4' : undefined}
                                              markerEnd={`url(#${markerId})`}
                                              className="transition-all duration-300 group-hover:stroke-indigo-400"
                                            />
                                            <text
                                              x={(src.x + tgt.x) / 2}
                                              y={(src.y + tgt.y) / 2 - 6}
                                              textAnchor="middle"
                                              fill="#475569"
                                              className="text-[8px] font-mono font-bold select-none pointer-events-none"
                                            >
                                              {edge.type}
                                            </text>
                                          </g>
                                        );
                                      })}

                                      {/* Render Nodes */}
                                      {graphData.nodes.map((node) => {
                                        const pos = nodeMap[node.id];
                                        const isSelected = selectedGraphNode?.id === node.id;
                                        const isRegulation = node.label === 'regulation';
                                        
                                        return (
                                          <g 
                                            key={node.id} 
                                            className="cursor-pointer group"
                                            onClick={() => setSelectedGraphNode(node)}
                                          >
                                            {/* Glow filter selection ring */}
                                            {isSelected && (
                                              <circle
                                                cx={pos.x}
                                                cy={pos.y}
                                                r="28"
                                                fill="none"
                                                stroke={isRegulation ? '#f43f5e' : '#6366f1'}
                                                strokeWidth="1.5"
                                                className="animate-ping opacity-25"
                                              />
                                            )}
                                            <circle
                                              cx={pos.x}
                                              cy={pos.y}
                                              r="22"
                                              fill={isRegulation ? '#31101b' : '#1e1b4b'}
                                              stroke={isSelected ? '#fff' : isRegulation ? '#f43f5e' : '#6366f1'}
                                              strokeWidth={isSelected ? 2.5 : 2}
                                              className="transition-all duration-300 group-hover:scale-105 group-hover:stroke-white"
                                            />
                                            {/* Node label code e.g. N1, N2 */}
                                            <text
                                              x={pos.x}
                                              y={pos.y + 4}
                                              textAnchor="middle"
                                              fill="#fff"
                                              className="text-[10px] font-mono font-extrabold select-none pointer-events-none"
                                            >
                                              N{node.id}
                                            </text>
                                            {/* Tooltip label below */}
                                            <text
                                              x={pos.x}
                                              y={pos.y + 34}
                                              textAnchor="middle"
                                              fill={isSelected ? '#fff' : '#64748b'}
                                              className="text-[9px] font-sans font-bold select-none pointer-events-none"
                                            >
                                              {node.name.length > 20 ? node.name.slice(0, 17) + '...' : node.name}
                                            </text>
                                          </g>
                                        );
                                      })}
                                    </>
                                  );
                                })()}
                              </svg>
                            ) : (
                              <div className="flex-1 flex items-center justify-center text-slate-500 italic text-xs">
                                Loading graph topology details...
                              </div>
                            )}
                          </div>

                          {/* Node details if selected */}
                          {selectedGraphNode && (
                            <div className="bg-slate-950 border border-slate-900 rounded-2xl p-5 space-y-3 animate-fadeIn">
                              <div className="flex justify-between items-start gap-4">
                                <div>
                                  <span className={`px-2 py-0.5 border rounded text-[9px] font-bold uppercase tracking-wider font-mono ${
                                    selectedGraphNode.label === 'regulation' 
                                      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
                                      : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                                  }`}>
                                    {selectedGraphNode.label}
                                  </span>
                                  <h4 className="text-sm font-bold text-slate-200 mt-1.5">{selectedGraphNode.name}</h4>
                                  <p className="text-xs text-slate-400 mt-0.5">{selectedGraphNode.description}</p>
                                </div>
                                <button 
                                  onClick={() => setSelectedGraphNode(null)}
                                  className="text-[10px] text-slate-500 hover:text-slate-300 font-semibold"
                                >
                                  Close
                                </button>
                              </div>

                              <div className="space-y-1.5 pt-2 border-t border-slate-900">
                                <span className="text-[9px] text-slate-500 font-bold uppercase font-mono">Bound rules (skill.md)</span>
                                <pre className="font-mono text-[10px] text-emerald-400/90 bg-black/40 p-3 rounded-lg overflow-y-auto max-h-[140px] whitespace-pre-wrap leading-normal border border-slate-900">
                                  {selectedGraphNode.skill_markdown}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* SQL Tabular Map (xl:col-span-5) */}
                        <div className="xl:col-span-5 space-y-4">
                          <div className="bg-slate-950 border border-slate-900 rounded-2xl p-5 shadow-inner flex flex-col h-full">
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-3">SQLite Database Tables Schema</span>
                            <pre className="font-mono text-[11px] text-emerald-400/90 bg-black/35 p-4 rounded-xl overflow-y-auto max-h-[460px] whitespace-pre-wrap leading-relaxed border border-slate-950/50">
                              {schema || "Extracting tabular schema from database..."}
                            </pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 4: LEDGER AUDIT */}
                  {activeTab === 'ledger' && (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between flex-wrap gap-4">
                        <div className="flex items-center gap-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
                          <Shield className="w-4 h-4 text-rose-400" />
                          <span>Append-Only Cryptographic Audit Ledger</span>
                        </div>
                        <button
                          onClick={() => fetchLedger(true)}
                          disabled={isVerifyingLedger}
                          className="flex items-center gap-1.5 px-3 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs text-slate-300 font-medium active:scale-95 transition-all disabled:opacity-50"
                        >
                          <RefreshCw className={`w-3.5 h-3.5 text-slate-400 ${isVerifyingLedger ? 'animate-spin' : ''}`} />
                          {isVerifyingLedger ? 'Verifying Integrity...' : 'Verify Ledger Integrity'}
                        </button>
                      </div>

                      {ledgerData ? (
                        <div className="space-y-6">
                          {/* Cryptographic Verification Status Banner */}
                          {ledgerData.is_verified ? (
                            <div className="bg-emerald-950/10 border border-emerald-500/20 p-5 rounded-2xl backdrop-blur-md shadow-lg flex items-start gap-4">
                              <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl shrink-0">
                                <Shield className="w-6 h-6 text-emerald-400 animate-pulse" />
                              </div>
                              <div className="space-y-1">
                                <h3 className="text-sm font-bold text-emerald-400">Cryptographic Verification Succeeded</h3>
                                <p className="text-xs text-slate-300">
                                  All audit records are verified. The SHA-256 block hash chain is structurally integrated. No unauthorized modifications detected.
                                </p>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-rose-950/15 border border-rose-500/30 p-5 rounded-2xl backdrop-blur-md shadow-lg flex items-start gap-4 animate-shake">
                              <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl shrink-0">
                                <AlertTriangle className="w-6 h-6 text-rose-500 animate-bounce" />
                              </div>
                              <div className="space-y-1">
                                <h3 className="text-sm font-bold text-rose-400">Ledger Cryptographic Verification Failed!</h3>
                                <p className="text-xs text-slate-300">
                                  WARNING: Unauthorized modifications or database tampering detected outside the consensus pipeline. 
                                  Tampered row indices flagged: <strong className="text-rose-400">{ledgerData.tampered_indices.join(', ')}</strong>.
                                </p>
                              </div>
                            </div>
                          )}

                          {/* Timeline of block mutations */}
                          <div className="relative border-l border-slate-800 ml-5 pl-7 space-y-6">
                            {ledgerData.events && ledgerData.events.length > 0 ? (
                              ledgerData.events.map((event) => {
                                const isTampered = ledgerData.tampered_indices.includes(event.id);
                                
                                return (
                                  <div key={event.id} className="relative group">
                                    {/* Link indicator */}
                                    <div className={`absolute -left-[35px] top-2.5 w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all ${
                                      isTampered 
                                        ? 'bg-rose-950 border-rose-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' 
                                        : 'bg-slate-950 border-slate-700 group-hover:border-emerald-500/50'
                                    }`}>
                                      {isTampered ? (
                                        <AlertCircle className="w-2.5 h-2.5 text-rose-500" />
                                      ) : (
                                        <div className="w-1.5 h-1.5 rounded-full bg-slate-700 group-hover:bg-emerald-500"></div>
                                      )}
                                    </div>

                                    {/* Event Card */}
                                    <div className={`bg-slate-900/20 border rounded-xl p-5 shadow transition-all duration-300 hover:bg-slate-900/30 ${
                                      isTampered 
                                        ? 'border-rose-500/30 shadow-[0_0_15px_rgba(239,68,68,0.15)] bg-rose-950/5' 
                                        : 'border-slate-800/80 hover:border-slate-700/80'
                                    }`}>
                                      {/* Card header */}
                                      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                                        <div className="flex items-center gap-2">
                                          <span className="font-mono text-[10px] font-bold text-slate-500">BLOCK #{event.id}</span>
                                          <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase tracking-wider ${
                                            event.action_type === 'GENESIS'
                                              ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                                              : event.action_type === 'DB_INITIALIZATION'
                                                ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                                                : event.action_type === 'SCHEMA_EVOLUTION'
                                                  ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                                                  : 'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                                          }`}>
                                            {event.action_type}
                                          </span>
                                        </div>
                                        <span className="text-[10px] text-slate-500 font-mono">{event.timestamp}</span>
                                      </div>

                                      {/* Action Agent and Details */}
                                      <div className="space-y-2 mb-4">
                                        <div className="flex items-center gap-2">
                                          <span className="text-[11px] text-slate-400 font-semibold">Agent Executor:</span>
                                          <span className="text-xs font-bold text-slate-200">{event.agent_name}</span>
                                        </div>
                                        {event.governing_node_id && (
                                          <div className="flex items-center gap-2">
                                            <span className="text-[11px] text-slate-400 font-semibold">Governance Node:</span>
                                            <span className="px-1.5 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded font-semibold text-[9px] font-mono">
                                              Node #{event.governing_node_id}
                                            </span>
                                          </div>
                                        )}
                                        <div className="mt-1 bg-black/40 rounded-lg p-3 border border-slate-900/60 shadow-inner">
                                          <span className="text-[9px] text-slate-500 font-bold uppercase block font-mono mb-1">Payload Details</span>
                                          <pre className="text-xs text-indigo-200 font-mono whitespace-pre-wrap break-all leading-normal">
                                            {typeof event.action_details === 'object' 
                                              ? JSON.stringify(event.action_details, null, 2) 
                                              : event.action_details}
                                          </pre>
                                        </div>
                                      </div>

                                      {/* Block Linkage Hashes */}
                                      <div className="pt-3 border-t border-slate-900 grid grid-cols-1 md:grid-cols-2 gap-3 text-[9px] font-mono">
                                        <div className="space-y-0.5">
                                          <span className="text-slate-500 font-semibold uppercase">PREV BLOCK LINK HASH:</span>
                                          <div className="text-slate-400 break-all bg-black/25 px-2 py-1 rounded border border-slate-950/40 select-all" title={event.prev_hash}>
                                            {event.prev_hash.slice(0, 16)}...{event.prev_hash.slice(-16)}
                                          </div>
                                        </div>
                                        <div className="space-y-0.5">
                                          <span className="text-slate-500 font-semibold uppercase">BLOCK SHA-256 SIGNATURE:</span>
                                          <div className={`${isTampered ? 'text-rose-400 bg-rose-950/10 border-rose-500/20' : 'text-emerald-400 bg-emerald-950/5 border-emerald-500/10'} break-all px-2 py-1 rounded border select-all`} title={event.row_hash}>
                                            {event.row_hash.slice(0, 16)}...{event.row_hash.slice(-16)}
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                );
                              })
                            ) : (
                              <div className="text-slate-500 italic text-xs py-8 text-center">No ledger blocks found.</div>
                            )}
                          </div>
                        </div>
                      ) : (
                        <div className="flex-1 flex flex-col justify-center items-center py-20 gap-3">
                          <div className="w-8 h-8 border-2 border-t-rose-500 border-rose-500/20 rounded-full animate-spin"></div>
                          <span className="text-xs text-slate-500 italic">Querying ledger database states...</span>
                        </div>
                      )}
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
