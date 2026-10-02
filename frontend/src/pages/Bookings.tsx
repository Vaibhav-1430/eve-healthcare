import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Calendar,
  Clock,
  ArrowRight,
  CreditCard,
  Ban,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { bookingsApi } from '../api/bookings';
import { centresApi } from '../api/centres';
import { Booking, DiagnosticCentre, PaginatedResponse } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { getErrorMessage } from '../api/client';

export const Bookings: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<PaginatedResponse<Booking> | null>(null);
  const [centresMap, setCentresMap] = useState<Record<string, DiagnosticCentre>>({});
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cancellation modal state
  const [cancelModalBooking, setCancelModalBooking] = useState<Booking | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  const fetchBookingsAndCentres = async (targetPage: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const [bookingsRes, centresRes] = await Promise.all([
        bookingsApi.getBookings(targetPage, 10),
        centresApi.getCentres(1, 50),
      ]);

      setData(bookingsRes);
      setPage(bookingsRes.page);

      const cMap: Record<string, DiagnosticCentre> = {};
      (centresRes.items || []).forEach((c) => {
        cMap[c.id] = c;
      });
      setCentresMap(cMap);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBookingsAndCentres(page);
  }, []);

  const handleCancelBooking = async () => {
    if (!cancelModalBooking) return;
    setIsCancelling(true);
    try {
      await bookingsApi.cancelBooking(cancelModalBooking.id);
      setCancelModalBooking(null);
      // Refresh current page
      await fetchBookingsAndCentres(page);
    } catch (err) {
      alert(`Cancellation failed: ${getErrorMessage(err)}`);
    } finally {
      setIsCancelling(false);
    }
  };

  const filteredItems = (data?.items || []).filter((b) => {
    if (statusFilter === 'ALL') return true;
    return b.status === statusFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">My Bookings</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage your diagnostic appointments, check payment status, or process cancellations.
          </p>
        </div>

        {/* Status filter dropdown */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 text-xs sm:text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-700"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">PENDING</option>
            <option value="CONFIRMED">CONFIRMED</option>
            <option value="FAILED">FAILED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <LoadingState message="Fetching your bookings from database..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchBookingsAndCentres(page)} />
      ) : (data?.items || []).length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No Bookings Yet"
          description="Browse our registered diagnostic centres and schedule your first laboratory test."
          actionText="Explore Centres"
          actionHref="/centres"
        />
      ) : filteredItems.length === 0 ? (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center">
          <p className="text-sm text-slate-600">No bookings match the filter "{statusFilter}".</p>
          <button
            onClick={() => setStatusFilter('ALL')}
            className="mt-3 text-xs font-medium text-teal-600 hover:underline"
          >
            Show All Bookings
          </button>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="divide-y divide-slate-100">
            {filteredItems.map((booking) => {
              const centre = centresMap[booking.diagnostic_centre_id];
              return (
                <div
                  key={booking.id}
                  className="p-5 sm:px-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 hover:bg-slate-50/50 transition-colors"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className="font-mono text-xs font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
                        #{booking.id.substring(0, 8)}
                      </span>
                      <StatusBadge status={booking.status} />
                    </div>

                    <div className="text-sm font-semibold text-slate-900">
                      {centre ? centre.name : 'Diagnostic Centre'}
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-500 flex-wrap">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        {new Date(booking.appointment_datetime).toLocaleString(undefined, {
                          dateStyle: 'medium',
                          timeStyle: 'short',
                        })}
                      </span>
                      <span>•</span>
                      <span>Created {new Date(booking.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between md:justify-end gap-3 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100">
                    <div className="text-left md:text-right mr-2">
                      <span className="text-[11px] text-slate-400 block">Amount</span>
                      <span className="text-base font-bold text-slate-900">
                        ₹{Number(booking.amount).toFixed(2)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {/* If PENDING, show Pay button */}
                      {booking.status === 'PENDING' && (
                        <>
                          <button
                            onClick={() => navigate(`/payment-demo?bookingId=${booking.id}`)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
                          >
                            <CreditCard className="w-3.5 h-3.5" />
                            <span>Pay</span>
                          </button>
                          <button
                            onClick={() => setCancelModalBooking(booking)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors border border-rose-200"
                            title="Cancel Booking"
                          >
                            <Ban className="w-3.5 h-3.5" />
                            <span className="hidden sm:inline">Cancel</span>
                          </button>
                        </>
                      )}

                      <Link
                        to={`/bookings/${booking.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
                      >
                        <span>Details</span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {data && data.pages > 1 && (
            <div className="p-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
              <span className="text-xs text-slate-500">
                Page {data.page} of {data.pages} ({data.total} records)
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => fetchBookingsAndCentres(page - 1)}
                  disabled={page <= 1}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Prev</span>
                </button>
                <button
                  onClick={() => fetchBookingsAndCentres(page + 1)}
                  disabled={page >= data.pages}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Dialog for Booking Cancellation */}
      <ConfirmDialog
        isOpen={!!cancelModalBooking}
        title="Cancel Diagnostic Booking"
        message={`Are you sure you want to cancel booking #${cancelModalBooking?.id.substring(
          0,
          8
        )}? This action transitions state to CANCELLED in PostgreSQL.`}
        confirmText="Yes, Cancel Booking"
        cancelText="Keep Booking"
        isDestructive={true}
        isLoading={isCancelling}
        onConfirm={handleCancelBooking}
        onCancel={() => setCancelModalBooking(null)}
      />
    </div>
  );
};
