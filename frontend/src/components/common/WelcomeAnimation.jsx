import React, { useState, useEffect } from 'react';

const WelcomeAnimation = () => {
  const adjectives = [
    "intuitive",
    "interactive",
    "practical",
  ];
  
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  
  useEffect(() => {
    const interval = setInterval(() => {
      // Fade out
      setIsVisible(false);
      
      // Change word after fade out
      setTimeout(() => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % adjectives.length);
        setIsVisible(true);
      }, 500); // Half a second for fade out
      
    }, 3000); // Change every 3 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-800 flex items-center justify-center">
          <span>LOGO is</span>
          <span 
            className={`ml-2 transition-opacity duration-500 ${
              isVisible ? 'opacity-100' : 'opacity-0'
            }`}
            style={{ color: '#00D179' }}
          >
            {adjectives[currentIndex]}
          </span>
        </h1>
      </div>
    </div>
  );
};

export default WelcomeAnimation; 