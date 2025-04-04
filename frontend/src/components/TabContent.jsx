import React from 'react';
import Canvas from './tabs/Canvas';
import Files from './tabs/Files';
// TODO: check if history is needed
// import History from './tabs/History';
import { useChatContext } from '../contexts/ChatContext';
import { ChatBubbleLeftIcon } from '@heroicons/react/24/outline';

const TabContent = ({ activeTab, setActiveTab }) => {
  const { isChatOpen, setIsChatOpen } = useChatContext();

  console.log('Rendering TabContent, active tab:', activeTab);

  const tabs = [
    { id: 'canvas', label: 'Canvas' },
    { id: 'files', label: 'Files' },
    // { id: 'history', label: 'History' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'canvas':
        return <Canvas />;
      case 'files':
        return <Files />;
    //   case 'history':
    //     return <History />;
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white">
        <div className="flex items-center">
          {/* Chat toggle button for tablet view */}
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className="hidden md:block lg:hidden p-2 mx-2 hover:bg-gray-100 rounded-full"
          >
            <ChatBubbleLeftIcon className="h-6 w-6" />
          </button>

          {/* Tabs */}
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 text-sm font-medium ${
                  activeTab === tab.id
                    ? 'text-[#00D179] border-b-2 border-[#00D179]'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="flex-1 p-4 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default TabContent; 