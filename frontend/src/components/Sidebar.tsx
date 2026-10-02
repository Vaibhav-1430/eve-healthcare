import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  CalendarCheck2,
  CreditCard,
  Code2,
  LogOut,
  X,
  ExternalLink,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Diagnostic Centres', path: '/centres', icon: Building2 },
    { label: 'My Bookings', path: '/bookings', icon: CalendarCheck2 },
    { label: 'Payment Demo', path: '/payment-demo', icon: CreditCard },
    { label: 'API Showcase', path: '/api-showcase', icon: Code2 },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
    onClose();
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:z-30 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Mobile Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-100 lg:hidden">
          <span className="text-sm font-semibold text-slate-900">Navigation</span>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Section title */}
        <div className="px-4 pt-6 pb-2">
          <span className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Platform Menu
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-teal-50 text-teal-700 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Swagger link card */}
        <div className="p-3 m-3 rounded-lg bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-700 font-medium mb-1">
            <span>FastAPI Docs</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <p className="text-[11px] text-slate-500 mb-2">
            Explore live OpenAPI schema and Swagger endpoints.
          </p>
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="block w-full py-1 text-center text-xs font-medium text-teal-700 bg-white border border-teal-200 rounded hover:bg-teal-50 transition-colors"
          >
            Open Swagger
          </a>
        </div>

        {/* Bottom logout */}
        <div className="p-3 border-t border-slate-200">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};
