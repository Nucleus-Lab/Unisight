import React from 'react';
import { usePrivy } from '@privy-io/react-auth';

const AuthButton = () => {
  const { login, ready, authenticated, user } = usePrivy();

  // Show loading state while Privy is initializing
  if (!ready) {
    return (
      <button 
        className="px-4 py-2 bg-gray-100 text-gray-400 rounded-lg animate-pulse"
        disabled
      >
        Loading...
      </button>
    );
  }

  // If authenticated, show wallet address
  if (authenticated && user?.wallet?.address) {
    const shortAddress = `${user.wallet.address.slice(0, 6)}...${user.wallet.address.slice(-4)}`;
    
    return (
      <div className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 font-medium">
        {shortAddress}
      </div>
    );
  }

  // If not authenticated, show connect button
  return (
    <button
      onClick={() => login()}
      className="px-4 py-2 bg-[#00D179] text-white rounded-lg hover:bg-[#00BD6D] transition-colors duration-200 font-medium"
    >
      Connect Wallet
    </button>
  );
};

export default AuthButton; 