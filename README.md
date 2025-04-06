# Unisight: One-click On-Chain Data Visualizations and Insights

A decentralized application that combines AI agents, smart contracts, and a modern web interface. The project consists of four main components: AI agents for intelligent interactions, a backend server, a React frontend, and smart contracts deployed on multiple networks.

## Architecture

### 1. AI Agents
- Intelligent agents for processing and responding to user queries
- Natural language understanding and generation
- Integration with the chat interface
- MCP (Message Control Protocol) for managing agent responses

### 2. Backend
- Python-based server (>= 3.10)
- Handles communication between frontend and AI agents
- Manages webhook integrations
- API endpoints for subscription and visualization data

### 3. Frontend
- React-based web application
- Features:
  - Chat interface with AI agents
  - Subscription management
  - Visualization canvas
  - File management system
- Theme color: `#00D179`

### 4. Smart Contracts (Hardhat)
- Subscription NFT system
- Deployed on multiple networks:
  - Base Sepolia testnet: [`0xCe4a81bc23e5DA5466b3421EBb9b961b07aBd9A9`](https://sepolia.basescan.org/address/0xCe4a81bc23e5DA5466b3421EBb9b961b07aBd9A9)
  - Zircuit Garfield testnet: [`0xD63878fcE308FDc2864B296334d96403910EDb77`](https://explorer.garfield-testnet.zircuit.com/address/0xD63878fcE308FDc2864B296334d96403910EDb77)

## Getting Started

### Prerequisites
- Node.js >= 16
- Python >= 3.10
- Hardhat
- MetaMask or compatible Web3 wallet

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install AI Agents dependencies
```bash
cd agents
pip install -r requirements.txt
```

3. Install Backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

4. Install Frontend dependencies
```bash
cd frontend
npm install
```

5. Install and compile contracts
```bash
cd hardhat
npm install
npx hardhat compile
```

### Configuration

1. Set up environment variables
```bash
# Create .env files in each component directory
cp .env.example .env
```

2. Configure the following in your .env files:
- AI API keys
- Backend server URLs
- Contract addresses
- Network configurations

### Running the Project

1. Start the Backend server
```bash
uvicorn backend.main:app --reload
```

3. Start the Frontend development server
```bash
cd frontend
npm run dev
```

4. Deploy contracts (if needed)
```bash
cd hardhat
npx hardhat run scripts/deploy.js --network <network-name>
```

## Features

- 🤖 AI-powered chat interface
- 💳 NFT-based subscription system
- 📊 Interactive visualization canvas
- 📁 File management system
- 🔗 Multi-chain support
- 🎨 Modern UI with consistent branding

## Development

### Project Structure
```
├── agents/ # AI agents implementation
├── backend/ # Python backend server
├── frontend/ # React frontend application
└── hardhat/ # Smart contract development
```