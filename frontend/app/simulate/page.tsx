
"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ParamVal { value: number; unit: string; symbol: string; }
interface PhysicsData {
  problem_type: string;
  parameters: Record<string, ParamVal>;
  equations: Array<{ label: string; formula: string }>;
  explanation: Array<{ step: number; text: string }>;
  key_results: Record<string, { value: number; unit: string }>;
  p5js_code: string;
  manim_code: string;
  job_id: string;
}

function buildIframeHTML(code: string, onError?: boolean): string {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #000; font-family: monospace; overflow-x: hidden; }
    canvas { display: block; }
    label { color: #777; font-size: 11px; display: block; margin: 6px 10px 2px; letter-spacing: 0.05em; text-transform: uppercase; }
    input[type=range] { accent-color: #fff; width: 200px; margin: 0 10px; cursor: pointer; vertical-align: middle; }
    button { background: #111; color: #ccc; border: 1px solid #222; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 11px; margin: 6px 10px; font-family: monospace; letter-spacing: 0.05em; }
    button:hover { background: #1a1a1a; color: #fff; }
    .controls { padding: 8px 0 4px; border-top: 1px solid #111; }
    span.val { color: #fff; font-size: 11px; margin-left: 6px; }
  </style>
</head>
<body>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.3/p5.min.js"><\/script>
  <script>
    window.onerror = function(msg, src, line, col, err) {
      window.parent.postMessage({ type: "p5error", error: msg + " (line " + line + ")" }, "*");
      return true;
    };
    try {
${code}
    } catch(e) {
      window.parent.postMessage({ type: "p5error", error: e.message }, "*");
    }
  <\/script>
</body>
</html>`;
}

function SimulatePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const question = searchParams.get("q") || "";

  const [data, setData] = useState<PhysicsData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"explanation" | "equations" | "results">("explanation");
  const [iframeSrc, setIframeSrc] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [videoStatus, setVideoStatus] = useState<"pending" | "done" | "error" | null>(null);
  const [activeView, setActiveView] = useState<"sim" | "video">("sim");
  const [p5Code, setP5Code] = useState("");
  const [fixing, setFixing] = useState(false);
  const pollRef = useRef<NodeJS.Timeout | null>(null);
  const blobRef = useRef<string>("");

  useEffect(() => {
    if (!question) { router.push("/"); return; }
    fetchSimulation(question);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [question]);

  useEffect(() => {
    if (p5Code) {
      if (blobRef.current) URL.revokeObjectURL(blobRef.current);
      const html = buildIframeHTML(p5Code);
      const blob = new Blob([html], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      blobRef.current = url;
      setIframeSrc(url);
    }
  }, [p5Code]);

  // Listen for p5.js errors from iframe
  useEffect(() => {
    const handler = async (e: MessageEvent) => {
      if (e.data?.type === "p5error" && p5Code && !fixing) {
        setFixing(true);
        try {
          const res = await fetch(`${API}/api/fix-p5js`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: p5Code, error: e.data.error, code_type: "p5js" }),
          });
          if (res.ok) {
            const json = await res.json();
            setP5Code(json.p5js_code);
          }
        } finally {
          setFixing(false);
        }
      }
    };
    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, [p5Code, fixing]);

  const startVideoPolling = (jobId: string) => {
    setVideoStatus("pending");
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/video/${jobId}`);
        if (!res.ok) return;
        const json = await res.json();
        if (json.status === "done") {
          setVideoUrl(json.url);
          setVideoStatus("done");
          if (pollRef.current) clearInterval(pollRef.current);
        } else if (json.status === "error") {
          setVideoStatus("error");
          if (pollRef.current) clearInterval(pollRef.current);
        }
      } catch {}
    }, 4000);
  };

  const fetchSimulation = async (q: string) => {
    setLoading(true);
    setError("");
    setData(null);
    setVideoUrl(null);
    setVideoStatus(null);
    if (pollRef.current) clearInterval(pollRef.current);
    try {
      const res = await fetch(`${API}/api/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to generate simulation");
      }
      const json: PhysicsData = await res.json();
      setData(json);
      setP5Code(json.p5js_code);
      startVideoPolling(json.job_id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col" style={{ height: "100vh" }}>
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 h-14 border-b border-white/5 flex-shrink-0">
        <button onClick={() => router.push("/")} className="flex items-center gap-2 text-white/40 hover:text-white transition-colors text-sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          New Problem
        </button>
        <span className="font-bold tracking-tight">Physics<span className="text-white/30">AI</span></span>
        {data ? (
          <span className="text-xs text-white/30 uppercase tracking-widest border border-white/10 px-3 py-1 rounded-full">
            {data.problem_type}
          </span>
        ) : <div className="w-28" />}
      </nav>

      {/* Question bar */}
      <div className="px-6 py-2.5 border-b border-white/5 bg-white/[0.01] flex-shrink-0">
        <p className="text-white/35 text-sm truncate">{question}</p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex-1 flex flex-col items-center justify-center gap-5">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 animate-spin text-white/30" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <span className="text-white/40">Generating simulation...</span>
          </div>
          <div className="text-white/20 text-xs text-center space-y-1.5 font-mono">
            <p>Analyzing physics principles</p>
            <p>Deriving equations</p>
            <p>Writing p5.js simulation</p>
            <p>Writing Manim animation</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div className="border border-white/10 rounded-2xl p-8 max-w-md text-center">
            <p className="text-white/50 text-sm font-medium mb-2">Generation Failed</p>
            <p className="text-white/30 text-sm mb-4">{error}</p>
            <button onClick={() => fetchSimulation(question)} className="bg-white text-black px-5 py-2 rounded-lg text-sm font-bold hover:bg-white/90">
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Main */}
      {data && !loading && (
        <div className="flex flex-1 overflow-hidden">
          {/* Left — Canvas / Video */}
          <div className="flex-1 flex flex-col bg-black border-r border-white/5 overflow-hidden">
            {/* View toggle */}
            <div className="flex items-center gap-0 border-b border-white/5 flex-shrink-0">
              <button
                onClick={() => setActiveView("sim")}
                className={`px-5 py-2.5 text-xs font-semibold uppercase tracking-widest transition-colors border-b-2 ${
                  activeView === "sim" ? "text-white border-white" : "text-white/25 border-transparent hover:text-white/50"
                }`}
              >
                Interactive Sim
              </button>
              <button
                onClick={() => setActiveView("video")}
                disabled={videoStatus !== "done"}
                className={`flex items-center gap-2 px-5 py-2.5 text-xs font-semibold uppercase tracking-widest transition-colors border-b-2 ${
                  activeView === "video" && videoStatus === "done"
                    ? "text-white border-white"
                    : "text-white/25 border-transparent"
                } disabled:cursor-not-allowed`}
              >
                Manim Video
                {videoStatus === "pending" && (
                  <svg className="w-3 h-3 animate-spin text-white/30" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                )}
                {videoStatus === "done" && <span className="w-1.5 h-1.5 rounded-full bg-white/60" />}
                {videoStatus === "error" && <span className="text-white/20">failed</span>}
              </button>
              {fixing && (
                <span className="ml-auto mr-4 text-xs text-white/25 font-mono">auto-fixing sim...</span>
              )}
            </div>

            {/* Simulation iframe */}
            {activeView === "sim" && (
              <iframe
                key={iframeSrc}
                src={iframeSrc}
                className="w-full flex-1 border-0"
                title="Physics Simulation"
                sandbox="allow-scripts"
              />
            )}

            {/* Manim video */}
            {activeView === "video" && videoStatus === "done" && videoUrl && (
              <div className="flex-1 flex items-center justify-center bg-black p-4">
                <video
                  src={videoUrl}
                  controls
                  autoPlay
                  loop
                  className="max-h-full max-w-full rounded-lg"
                  style={{ background: "#000" }}
                />
              </div>
            )}
          </div>

          {/* Right panel */}
          <div className="w-[370px] flex flex-col bg-black overflow-hidden flex-shrink-0">
            {/* Tabs */}
            <div className="flex border-b border-white/5 flex-shrink-0">
              {(["explanation", "equations", "results"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-3.5 text-xs font-semibold uppercase tracking-widest transition-colors ${
                    activeTab === tab ? "text-white border-b-2 border-white" : "text-white/25 hover:text-white/50"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-3">
              {activeTab === "explanation" && data.explanation.map((step) => (
                <div key={step.step} className="flex gap-3">
                  <span className="w-5 h-5 rounded-full bg-white/10 text-white/50 text-xs flex items-center justify-center flex-shrink-0 font-bold mt-0.5">
                    {step.step}
                  </span>
                  <p className="text-white/60 text-sm leading-relaxed">{step.text}</p>
                </div>
              ))}

              {activeTab === "equations" && data.equations.map((eq, i) => (
                <div key={i} className="border border-white/5 rounded-xl p-4 bg-white/[0.02]">
                  <p className="text-white/25 text-xs uppercase tracking-wider mb-2">{eq.label}</p>
                  <p className="text-white font-mono text-sm">{eq.formula}</p>
                </div>
              ))}

              {activeTab === "results" && Object.entries(data.key_results).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between border border-white/5 rounded-xl p-4 bg-white/[0.02]">
                  <span className="text-white/35 text-xs uppercase tracking-wider">{key.replace(/_/g, " ")}</span>
                  <span className="text-white font-mono text-sm font-bold">
                    {typeof val.value === "number" ? val.value.toFixed(2) : val.value}{" "}
                    <span className="text-white/30 font-normal">{val.unit}</span>
                  </span>
                </div>
              ))}
            </div>

            {/* Parameters */}
            <div className="border-t border-white/5 p-4 flex-shrink-0">
              <p className="text-white/20 text-xs uppercase tracking-widest mb-3 font-semibold">Parameters</p>
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(data.parameters).map(([key, p]) => (
                  <div key={key} className="bg-white/[0.03] rounded-lg p-2.5">
                    <p className="text-white/25 text-xs mb-1">{p.symbol}</p>
                    <p className="text-white text-xs font-bold font-mono">
                      {p.value} <span className="text-white/25 font-normal">{p.unit}</span>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SimulatePageWrapper() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-black flex items-center justify-center text-white/30 text-sm">Loading...</div>}>
      <SimulatePage />
    </Suspense>
  );
}
