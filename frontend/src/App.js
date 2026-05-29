import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';
import HolographicHUD from './components/HolographicHUD';
import AgentTerminal from './components/AgentTerminal';
import CommandOrb from './components/CommandOrb';
import SystemArc from './components/SystemArc';
import LogStream from './components/LogStream';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

function App() {
  const [logs, setLogs] = useState([]);
  const [agents, setAgents] = useState({
    assistant: { status: 'idle', logs: [], lastAction: '' },
    coding: { status: 'idle', logs: [], lastAction: '' },
    device: { status: 'idle', logs: [], lastAction: '' },
    file: { status: 'idle', logs: [], lastAction: '' },
    website: { status: 'idle', logs: [], lastAction: '' },
  });
  const [activeTerminals, setActiveTerminals] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [connected, setConnected] = useState(false);
  const [response, setResponse] = useState('');
  const [processing, setProcessing] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const wsRef = useRef(null);

  const addLog = useCallback((type, message, agent = '') => {
    const entry = {
      id: Date.now() + Math.random(),
      time: new Date().toLocaleTimeString(),
      type, message, agent,
    };
    setLogs(prev => [entry, ...prev].slice(0, 200));

    if (agent) {
      setAgents(prev => ({
        ...prev,
        [agent]: {
          ...prev[agent],
          logs: [entry, ...(prev[agent]?.logs || [])].slice(0, 50),
        },
      }));
    }
  }, []);

  const openTerminal = useCallback((agentName) => {
    setActiveTerminals(prev => {
      if (prev.includes(agentName)) return prev;
      return [...prev, agentName];
    });
  }, []);

  const closeTerminal = useCallback((agentName) => {
    setActiveTerminals(prev => prev.filter(a => a !== agentName));
  }, []);

  useEffect(() => {
    const connectWS = () => {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        addLog('system', 'JARVIS Neural Link Established', '');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          addLog(data.type || 'event', data.message || JSON.stringify(data), data.agent || '');

          if (data.type === 'agent_started' && data.agent) {
            setAgents(prev => ({
              ...prev,
              [data.agent]: { ...prev[data.agent], status: 'active', lastAction: data.message },
            }));
            openTerminal(data.agent);
          } else if (data.type === 'agent_completed' && data.agent) {
            setAgents(prev => ({
              ...prev,
              [data.agent]: { ...prev[data.agent], status: 'completed', lastAction: data.message },
            }));
            setTimeout(() => {
              setAgents(prev => ({
                ...prev,
                [data.agent]: { ...prev[data.agent], status: 'idle' },
              }));
            }, 5000);
            setTimeout(() => closeTerminal(data.agent), 8000);
          }
        } catch (e) { /* ignore parse errors */ }
      };

      ws.onclose = () => {
        setConnected(false);
        addLog('system', 'Neural Link Disconnected. Reconnecting...', '');
        setTimeout(connectWS, 3000);
      };

      ws.onerror = () => ws.close();
    };

    connectWS();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [addLog, openTerminal, closeTerminal]);

  useEffect(() => {
    fetch(`${API_URL}/system/status`)
      .then(r => r.json())
      .then(setSystemStatus)
      .catch(() => {});
  }, []);

  const sendCommand = async (command) => {
    setProcessing(true);
    setResponse('');
    setCommandHistory(prev => [command, ...prev].slice(0, 20));
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

  const toggleTerminal = (agentName) => {
    if (activeTerminals.includes(agentName)) {
      closeTerminal(agentName);
    } else {
      openTerminal(agentName);
    }
  };

  return (
    <div className="jarvis-cinematic">
      <div className="grid-overlay" />
      <div className="vignette" />

      {/* Floating particles */}
      <div className="particles">
        {Array.from({ length: 30 }, (_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 8}s`,
              animationDuration: `${6 + Math.random() * 8}s`,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <header className="hud-header">
        <div className="header-left">
          <HolographicHUD processing={processing} />
          <div className="brand">
            <h1>J.A.R.V.I.S.</h1>
            <span className="tagline">ADVANCED AI OPERATING SYSTEM</span>
          </div>
        </div>
        <div className="header-center">
          <SystemArc status={systemStatus} connected={connected} />
        </div>
        <div className="header-right">
          <div className={`neural-link ${connected ? 'active' : ''}`}>
            <div className="link-pulse" />
            <span>{connected ? 'NEURAL LINK ACTIVE' : 'LINK OFFLINE'}</span>
          </div>
        </div>
      </header>

      {/* Agent selector bar */}
      <div className="agent-bar">
        {Object.entries(agents).map(([name, info]) => (
          <button
            key={name}
            className={`agent-tab ${info.status} ${activeTerminals.includes(name) ? 'open' : ''}`}
            onClick={() => toggleTerminal(name)}
          >
            <span className="tab-indicator" />
            <span className="tab-name">{name.toUpperCase()}</span>
            <span className={`tab-status ${info.status}`}>
              {info.status === 'active' ? 'RUNNING' : info.status === 'completed' ? 'DONE' : 'STANDBY'}
            </span>
          </button>
        ))}
      </div>

      {/* Main workspace */}
      <div className="workspace">
        {/* Floating agent terminals */}
        <div className="terminal-layer">
          {activeTerminals.map((agentName, index) => (
            <AgentTerminal
              key={agentName}
              name={agentName}
              info={agents[agentName]}
              index={index}
              total={activeTerminals.length}
              onClose={() => closeTerminal(agentName)}
            />
          ))}
        </div>

        {/* Central response area */}
        <div className="center-stage">
          <div className="response-hologram">
            <div className="hologram-border top-left" />
            <div className="hologram-border top-right" />
            <div className="hologram-border bottom-left" />
            <div className="hologram-border bottom-right" />
            <div className="response-label">JARVIS OUTPUT</div>
            <div className="response-text">
              {response || 'Systems nominal. Awaiting your command, sir.'}
            </div>
          </div>
        </div>

        {/* Log stream - bottom */}
        <LogStream logs={logs} />
      </div>

      {/* Command input - bottom */}
      <CommandOrb onSend={sendCommand} processing={processing} />
    </div>
  );
}

export default App;
