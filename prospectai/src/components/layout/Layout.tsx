import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from '../Header';

export function Layout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-text-primary font-sans transition-colors duration-300">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:w-[280px] md:flex-col">
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto overflow-x-hidden focus:outline-none">
          <div className="h-full px-4 py-6 sm:px-6 md:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
