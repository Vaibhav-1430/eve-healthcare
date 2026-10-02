import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Building2,
  MapPin,
  Calendar,
  ArrowLeft,
  CalendarPlus,
  Clock,
} from 'lucide-react';
import { centresApi } from '../api/centres';
import { testsApi } from '../api/tests';
import { DiagnosticCentre, DiagnosticTest, PaginatedResponse } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getErrorMessage } from '../api/client';

export const CentreDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [centre, setCentre] = useState<DiagnosticCentre | null>(null);
  const [testsData, setTestsData] = useState<PaginatedResponse<DiagnosticTest>>({
    items: [],
    total: 0,
    page: 1,
    page_size: 20,
    pages: 1,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCentreAndTests = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const [centreRes, testsRes] = await Promise.all([
        centresApi.getCentre(id),
        testsApi.getCentreTests(id, 1, 50),
      ]);
      setCentre(centreRes);
      setTestsData(testsRes);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCentreAndTests();
  }, [id]);

  if (isLoading) {
    return <LoadingState message="Loading centre details and laboratory tests..." />;
  }

  if (error || !centre) {
    return (
      <ErrorState
        title="Unable to load diagnostic centre"
        message={error || 'Diagnostic centre not found.'}
        onRetry={fetchCentreAndTests}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div>
        <Link
          to="/centres"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Centres</span>
        </Link>
      </div>

      {/* Centre Header Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600 shrink-0">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-semibold tracking-wider text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200/50 uppercase">
                  Verified Lab
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mt-1">
                {centre.name}
              </h1>
              <div className="flex items-center gap-2 text-xs sm:text-sm text-slate-500 mt-1">
                <MapPin className="w-4 h-4 text-slate-400" />
                <span>{centre.location}</span>
                <span className="text-slate-300">•</span>
                <span className="font-mono text-xs text-slate-400">UUID: {centre.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Available Diagnostic Tests Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900">Available Diagnostic Tests</h2>
          <p className="text-xs text-slate-500">
            Select a test below to schedule an appointment with this diagnostic laboratory.
          </p>
        </div>
        <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200">
          {testsData.total} {testsData.total === 1 ? 'test' : 'tests'} available
        </span>
      </div>

      {/* Tests Grid */}
      {testsData.items.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No Tests Configured"
          description="This centre does not currently have any active tests configured in the system."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {testsData.items.map((test) => (
            <div
              key={test.id}
              className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:border-teal-200 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-base font-semibold text-slate-900 leading-snug">
                    {test.name}
                  </h3>
                  <div className="text-right shrink-0">
                    <span className="text-base font-bold text-slate-900">
                      ₹{Number(test.price).toFixed(2)}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-500 mt-2 line-clamp-2">
                  {test.description || 'Standard certified pathology/imaging test.'}
                </p>

                <div className="flex items-center gap-3 mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    Turnaround: 24-48 hrs
                  </span>
                  <span>•</span>
                  <span>ID: {test.id.substring(0, 8)}...</span>
                </div>
              </div>

              <div className="mt-5 pt-3">
                <Link
                  to={`/book?centreId=${centre.id}&testId=${test.id}`}
                  className="w-full inline-flex items-center justify-center gap-2 py-2 px-3 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
                >
                  <CalendarPlus className="w-4 h-4" />
                  <span>Book This Test</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
