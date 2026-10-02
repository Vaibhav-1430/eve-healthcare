import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  Building2,
  CreditCard,
  ArrowRight,
  PlusCircle,
  Activity,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { bookingsApi } from '../api/bookings';
import { centresApi } from '../api/centres';
import { Booking, DiagnosticCentre } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { getErrorMessage } from '../api/client';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [centresMap, setCentresMap] = useState<Record<string, DiagnosticCentre>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [bookingsData, centresData] = await Promise.all([
        bookingsApi.getBookings(1, 50),
        centresApi.getCentres(1, 50),
      ]);

      setBookings(bookingsData.items || []);

      const cMap: Record<string, DiagnosticCentre> = {};
      (centresData.items || []).forEach((c) => {
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
    fetchDashboardData();
  }, []);

  // Compute real metrics from API response
  const totalBookings = bookings.length;
  const pendingBookings = bookings.filter((b) => b.status === 'PENDING').length;
  const confirmedBookings = bookings.filter((b) => b.status === 'CONFIRMED').length;
  const failedOrCancelledBookings = bookings.filter(
    (b) => b.status === 'FAILED' || b.status === 'CANCELLED'
  ).length;

  const recentBookings = bookings.slice(0, 5);

  if (isLoading) {
    return <LoadingState message="Fetching live dashboard metrics..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchDashboardData} />;
  }

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-teal-700 uppercase tracking-wider">
              Diagnostic Overview
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
            Welcome back, {user?.full_name || 'Healthcare Practitioner'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Live diagnostic bookings and payment telemetry connected to FastAPI.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/centres"
            className="inline-flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Book New Test</span>
          </Link>
        </div>
      </div>

      {/* Real telemetry cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Total Bookings</span>
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{totalBookings}</span>
            <span className="text-[11px] text-slate-400">records</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Pending Payment</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-amber-600">{pendingBookings}</span>
            <span className="text-[11px] text-slate-400">awaiting settlement</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Confirmed Tests</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-emerald-600">{confirmedBookings}</span>
            <span className="text-[11px] text-slate-400">verified</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Failed / Cancelled</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center text-rose-600">
              <XCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-700">{failedOrCancelledBookings}</span>
            <span className="text-[11px] text-slate-400">closed</span>
          </div>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/centres"
          className="group p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-teal-400 hover:shadow transition-all"
        >
          <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
            <Building2 className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-slate-900 group-hover:text-teal-700">
            View Centres
          </h3>
          <p className="text-xs text-slate-500 mt-1">Browse diagnostic labs and available testing kits.</p>
        </Link>

        <Link
          to="/centres"
          className="group p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-teal-400 hover:shadow transition-all"
        >
          <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
            <Activity className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-slate-900 group-hover:text-teal-700">
            Book a Test
          </h3>
          <p className="text-xs text-slate-500 mt-1">Select diagnostic test and schedule an appointment.</p>
        </Link>

        <Link
          to="/bookings"
          className="group p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-teal-400 hover:shadow transition-all"
        >
          <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
            <Calendar className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-slate-900 group-hover:text-teal-700">
            My Bookings
          </h3>
          <p className="text-xs text-slate-500 mt-1">Review scheduled appointments and cancellation status.</p>
        </Link>

        <Link
          to="/payment-demo"
          className="group p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-teal-400 hover:shadow transition-all"
        >
          <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
            <CreditCard className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-slate-900 group-hover:text-teal-700">
            Payment Demo
          </h3>
          <p className="text-xs text-slate-500 mt-1">Simulate asynchronous payments &amp; Celery webhooks.</p>
        </Link>
      </div>

      {/* Recent Bookings Section */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Recent Bookings</h2>
            <p className="text-xs text-slate-500 mt-0.5">Most recent tests booked via your account</p>
          </div>
          <Link
            to="/bookings"
            className="text-xs font-semibold text-teal-600 hover:text-teal-700 flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentBookings.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-xs text-slate-500 mb-3">No bookings placed yet.</p>
            <Link
              to="/centres"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
            >
              Browse Centres &amp; Book
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {recentBookings.map((b) => (
              <div
                key={b.id}
                className="p-4 sm:px-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-slate-50/50 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-slate-700">
                      #{b.id.substring(0, 8)}
                    </span>
                    <StatusBadge status={b.status} size="sm" />
                  </div>
                  <div className="text-xs text-slate-600">
                    <span className="font-medium text-slate-900">
                      {centresMap[b.diagnostic_centre_id]?.name || 'Diagnostic Centre'}
                    </span>
                    <span className="mx-1.5 text-slate-300">•</span>
                    <span>
                      {new Date(b.appointment_datetime).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-4">
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-900">
                      ₹{Number(b.amount).toFixed(2)}
                    </span>
                  </div>
                  <Link
                    to={`/bookings/${b.id}`}
                    className="inline-flex items-center gap-1 px-3 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    <span>Details</span>
                    <ArrowRight className="w-3 h-3 text-slate-400" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
