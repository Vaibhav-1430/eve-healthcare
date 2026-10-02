import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  Building2,
  Clock,
  CreditCard,
  Ban,
  CheckCircle2,
  XCircle,
  FileText,
} from 'lucide-react';
import { bookingsApi } from '../api/bookings';
import { centresApi } from '../api/centres';
import { testsApi } from '../api/tests';
import { Booking, DiagnosticCentre, DiagnosticTest } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { getErrorMessage } from '../api/client';

export const BookingDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [booking, setBooking] = useState<Booking | null>(null);
  const [centre, setCentre] = useState<DiagnosticCentre | null>(null);
  const [test, setTest] = useState<DiagnosticTest | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  const fetchDetails = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const b = await bookingsApi.getBooking(id);
      setBooking(b);

      // Fetch related centre and test
      try {
        const [c, t] = await Promise.all([
          centresApi.getCentre(b.diagnostic_centre_id),
          testsApi.getTest(b.diagnostic_test_id),
        ]);
        setCentre(c);
        setTest(t);
      } catch {
        // Soft error if test or centre fetch fails
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleCancel = async () => {
    if (!booking) return;
    setIsCancelling(true);
    try {
      const updated = await bookingsApi.cancelBooking(booking.id);
      setBooking(updated);
      setIsCancelModalOpen(false);
    } catch (err) {
      alert(`Cancellation failed: ${getErrorMessage(err)}`);
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading booking details from server..." />;
  }

  if (error || !booking) {
    return (
      <ErrorState
        title="Could not load booking"
        message={error || 'Booking was not found or access denied.'}
        onRetry={fetchDetails}
      />
    );
  }

  // Determine timeline step states based on real booking status
  const isPaid = booking.status === 'CONFIRMED';
  const isFailed = booking.status === 'FAILED';
  const isCancelled = booking.status === 'CANCELLED';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top back button */}
      <div>
        <Link
          to="/bookings"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Bookings</span>
        </Link>
      </div>

      {/* Main Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold text-slate-900">
                Booking #{booking.id.substring(0, 8)}
              </h1>
              <StatusBadge status={booking.status} />
            </div>
            <p className="font-mono text-xs text-slate-400 mt-1">Full ID: {booking.id}</p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {booking.status === 'PENDING' && (
              <>
                <button
                  onClick={() => navigate(`/payment-demo?bookingId=${booking.id}`)}
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
                >
                  <CreditCard className="w-4 h-4" />
                  <span>Simulate Payment</span>
                </button>
                <button
                  onClick={() => setIsCancelModalOpen(true)}
                  className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg border border-rose-200 transition-colors"
                >
                  <Ban className="w-4 h-4" />
                  <span>Cancel Booking</span>
                </button>
              </>
            )}

            {booking.status === 'FAILED' && (
              <button
                onClick={() => navigate(`/payment-demo?bookingId=${booking.id}`)}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
              >
                <CreditCard className="w-4 h-4" />
                <span>Retry Payment</span>
              </button>
            )}
          </div>
        </div>

        {/* Visual Lifecycle Timeline */}
        <div className="py-6 border-b border-slate-200">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-6">
            Lifecycle Progress
          </h2>

          <div className="relative flex items-center justify-between max-w-2xl mx-auto px-4">
            {/* Step 1: Created */}
            <div className="flex flex-col items-center z-10">
              <div className="w-9 h-9 rounded-full bg-teal-600 text-white flex items-center justify-center shadow-sm">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <span className="text-xs font-semibold text-slate-800 mt-2">Created</span>
              <span className="text-[10px] text-slate-400">PENDING</span>
            </div>

            {/* Connecting Bar 1 */}
            <div
              className={`flex-1 h-0.5 mx-2 ${
                isPaid ? 'bg-teal-600' : isFailed ? 'bg-rose-400' : isCancelled ? 'bg-slate-300' : 'bg-slate-200'
              }`}
            />

            {/* Step 2: Payment */}
            <div className="flex flex-col items-center z-10">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center shadow-sm ${
                  isPaid
                    ? 'bg-teal-600 text-white'
                    : isFailed
                    ? 'bg-rose-600 text-white'
                    : isCancelled
                    ? 'bg-slate-200 text-slate-400'
                    : 'bg-amber-100 text-amber-700 border border-amber-300'
                }`}
              >
                {isPaid ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : isFailed ? (
                  <XCircle className="w-5 h-5" />
                ) : (
                  <CreditCard className="w-4 h-4" />
                )}
              </div>
              <span className="text-xs font-semibold text-slate-800 mt-2">Payment</span>
              <span className="text-[10px] text-slate-400">
                {isPaid ? 'Settled' : isFailed ? 'Failed' : isCancelled ? 'N/A' : 'Awaiting'}
              </span>
            </div>

            {/* Connecting Bar 2 */}
            <div
              className={`flex-1 h-0.5 mx-2 ${
                isPaid ? 'bg-emerald-600' : 'bg-slate-200'
              }`}
            />

            {/* Step 3: Confirmation */}
            <div className="flex flex-col items-center z-10">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center shadow-sm ${
                  isPaid
                    ? 'bg-emerald-600 text-white'
                    : isCancelled
                    ? 'bg-slate-300 text-slate-500'
                    : 'bg-slate-100 text-slate-400 border border-slate-200'
                }`}
              >
                {isPaid ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : isCancelled ? (
                  <Ban className="w-4 h-4" />
                ) : (
                  <Clock className="w-4 h-4" />
                )}
              </div>
              <span className="text-xs font-semibold text-slate-800 mt-2">
                {isCancelled ? 'Cancelled' : 'Confirmed'}
              </span>
              <span className="text-[10px] text-slate-400">
                {isPaid ? 'Completed' : isCancelled ? 'Void' : 'Pending'}
              </span>
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          {/* Diagnostic Centre Info */}
          <div className="bg-slate-50/60 rounded-xl p-4 border border-slate-200/80 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
              <Building2 className="w-4 h-4 text-teal-600" />
              <span>Diagnostic Facility</span>
            </div>
            <p className="font-semibold text-slate-900 text-base">
              {centre ? centre.name : 'Registered Centre'}
            </p>
            <p className="text-xs text-slate-500">{centre ? centre.location : 'Location unavailable'}</p>
            <p className="font-mono text-[11px] text-slate-400 pt-2 border-t border-slate-200">
              Centre ID: {booking.diagnostic_centre_id}
            </p>
          </div>

          {/* Test & Schedule Info */}
          <div className="bg-slate-50/60 rounded-xl p-4 border border-slate-200/80 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
              <FileText className="w-4 h-4 text-teal-600" />
              <span>Diagnostic Procedure</span>
            </div>
            <p className="font-semibold text-slate-900 text-base">{test ? test.name : 'Lab Test'}</p>
            <div className="flex items-center gap-1.5 text-xs text-slate-600">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>
                {new Date(booking.appointment_datetime).toLocaleString(undefined, {
                  dateStyle: 'full',
                  timeStyle: 'short',
                })}
              </span>
            </div>
            <p className="font-mono text-[11px] text-slate-400 pt-2 border-t border-slate-200">
              Test ID: {booking.diagnostic_test_id}
            </p>
          </div>

          {/* Financial Breakdown */}
          <div className="bg-slate-50/60 rounded-xl p-4 border border-slate-200/80 space-y-2 md:col-span-2">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
                Financial Breakdown
              </span>
              <span className="text-xs text-slate-400">Strictly derived by backend</span>
            </div>
            <div className="flex justify-between items-center text-sm py-1">
              <span className="text-slate-600">Base Lab Test Fee:</span>
              <span className="font-medium text-slate-900">₹{Number(booking.amount).toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center text-sm py-1">
              <span className="text-slate-600">Taxes &amp; Diagnostic Charges:</span>
              <span className="font-medium text-slate-900">₹0.00</span>
            </div>
            <div className="flex justify-between items-center text-base font-bold text-slate-900 pt-2 border-t border-slate-200">
              <span>Total Amount:</span>
              <span className="text-teal-700">₹{Number(booking.amount).toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog for Cancellation */}
      <ConfirmDialog
        isOpen={isCancelModalOpen}
        title="Cancel Diagnostic Booking"
        message="Are you sure you want to cancel this booking? This will execute POST /bookings/{id}/cancel on the backend."
        confirmText="Confirm Cancellation"
        cancelText="Return"
        isDestructive={true}
        isLoading={isCancelling}
        onConfirm={handleCancel}
        onCancel={() => setIsCancelModalOpen(false)}
      />
    </div>
  );
};
