import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  Calendar,
  Clock,
  Building2,
  Activity,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
} from 'lucide-react';
import { centresApi } from '../api/centres';
import { testsApi } from '../api/tests';
import { bookingsApi } from '../api/bookings';
import { DiagnosticCentre, DiagnosticTest, Booking } from '../types';
import { LoadingState } from '../components/LoadingState';
import { getErrorMessage } from '../api/client';

export const BookTest: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const queryCentreId = searchParams.get('centreId') || '';
  const queryTestId = searchParams.get('testId') || '';

  // Form states
  const [centres, setCentres] = useState<DiagnosticCentre[]>([]);
  const [selectedCentreId, setSelectedCentreId] = useState<string>(queryCentreId);
  const [tests, setTests] = useState<DiagnosticTest[]>([]);
  const [selectedTestId, setSelectedTestId] = useState<string>(queryTestId);

  // Default appointment date to tomorrow at 10:00 AM
  const getDefaultDatetime = () => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    d.setHours(10, 0, 0, 0);
    // Format YYYY-MM-DDTHH:mm
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const [appointmentDatetime, setAppointmentDatetime] = useState<string>(getDefaultDatetime());
  const [isLoadingCentres, setIsLoadingCentres] = useState(true);
  const [isLoadingTests, setIsLoadingTests] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmedBooking, setConfirmedBooking] = useState<Booking | null>(null);

  // Fetch all centres for the dropdown
  useEffect(() => {
    const loadCentres = async () => {
      try {
        const res = await centresApi.getCentres(1, 50);
        setCentres(res.items || []);
        if (!selectedCentreId && res.items.length > 0) {
          setSelectedCentreId(res.items[0].id);
        }
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsCentresLoading(false);
      }
    };
    loadCentres();
  }, []);

  const setIsCentresLoading = (val: boolean) => setIsLoadingCentres(val);

  // When selected centre changes, fetch its tests
  useEffect(() => {
    if (!selectedCentreId) return;

    const loadTests = async () => {
      setIsLoadingTests(true);
      setError(null);
      try {
        const res = await testsApi.getCentreTests(selectedCentreId, 1, 50);
        setTests(res.items || []);

        // If currently selected test is not in this centre's list, select first test
        if (
          !res.items.some((t) => t.id === selectedTestId) &&
          res.items.length > 0
        ) {
          setSelectedTestId(res.items[0].id);
        } else if (res.items.length === 0) {
          setSelectedTestId('');
        }
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsLoadingTests(false);
      }
    };

    loadTests();
  }, [selectedCentreId]);

  const selectedCentre = centres.find((c) => c.id === selectedCentreId);
  const selectedTest = tests.find((t) => t.id === selectedTestId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCentreId || !selectedTestId || !appointmentDatetime) {
      setError('Please select a centre, test, and appointment schedule.');
      return;
    }

    // Appointment must be in future
    const appointmentDate = new Date(appointmentDatetime);
    if (appointmentDate.getTime() <= Date.now()) {
      setError('Appointment date and time must be set in the future.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Backend expects ISO string format
      const isoDatetime = appointmentDate.toISOString();
      const booking = await bookingsApi.createBooking({
        diagnostic_centre_id: selectedCentreId,
        diagnostic_test_id: selectedTestId,
        appointment_datetime: isoDatetime,
      });

      setConfirmedBooking(booking);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingCentres) {
    return <LoadingState message="Loading diagnostic booking options..." />;
  }

  // Confirmation view
  if (confirmedBooking) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm text-center">
          <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <h2 className="text-xl font-bold text-slate-900">Booking Successfully Created!</h2>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-md mx-auto">
            Your appointment has been registered in the database with status{' '}
            <span className="font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              PENDING
            </span>
            . Complete payment to confirm.
          </p>

          <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200 text-left space-y-2.5 text-xs text-slate-600">
            <div className="flex justify-between">
              <span className="font-medium text-slate-500">Booking Reference:</span>
              <span className="font-mono font-semibold text-slate-900">{confirmedBooking.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-slate-500">Diagnostic Centre:</span>
              <span className="font-semibold text-slate-800">{selectedCentre?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-slate-500">Diagnostic Test:</span>
              <span className="font-semibold text-slate-800">{selectedTest?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-slate-500">Scheduled Time:</span>
              <span className="font-semibold text-slate-800">
                {new Date(confirmedBooking.appointment_datetime).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between pt-2 border-t border-slate-200 text-sm">
              <span className="font-bold text-slate-900">Total Payable:</span>
              <span className="font-bold text-teal-700">₹{Number(confirmedBooking.amount).toFixed(2)}</span>
            </div>
          </div>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={() => navigate(`/payment-demo?bookingId=${confirmedBooking.id}`)}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 py-2 px-5 text-xs sm:text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors"
            >
              <span>Proceed to Payment Demo</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <Link
              to={`/bookings/${confirmedBooking.id}`}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 py-2 px-4 text-xs sm:text-sm font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition-colors"
            >
              <span>View Booking Details</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back button */}
      <div>
        <Link
          to="/centres"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Diagnostic Centres</span>
        </Link>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">Book Diagnostic Appointment</h1>
            <p className="text-xs text-slate-500">
              Select your laboratory, test package, and preferred slot.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Step 1: Select Diagnostic Centre */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              1. Choose Diagnostic Centre
            </label>
            <div className="relative">
              <select
                value={selectedCentreId}
                onChange={(e) => setSelectedCentreId(e.target.value)}
                className="w-full pl-3 pr-8 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-900"
              >
                {centres.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} — {c.location}
                  </option>
                ))}
              </select>
            </div>
            {selectedCentre && (
              <p className="mt-1 text-xs text-slate-500 flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                <span>Facility Location: {selectedCentre.location}</span>
              </p>
            )}
          </div>

          {/* Step 2: Select Test */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              2. Select Diagnostic Test
            </label>
            {isLoadingTests ? (
              <div className="p-4 text-center border border-slate-200 rounded-lg text-xs text-slate-500">
                Loading available laboratory tests...
              </div>
            ) : tests.length === 0 ? (
              <div className="p-4 text-center border border-amber-200 bg-amber-50 rounded-lg text-xs text-amber-800">
                No diagnostic tests are currently available at this centre. Please choose another centre.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {tests.map((test) => {
                  const isSelected = test.id === selectedTestId;
                  return (
                    <div
                      key={test.id}
                      onClick={() => setSelectedTestId(test.id)}
                      className={`cursor-pointer p-4 rounded-xl border transition-all ${
                        isSelected
                          ? 'border-teal-500 bg-teal-50/40 ring-1 ring-teal-500 shadow-sm'
                          : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <span className="text-sm font-semibold text-slate-900">{test.name}</span>
                        <span className="text-xs font-bold text-teal-700">
                          ₹{Number(test.price).toFixed(2)}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                        {test.description || 'Standard pathology test'}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Step 3: Schedule Date and Time */}
          <div>
            <label
              htmlFor="appointment_time"
              className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2"
            >
              3. Appointment Date &amp; Time
            </label>
            <div className="relative max-w-sm">
              <input
                id="appointment_time"
                type="datetime-local"
                required
                value={appointmentDatetime}
                onChange={(e) => setAppointmentDatetime(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-900"
              />
            </div>
            <p className="mt-1 text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>Diagnostic slots must be booked for future dates.</span>
            </p>
          </div>

          {/* Summary Box */}
          {selectedTest && (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <div className="flex items-center gap-1.5 text-xs text-slate-500">
                  <ShieldCheck className="w-4 h-4 text-teal-600" />
                  <span>Amount derived automatically from backend test price</span>
                </div>
                <div className="text-sm font-semibold text-slate-800 mt-0.5">
                  {selectedTest.name}
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-500 block">Total Due</span>
                <span className="text-xl font-bold text-teal-800">
                  ₹{Number(selectedTest.price).toFixed(2)}
                </span>
              </div>
            </div>
          )}

          {/* Submit */}
          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting || !selectedTestId}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              <Calendar className="w-4 h-4" />
              <span>{isSubmitting ? 'Confirming with Backend...' : 'Confirm Appointment'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
