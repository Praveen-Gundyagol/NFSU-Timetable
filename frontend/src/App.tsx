import { useState, useEffect } from 'react';
import { Calendar, CheckCircle2, AlertCircle, Building2, Users, BookOpen, Clock } from 'lucide-react';

interface HealthStatus {
  status: string;
  app: string;
  version: string;
  solver: string;
}

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Top Header */}
      <header className="bg-slate-900 text-white shadow-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-sky-600 rounded-lg">
              <Calendar className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">NFSU Timetable Generator</h1>
              <p className="text-xs text-slate-400">National Forensic Sciences University &bull; Automated Academic Scheduling</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {loading ? (
              <span className="text-xs bg-slate-800 text-slate-300 px-3 py-1.5 rounded-full flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                Connecting to Backend...
              </span>
            ) : health ? (
              <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-3 py-1.5 rounded-full flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Backend & OR-Tools Connected
              </span>
            ) : (
              <span className="text-xs bg-rose-950 text-rose-300 border border-rose-800 px-3 py-1.5 rounded-full flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                Backend Offline ({error})
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-slate-800 mb-2">Milestone 1 Verified</h2>
          <p className="text-slate-600 text-sm mb-4">
            The full-stack development environment is initialized and verified:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-sky-50 border border-sky-100 flex items-start space-x-3">
              <Clock className="h-5 w-5 text-sky-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm text-sky-900">University Config</h3>
                <p className="text-xs text-sky-700 mt-0.5">Days, Timings & Breaks</p>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-purple-50 border border-purple-100 flex items-start space-x-3">
              <Building2 className="h-5 w-5 text-purple-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm text-purple-900">Rooms & Labs</h3>
                <p className="text-xs text-purple-700 mt-0.5">Capacities & Specialties</p>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-100 flex items-start space-x-3">
              <Users className="h-5 w-5 text-emerald-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm text-emerald-900">Faculty Matrix</h3>
                <p className="text-xs text-emerald-700 mt-0.5">Availability & Max Hours</p>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-amber-50 border border-amber-100 flex items-start space-x-3">
              <BookOpen className="h-5 w-5 text-amber-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm text-amber-900">Programmes</h3>
                <p className="text-xs text-amber-700 mt-0.5">Theory & Lab Batches</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
