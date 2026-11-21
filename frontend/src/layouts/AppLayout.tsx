import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Navbar } from '../components/Navbar';
import { BottomNav } from '../components/BottomNav';

export const AppLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-cream-100 font-sans text-charcoal-900">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 pb-24 lg:pb-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
        <BottomNav />
      </div>
    </div>
  );
};
