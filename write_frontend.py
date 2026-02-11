import os

os.makedirs('D:/Phyai/frontend/app/simulate', exist_ok=True)

# ─── globals.css ───────────────────────────────────────────────────────────────
globals_css = """@import "tailwindcss";

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

:root {
  --background: #000000;
  --foreground: #ffffff;
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: 'Space Grotesk', sans-serif;
}

* {
  box-sizing: border-box;
}

::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: #0a0a0a;
}
::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}
"""

# ─── layout.tsx ───────────────────────────────────────────────────────────────
layout_tsx = '''import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PhysicsAI",
  description: "Turn any physics problem into an interactive simulation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-black text-white min-h-screen">
        {children}
      </body>
    </html>
  );
}
'''

# ─── page.tsx (landing) ───────────────────────────────────────────────────────
page_tsx = '''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const EXAMPLES = [
  "A ball is thrown at 45 degrees with 20 m/s initial velocity. Show the projectile motion.",
  "A pendulum of length 1.5m is released from 30 degrees. Animate the oscillation.",
  "Two blocks on a frictionless inclined plane at 30 degrees. Block A is 5kg Block B is 3kg connected by rope.",
  "A 2kg object on a spring with k=50 N/m show the simple harmonic motion.",
  "A boat moves at 4 m/s across a river that flows at 3 m/s. Show relative velocity.",
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = () => {
    const q = question.trim();
    if (!q) return;
    setLoading(true);
    router.push(`/simulate?q=${encodeURIComponent(q)}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      handleSubmit();
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      <div className="mb-16 text-center">
        <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 border border-white/10 rounded-full text-xs font-semibold tracking-widest uppercase text-white/40">
          <span className="w-1.5 h-1.5 rounded-full bg-white/60 animate-pulse" />
          AI-Powered Physics Engine
        </div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-none mb-4">
          Physics<span className="text-white/30">AI</span>
        </h1>
        <p className="text-white/40 text-lg max-w-md mx-auto leading-relaxed">
          Describe any physics problem in plain English.<br />
          Get an interactive simulation instantly.
        </p>
      </div>

      <div className="w-full max-w-2xl">
        <div className="border border-white/10 rounded-2xl overflow-hidden bg-white/[0.02]">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="A 5kg block slides down a 30 degree inclined plane with friction coefficient 0.3..."
            className="w-full bg-transparent text-white placeholder-white/20 text-base p-6 resize-none outline-none min-h-[140px] font-light"
            disabled={loading}
          />
          <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
            <span className="text-white/20 text-xs">Ctrl+Enter to submit</span>
            <button
              onClick={handleSubmit}
              disabled={!question.trim() || loading}
              className="flex items-center gap-2 bg-white text-black px-6 py-2.5 rounded-xl text-sm font-bold transition-all hover:bg-white/90 disabled:opacity-20 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  Simulate
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="mt-6">
          <p className="text-white/20 text-xs uppercase tracking-widest mb-3 font-semibold">Try an example</p>
          <div className="flex flex-col gap-2">
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                onClick={() => setQuestion(ex)}
                className="text-left text-sm text-white/40 hover:text-white/70 transition-colors py-1.5 border-l-2 border-white/5 hover:border-white/30 pl-3"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
'''

