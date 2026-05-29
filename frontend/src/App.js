import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';
import HUDRing from './components/HUDRing';
import AgentPanel from './components/AgentPanel';
import LogPanel from './components/LogPanel';
import CommandInput from './components/CommandInput';
import SystemStatus from './components/SystemStatus';
import ReminderPanel from './components/ReminderPanel';
import HealthPanel from './components/HealthPanel';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

function App() {
  const [logs, setLogs] = useState([]);
  const [agents, setAgents] = useState({
    assistant: { status: 'idle', lastAction: '' },
    coding: { status: 'idle', lastAction: '' },
    device: { status: 'idle', lastAction: '' },
    file: { status: 'idle', lastAction: '' },
    website: { status: 'idle', lastAction: '' },
  });
  const [systemStatus, setSystemStatus] = useState(null);
  const [connected, setConnected] = useState(false);
  const [response, setResponse] = useState('');
  const [processing, setProcessing] = useState(false);
  const wsRef = useRef(null);

  const addLog = useCallback((type, message, agent = '') => {
    const entry = {
      id: Date.now() + Math.random(),
      time: new Date().toLocaleTimeString(),
      type,
      message,
      agent,
    };
    setLogs(prev => [entry, ...prev].slice(0, 100));
  }, []);

  useEffect(() => {
    const connectWS = () => {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        addLog('system', 'WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          addLog(data.type || 'event', data.message || JSON.stringify(data), data.agent || '');

          if (data.type === 'agent_started') {
            setAgents(prev => ({
              ...prev,
              [data.agent]: { status: 'active', lastAction: data.message },
            }));
          } else if (data.type === 'agent_completed') {
            setAgents(prev => ({
              ...prev,
              [data.agent]: { status: 'idle', lastAction: data.message },
            }));
          }
        } catch (e) {
          addLog('error', 'Failed to parse message');
        }
      };

      ws.onclose = () => {
        setConnected(false);
        addLog('system', 'WebSocket disconnected. Reconnecting...');
        setTimeout(connectWS, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connectWS();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [addLog]);

  useEffect(() => {
    fetch(`${API_URL}/system/status`)
      .then(r => r.json())
      .then(setSystemStatus)
      .catch(() => {});
  }, []);

  const sendCommand = async (command) => {
    setProcessing(true);
    setResponse('');
    addLog('command', command, 'user');

    try {
      const res = await fetch(`${API_URL}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      const data = await res.json();
      setResponse(data.response || JSON.stringify(data));
      addLog('response', data.response || 'Done', data.agent || '');
    } catch (err) {
      setResponse('Connection error. Is JARVIS backend running?');
      addLog('error', err.message);
    }
    setProcessing(false);
  };

  return (
    <div className="jarvis-app">
      <div className="scanline" />
      <header className="jarvis-header">
        <HUDRing processing={processing} />
        <div className="header-text">
          <h1>J.A.R.V.I.S.</h1>
          <p className="subtitle">Just A Rather Very Intelligent System</p>
        </div>
        <div className="connection-status">
          <span className={`status-dot ${connected ? 'online' : 'offline'}`} />
          {connected ? 'CONNECTED' : 'OFFLINE'}
        </div>
      </header>

      <main className="jarvis-main">
        <div className="left-panel">
          <AgentPanel agents={agents} />
          <SystemStatus status={systemStatus} />
        </div>

        <div className="center-panel">
          <div className="response-display">
            <div className="response-header">JARVIS OUTPUT</div>
            <div className="response-content">
              {response || 'Awaiting your command, sir.'}
            </div>
          </div>
          <CommandInput onSend={sendCommand} processing={processing} />
        </div>

        <div className="right-panel">
          <ReminderPanel apiUrl={API_URL} />
          <HealthPanel apiUrl={API_URL} />
          <LogPanel logs={logs} />
        </div>
      </main>
    </div>
  );
}

export default App;
