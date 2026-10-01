import React, { useState } from 'react';
import { ArrowRight, LockKeyhole, ShieldCheck } from 'lucide-react';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await onLogin(email.trim(), password);
    } catch (err) {
      setError(err.message || 'Sign-in failed. Check your details and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 p-4 sm:p-8">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl overflow-hidden rounded-2xl bg-white shadow-xl shadow-slate-900/10 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative flex min-h-64 flex-col justify-between overflow-hidden bg-emerald-950 p-8 text-white sm:p-12 lg:min-h-[680px]">
          <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(#a7f3d0 1px, transparent 1px)', backgroundSize: '22px 22px' }} />
          <div className="absolute -right-24 -top-24 h-80 w-80 rounded-full border border-emerald-300/20" />
          <div className="absolute -right-12 -top-12 h-56 w-56 rounded-full border border-emerald-300/20" />

          <div className="relative">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-400 text-emerald-950">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <span className="text-sm font-bold tracking-wide text-emerald-50">SUPPLY CHAIN INTELLIGENCE</span>
            </div>
            <div className="mt-16 max-w-lg">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-300">Operational risk, in view</p>
              <h1 className="mt-4 text-4xl font-semibold leading-tight sm:text-5xl">See disruption before it reaches the line.</h1>
              <p className="mt-5 max-w-md text-sm leading-6 text-emerald-100/75">
                A single workspace for supplier signals, inventory exposure, demand forecasts, and response planning.
              </p>
            </div>
          </div>

          <div className="relative mt-12 grid grid-cols-2 gap-3 sm:max-w-md">
            <div className="border-l border-emerald-400/60 pl-4">
              <div className="text-2xl font-semibold">25</div>
              <div className="mt-1 text-xs text-emerald-100/70">suppliers monitored</div>
            </div>
            <div className="border-l border-emerald-400/60 pl-4">
              <div className="text-2xl font-semibold">120k</div>
              <div className="mt-1 text-xs text-emerald-100/70">shipment records</div>
            </div>
          </div>
        </section>

        <section className="flex items-center justify-center px-6 py-12 sm:px-12">
          <div className="w-full max-w-sm">
            <div className="mb-10 lg:hidden">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-700 text-white">
                <ShieldCheck className="h-6 w-6" />
              </div>
            </div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-700">Workspace access</p>
            <h2 className="mt-3 text-3xl font-semibold text-slate-900">Welcome back</h2>
            <p className="mt-2 text-sm text-slate-500">Sign in to open your risk intelligence workspace.</p>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="login-email" className="mb-2 block text-sm font-semibold text-slate-700">Work email</label>
                <input
                  id="login-email"
                  type="email"
                  autoComplete="username"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@company.com"
                  className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-600 focus:ring-4 focus:ring-emerald-600/10"
                />
              </div>
              <div>
                <label htmlFor="login-password" className="mb-2 block text-sm font-semibold text-slate-700">Password</label>
                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    id="login-password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    className="w-full rounded-lg border border-slate-300 bg-white py-3 pl-10 pr-3.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-600 focus:ring-4 focus:ring-emerald-600/10"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-700 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-800 focus:outline-none focus:ring-4 focus:ring-emerald-700/20 disabled:cursor-wait disabled:opacity-60"
              >
                {submitting ? 'Signing in...' : 'Sign in'} {!submitting && <ArrowRight className="h-4 w-4" />}
              </button>
              {error && <p className="text-sm text-rose-700" role="alert">{error}</p>}
            </form>

            <p className="mt-6 border-t border-slate-200 pt-5 text-xs leading-5 text-slate-500">
              Your credentials are verified by the backend. The session uses an HttpOnly browser cookie, and your password is not saved on this device.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}