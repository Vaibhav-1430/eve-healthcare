import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  CreditCard,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { bookingsApi } from '../api/bookings';
import { centresApi } from '../api/centres';
import { testsApi } from '../api/tests';
import { paymentsApi } from '../api/payments';
import { Booking, DiagnosticCentre, DiagnosticTest, Payment, PaymentStatus } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingState } from '../components/LoadingState';
import { getErrorMessage } from '../api/client';

export const PaymentDemo: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryBookingId = searchParams.get('bookingId') || '';

  const [eligibleBookings, setEligibleBookings] = useState<Booking[]>([]);
  const [selectedBookingId, setSelectedBookingId] = useState<string>(queryBookingId);
  const [activeBooking, setActiveBooking] = useState<Booking | null>(null);
  const [activeCentre, setActiveCentre] = useState<DiagnosticCentre | null>(null);
  const [activeTest, setActiveTest] = useState<DiagnosticTest | null>(null);

  const [simulatedStatus, setSimulatedStatus] = useState<PaymentStatus>('SUCCESS');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastPaymentResult, setLastPaymentResult] = useState<Payment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load eligible bookings (PENDING or FAILED)
  const loadEligibleBookings = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await bookingsApi.getBookings(1, 50);
      const all = res.items || [];
      const eligible = all.filter((b) => b.status === 'PENDING' || b.status === 'FAILED');
      setEligibleBookings(eligible);

      // If queryBookingId exists in all, set it
      if (queryBookingId && all.some((b) => b.id === queryBookingId)) {
        setSelectedBookingId(queryBookingId);
      } else if (eligible.length > 0 && !selectedBookingId) {
        setSelectedBookingId(eligible[0].id);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEligibleBookings();
  }, []);

  // When selected booking changes, fetch active details
  useEffect(() => {
    if (!selectedBookingId) {
      setActiveBooking(null);
      return;
    }

    const fetchBookingDetails = async () => {
      try {
        const b = await bookingsApi.getBooking(selectedBookingId);
        setActiveBooking(b);

        // Fetch centre and test details
        try {
          const [c, t] = await Promise.all([
            centresApi.getCentre(b.diagnostic_centre_id),
            testsApi.getTest(b.diagnostic_test_id),
          ]);
          setActiveCentre(c);
          setActiveTest(t);
        } catch {
          // Fallback if related objects fail
        }
      } catch (err) {
        setError(getErrorMessage(err));
      }
    };

    fetchBookingDetails();
  }, [selectedBookingId]);

  const handleSimulatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBookingId || !activeBooking) {
      setError('Please choose a valid booking to process payment.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setLastPaymentResult(null);

    try {
      // Call POST /payments/ without user-supplied amount
      const paymentResponse = await paymentsApi.simulatePayment({
        booking_id: selectedBookingId,
        simulated_status: simulatedStatus,
      });

      setLastPaymentResult(paymentResponse);

      // Refetch the booking to see updated state machine transition in PostgreSQL
      // Give a tiny 400ms pause in case Celery webhook worker is processing asynchronously
      setTimeout(async () => {
        try {
          const refreshed = await bookingsApi.getBooking(selectedBookingId);
          setActiveBooking(refreshed);
        } catch {
          // ignore
        }
      }, 400);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading payment simulator..." />;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Simulation Banner */}
      <div className="bg-amber-50 border border-amber-200/80 rounded-xl p-4 flex items-start gap-3 text-amber-900">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed">
          <p className="font-semibold text-amber-900">Demo Payment Environment</p>
          <p className="text-amber-700 mt-0.5">
            This interface simulates an external payment gateway transaction. The payment amount is
            strictly derived by the backend from the booking's price. No real funds are transferred.
          </p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600">
            <CreditCard className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">Payment Simulation</h1>
            <p className="text-xs text-slate-500">
              Trigger simulated payment webhooks and inspect real-time state machine transitions.
            </p>
          </div>
        </div>

        {error && (
          <div className="mt-6 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {eligibleBookings.length === 0 && !activeBooking ? (
          <div className="py-12 text-center">
            <Clock className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-800">No Unpaid Bookings Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-5">
              All existing bookings are already confirmed, cancelled, or there are no bookings yet.
            </p>
            <Link
              to="/centres"
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors shadow-sm"
            >
              <span>Book a New Test</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSimulatePayment} className="mt-6 space-y-6">
            {/* Booking Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Select Booking to Settle
              </label>
              <select
                value={selectedBookingId}
                onChange={(e) => {
                  setSelectedBookingId(e.target.value);
                  setSearchParams({ bookingId: e.target.value });
                  setLastPaymentResult(null);
                }}
                className="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800"
              >
                {eligibleBookings.map((b) => (
                  <option key={b.id} value={b.id}>
                    Booking #{b.id.substring(0, 8)} — ₹{Number(b.amount).toFixed(2)} ({b.status})
                  </option>
                ))}
              </select>
            </div>

            {/* Active Booking Summary */}
            {activeBooking && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                  <span className="font-semibold text-slate-700 uppercase tracking-wider">
                    Booking Summary
                  </span>
                  <StatusBadge status={activeBooking.status} size="sm" />
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1 text-slate-600">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Diagnostic Centre</span>
                    <span className="font-medium text-slate-800">
                      {activeCentre?.name || 'Diagnostic Centre'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Diagnostic Test</span>
                    <span className="font-medium text-slate-800">
                      {activeTest?.name || 'Lab Test'}
                    </span>
                  </div>
                </div>
                <div className="pt-2 border-t border-slate-200 flex justify-between items-baseline">
                  <span className="text-slate-600 font-medium">Backend Verified Amount:</span>
                  <span className="text-lg font-bold text-teal-800">
                    ₹{Number(activeBooking.amount).toFixed(2)}
                  </span>
                </div>
              </div>
            )}

            {/* Simulated Outcome Choice */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Simulated Gateway Outcome
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setSimulatedStatus('SUCCESS')}
                  className={`p-3.5 rounded-xl border text-left flex items-start gap-3 transition-all ${
                    simulatedStatus === 'SUCCESS'
                      ? 'border-emerald-500 bg-emerald-50/60 ring-1 ring-emerald-500 text-emerald-900'
                      : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                  }`}
                >
                  <CheckCircle2
                    className={`w-5 h-5 shrink-0 mt-0.5 ${
                      simulatedStatus === 'SUCCESS' ? 'text-emerald-600' : 'text-slate-400'
                    }`}
                  />
                  <div>
                    <span className="text-xs font-bold block">Simulate SUCCESS</span>
                    <span className="text-[11px] text-slate-500">
                      Backend updates status to CONFIRMED
                    </span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setSimulatedStatus('FAILED')}
                  className={`p-3.5 rounded-xl border text-left flex items-start gap-3 transition-all ${
                    simulatedStatus === 'FAILED'
                      ? 'border-rose-500 bg-rose-50/60 ring-1 ring-rose-500 text-rose-900'
                      : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                  }`}
                >
                  <XCircle
                    className={`w-5 h-5 shrink-0 mt-0.5 ${
                      simulatedStatus === 'FAILED' ? 'text-rose-600' : 'text-slate-400'
                    }`}
                  />
                  <div>
                    <span className="text-xs font-bold block">Simulate FAILED</span>
                    <span className="text-[11px] text-slate-500">
                      Backend updates status to FAILED
                    </span>
                  </div>
                </button>
              </div>
            </div>

            {/* Simulation Action */}
            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                type="submit"
                disabled={isSubmitting || !activeBooking || activeBooking.status === 'CONFIRMED'}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 text-xs sm:text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Processing with Backend...</span>
                  </>
                ) : (
                  <>
                    <CreditCard className="w-4 h-4" />
                    <span>Execute Simulated Payment</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* Live Payment Execution Result */}
        {lastPaymentResult && (
          <div className="mt-8 p-5 rounded-xl border border-slate-200 bg-slate-50 space-y-3 animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                {lastPaymentResult.status === 'SUCCESS' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-600" />
                )}
                <span className="text-sm font-bold text-slate-900">
                  Transaction {lastPaymentResult.status}
                </span>
              </div>
              <StatusBadge status={lastPaymentResult.status} size="sm" />
            </div>

            <div className="space-y-1.5 text-xs text-slate-600">
              <div className="flex justify-between">
                <span className="text-slate-500">Payment ID:</span>
                <span className="font-mono text-slate-900">{lastPaymentResult.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Booking ID:</span>
                <span className="font-mono text-slate-900">{lastPaymentResult.booking_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Provider Reference:</span>
                <span className="font-mono text-slate-900">
                  {lastPaymentResult.provider_reference || 'SIM_GW_REF'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Amount Charged:</span>
                <span className="font-bold text-slate-900">
                  ₹{Number(lastPaymentResult.amount).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-200">
                <span className="text-slate-500">Live Booking State in PostgreSQL:</span>
                <span className="font-bold text-teal-700">
                  {activeBooking?.status || 'UPDATED'}
                </span>
              </div>
            </div>

            <div className="pt-3 flex justify-end">
              <Link
                to={`/bookings/${lastPaymentResult.booking_id}`}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-600 hover:text-teal-700 hover:underline"
              >
                <span>View Full Booking Record</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
