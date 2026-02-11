"use client";

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
