import React from 'react';
import { Link } from 'react-router-dom';
import AuthButton from './AuthButton';

const Navbar = () => {
  // Placeholder navigation items - can be expanded later
  const navItems = [
    // Add your navigation items here
    // { name: 'Home', path: '/' },
    // { name: 'Dashboard', path: '/dashboard' },
  ];

  return (
    <nav className="bg-white h-16">
      <div className="h-full max-w-7xl mx-auto px-4 flex items-center justify-between">
        {/* Left - Logo */}
        <div className="flex-shrink-0">
          <span className="text-xl font-semibold text-gray-800">LOGO</span>
        </div>

        {/* Center - Navigation */}
        <div className="hidden md:flex items-center justify-center flex-1 px-8">
          <div className="flex space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>

        {/* Right - Auth Button */}
        <div className="flex items-center">
          <AuthButton />
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 