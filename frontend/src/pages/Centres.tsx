import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, MapPin, ArrowRight, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import { centresApi } from '../api/centres';
import { DiagnosticCentre, PaginatedResponse } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getErrorMessage } from '../api/client';

export const Centres: React.FC = () => {
  const [data, setData] = useState<PaginatedResponse<DiagnosticCentre> | null>(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCentres = async (targetPage: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await centresApi.getCentres(targetPage, 9);
      setData(res);
      setPage(res.page);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCentres(page);
  }, []);

  const filteredCentres = (data?.items || []).filter((c) =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Diagnostic Centres</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Registered medical and diagnostic facilities offering accredited laboratory tests.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search centres or city..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs sm:text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <LoadingState message="Loading diagnostic centres..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchCentres(page)} />
      ) : (data?.items || []).length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No Diagnostic Centres Available"
          description="There are currently no diagnostic centres registered in the system."
        />
      ) : filteredCentres.length === 0 ? (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center">
          <p className="text-sm text-slate-600">No centres match your search "{searchTerm}".</p>
          <button
            onClick={() => setSearchTerm('')}
            className="mt-3 text-xs font-medium text-teal-600 hover:underline"
          >
            Clear Search
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredCentres.map((centre) => (
              <div
                key={centre.id}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:border-slate-300 hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="w-10 h-10 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                    <Building2 className="w-5 h-5" />
                  </div>

                  <h3 className="text-base font-semibold text-slate-900 leading-snug">
                    {centre.name}
                  </h3>

                  <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="truncate">{centre.location}</span>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                    <span>ID: {centre.id.substring(0, 8)}...</span>
                    <span>Accredited Lab</span>
                  </div>
                </div>

                <div className="mt-5 pt-3">
                  <Link
                    to={`/centres/${centre.id}`}
                    className="w-full inline-flex items-center justify-center gap-2 py-2 px-3 text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100/80 border border-teal-200/60 rounded-lg transition-colors"
                  >
                    <span>View Available Tests</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {data && data.pages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-slate-200">
              <span className="text-xs text-slate-500">
                Page {data.page} of {data.pages} ({data.total} total centres)
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => fetchCentres(page - 1)}
                  disabled={page <= 1}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40 transition-colors"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  onClick={() => fetchCentres(page + 1)}
                  disabled={page >= data.pages}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40 transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
