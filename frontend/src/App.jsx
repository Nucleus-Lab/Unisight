import { useState } from 'react'
import Navbar from './components/layout/Navbar'
import ChatInterface from './components/layout/ChatInterface'
import TabContent from './components/TabContent'
import { ChatProvider } from './contexts/ChatContext'
import ChatToggleButton from './components/layout/ChatToggleButton'
import { PrivyProvider } from '@privy-io/react-auth';
import { CanvasProvider } from './contexts/CanvasContext';
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('canvas')
  
  console.log('Current active tab:', activeTab) // Debugging log

  return (
    <PrivyProvider
      appId={import.meta.env.VITE_PRIVY_APP_ID}
      config={{
        loginMethods: ['wallet', 'email'],
        appearance: {
          theme: 'light',
          accentColor: '#00D179',
        },
      }}
    >
      <CanvasProvider>
        <ChatProvider>
          <div className="fixed inset-0 flex flex-col">
            {/* Navbar */}
            <Navbar />
            
            {/* Main Content */}
            <div className="flex flex-col md:flex-row flex-1 min-h-0">
              <ChatInterface />
              {/* Right Side - Tab Content */}
              <div className="flex-1 min-w-0">
                <TabContent activeTab={activeTab} setActiveTab={setActiveTab} />
              </div>
            </div>

            {/* Mobile Chat Toggle Button - Fixed at bottom right on mobile */}
            <div className="md:hidden">
              <ChatToggleButton />
            </div>
          </div>
        </ChatProvider>
      </CanvasProvider>
    </PrivyProvider>
  )
}

export default App