# ─── simulate/page.tsx ────────────────────────────────────────────────────────
simulate_tsx = '''"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

interface ParamVal {
  value: number;
  unit: string;
  symbol: string;
}

interface PhysicsData {
  problem_type: string;
  parameters: Record<string, ParamVal>;
  equations: Array<{ label: string; formula: string }>;
  explanation: Array<{ step: number; text: string }>;
  key_results: Record<string, { value: number; unit: string }>;
  p5js_code: string;
}

function buildIframeSrc(code: string): string {
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #000; overflow: hidden; font-family: monospace; }
    canvas { display: block; }
    label { color: #888; font-size: 11px; display: block; margin: 4px 8px 1px; }
    input[type=range] { accent-color: #fff; width: 180px; margin: 0 8px; cursor: pointer; }
    button { background: #111; color: #fff; border: 1px solid #2a2a2a; padding: 5px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; margin: 4px 8px; font-family: monospace; }
    button:hover { background: #222; }
    select { background: #111; color: #fff; border: 1px solid #2a2a2a; padding: 4px 8px; border-radius: 6px; font-size: 12px; margin: 4px 8px; }
  </style>
</head>
<body>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.3/p5.min.js"></script>
  <script>
${code}
  </script>
</body>
</html>`;
  const blob = new Blob([html], { type: "text/html" });
  return URL.createObjectURL(blob);
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

  useEffect(() => {
    if (!question) {
      router.push("/");
      return;
    }
    fetchSimulation(question);
  }, [question]);

  useEffect(() => {
    if (data?.p5js_code) {
      const src = buildIframeSrc(data.p5js_code);
      setIframeSrc(src);
      return () => URL.revokeObjectURL(src);
    }
  }, [data]);

  const fetchSimulation = async (q: string) => {
    setLoading(true);
    setError("");
    setData(null);
    try {
      const res = await fetch("http://localhost:8000/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to generate simulation");
      }
      const json = await res.json();
      setData(json);
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
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 text-white/40 hover:text-white transition-colors text-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          New Problem
        </button>
        <span className="font-bold tracking-tight">
          Physics<span className="text-white/30">AI</span>
        </span>
        {data ? (
          <span className="text-xs text-white/30 uppercase tracking-widest border border-white/10 px-3 py-1 rounded-full">
            {data.problem_type}
          </span>
        ) : (
          <div className="w-24" />
        )}
      </nav>

      {/* Question bar */}
      <div className="px-6 py-3 border-b border-white/5 bg-white/[0.01] flex-shrink-0">
        <p className="text-white/40 text-sm truncate">{question}</p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex-1 flex flex-col items-center justify-center gap-6">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 animate-spin text-white/40" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <span className="text-white/40">Generating simulation...</span>
          </div>
          <div className="text-white/20 text-sm text-center space-y-1">
            <p>Analyzing physics</p>
            <p>Deriving equations</p>
            <p>Writing p5.js simulation</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-4">
          <div className="border border-white/10 rounded-2xl p-8 max-w-md text-center">
            <p className="text-white/50 text-sm font-medium mb-2">Generation Failed</p>
            <p className="text-white/30 text-sm mb-4">{error}</p>
            <button
              onClick={() => fetchSimulation(question)}
              className="bg-white text-black px-5 py-2 rounded-lg text-sm font-bold hover:bg-white/90"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Main content */}
      {data && !loading && (
        <div className="flex flex-1 overflow-hidden">
          {/* Simulation canvas */}
          <div className="flex-1 bg-black flex flex-col border-r border-white/5">
            <iframe
              src={iframeSrc}
              className="w-full flex-1 border-0"
              title="Physics Simulation"
              sandbox="allow-scripts"
            />
          </div>

          {/* Right panel */}
          <div className="w-[380px] flex flex-col bg-black overflow-hidden flex-shrink-0">
            {/* Tabs */}
            <div className="flex border-b border-white/5 flex-shrink-0">
              {(["explanation", "equations", "results"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-3.5 text-xs font-semibold uppercase tracking-widest transition-colors ${
                    activeTab === tab
                      ? "text-white border-b-2 border-white"
                      : "text-white/25 hover:text-white/50"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-y-auto p-5 space-y-3">
              {activeTab === "explanation" &&
                data.explanation.map((step) => (
                  <div key={step.step} className="flex gap-3">
                    <span className="w-5 h-5 rounded-full bg-white/10 text-white/50 text-xs flex items-center justify-center flex-shrink-0 font-bold mt-0.5">
                      {step.step}
                    </span>
                    <p className="text-white/60 text-sm leading-relaxed">{step.text}</p>
                  </div>
                ))}

              {activeTab === "equations" &&
                data.equations.map((eq, i) => (
                  <div key={i} className="border border-white/5 rounded-xl p-4 bg-white/[0.02]">
                    <p className="text-white/25 text-xs uppercase tracking-wider mb-2">{eq.label}</p>
                    <p className="text-white font-mono text-sm">{eq.formula}</p>
                  </div>
                ))}

              {activeTab === "results" &&
                Object.entries(data.key_results).map(([key, val]) => (
                  <div
                    key={key}
                    className="flex items-center justify-between border border-white/5 rounded-xl p-4 bg-white/[0.02]"
                  >
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
                      {p.value}{" "}
                      <span className="text-white/25 font-normal">{p.unit}</span>
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
    <Suspense
      fallback={
        <div className="min-h-screen bg-black flex items-center justify-center text-white/30 text-sm">
          Loading...
        </div>
      }
    >
      <SimulatePage />
    </Suspense>
  );
}
'''

# Write all files
files = {
    'D:/Phyai/frontend/app/globals.css': globals_css,
    'D:/Phyai/frontend/app/layout.tsx': layout_tsx,
    'D:/Phyai/frontend/app/page.tsx': page_tsx,
    'D:/Phyai/frontend/app/simulate/page.tsx': simulate_tsx,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written: {path}')

print('All frontend files written.')
