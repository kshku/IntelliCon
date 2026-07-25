import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const Layout: React.FC = () => {
  return (
    <div className="flex w-screen h-screen overflow-hidden bg-bg-light font-sans antialiased">
      {/* Sticky Sidebar */}
      <Sidebar />

      {/* Workspace Panel */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Navigation / Utility Bar */}
        <Header />

        {/* Scrollable Work Area */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
