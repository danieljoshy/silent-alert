/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  ShieldAlert, 
  Camera, 
  Activity, 
  Terminal,
  AlertTriangle,
  Flame,
  Crosshair,
  Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

type AlertState = 'NORMAL' | 'CRITICAL';

interface CameraFeedProps {
  id: string;
  name: string;
  isAlerting: boolean;
  isScanning: boolean;
}

const CameraFeed = ({ id, name, isAlerting, isScanning }: CameraFeedProps) => {
  return (
    <div className={`relative aspect-video bg-slate-900 rounded-lg overflow-hidden border-2 transition-all duration-500 ${
      isAlerting ? 'border-red-600 shadow-[0_0_40px_rgba(220,38,38,0.6)] scale-[1.02] z-10' : 
      isScanning ? 'border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.2)]' : 'border-slate-800'
    }`}>
      {/* Flashing/Scanning Overlays */}
      {isAlerting && (
        <motion.div
          animate={{ opacity: [0, 1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="absolute inset-0 border-8 border-red-500 z-30 pointer-events-none"
        />
      )}
      
      {isScanning && !isAlerting && (
        <motion.div 
          initial={{ top: '-100%' }}
          animate={{ top: '100%' }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute left-0 right-0 h-1 bg-emerald-500/30 blur-sm z-20 pointer-events-none"
        />
      )}
      
      {/* Camera Header */}
      <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-black/90 to-transparent z-40 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Camera className={`w-4 h-4 ${isAlerting ? 'text-red-500' : isScanning ? 'text-emerald-500' : 'text-slate-400'}`} />
          <span className="text-[10px] font-mono font-black tracking-widest uppercase">{id}: {name}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isAlerting ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'}`} />
          <span className="text-[9px] font-mono opacity-70 tracking-tighter">LIVE_FEED</span>
        </div>
      </div>

      {/* Visual Content */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-full h-full bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-800 to-slate-950 opacity-40" />
        
        {/* CRT Scanlines */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />
        
        <Activity className={`w-16 h-16 transition-colors duration-500 ${isAlerting ? 'text-red-600/20' : isScanning ? 'text-emerald-500/10' : 'text-slate-800'}`} />
        
        {isScanning && !isAlerting && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-[10px] font-mono text-emerald-500/40 uppercase tracking-[0.3em] animate-pulse">Analyzing...</span>
          </div>
        )}
      </div>

      {/* Data Overlay */}
      <div className="absolute bottom-3 left-3 right-3 flex justify-between items-end z-40">
        <div className="flex flex-col gap-0.5">
          <span className="text-[9px] font-mono bg-black/80 px-1.5 py-0.5 rounded text-slate-400 border border-slate-800">BW: 4.2MB/S</span>
          <span className="text-[9px] font-mono bg-black/80 px-1.5 py-0.5 rounded text-slate-400 border border-slate-800">SIG: 98%</span>
        </div>
        <div className="text-[9px] font-mono text-slate-500 bg-black/40 px-1 rounded">
          {new Date().toISOString().split('T')[1].split('.')[0]}
        </div>
      </div>
    </div>
  );
};

export default function App() {
  const [state, setState] = useState<AlertState>('NORMAL');
  const [cycle, setCycle] = useState(0);
  const [logs, setLogs] = useState<string[]>(["[SYSTEM] Initialization complete.", "[AI] Monitoring protocols engaged."]);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Autonomous State Machine Loop
  useEffect(() => {
    const interval = setInterval(() => {
      setCycle(prev => prev + 1);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (state === 'CRITICAL') return;

    if (cycle > 0 && cycle < 6) {
      const camId = (cycle % 4) || 4;
      const newLog = `[SCAN] Analyzing Camera ${camId}... Clear.`;
      setLogs(prev => [newLog, ...prev].slice(0, 100));
    }

    // Autonomous Trigger on 6th cycle
    if (cycle === 6) {
      setState('CRITICAL');
      setLogs(prev => [
        "CRITICAL: THERMAL ANOMALY DETECTED",
        "ALERT: FIRE SIGNATURE CONFIRMED IN KITCHEN",
        "EMERGENCY PROTOCOL DELTA-9 ACTIVATED",
        ...prev
      ]);
    }
  }, [cycle, state]);

  return (
    <div className="min-h-screen bg-[#020408] text-slate-100 font-sans overflow-hidden">
      {/* Header */}
      <header className="h-20 border-b border-slate-800/50 flex items-center justify-between px-8 bg-[#020408]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className={`absolute inset-0 blur-lg opacity-50 ${state === 'NORMAL' ? 'bg-emerald-500' : 'bg-red-600'}`} />
            <div className={`relative p-2.5 rounded-lg border ${state === 'NORMAL' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-600/10 border-red-600/20'}`}>
              <Shield className={`w-7 h-7 ${state === 'NORMAL' ? 'text-emerald-500' : 'text-red-600'}`} />
            </div>
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tighter text-white">SILENT ALARM <span className="text-slate-500 font-light">| COMMAND CENTER</span></h1>
            <div className="flex items-center gap-2 mt-0.5">
              <div className="flex gap-1">
                {[1, 2, 3].map(i => (
                  <div key={i} className="w-1 h-1 bg-slate-700 rounded-full" />
                ))}
              </div>
              <p className="text-[9px] font-mono text-slate-500 uppercase tracking-[0.2em]">Autonomous Response System v4.2</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-8">
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-2">
              <motion.div 
                animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className={`w-2.5 h-2.5 rounded-full ${state === 'NORMAL' ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-red-600 shadow-[0_0_10px_#dc2626]'}`} 
              />
              <span className={`text-xs font-black tracking-widest uppercase ${state === 'NORMAL' ? 'text-emerald-500' : 'text-red-500'}`}>
                {state === 'NORMAL' ? 'System Online & Monitoring...' : 'CRITICAL THREAT DETECTED'}
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-500 mt-1">NODE: HKG-SEC-09 // UPTIME: 142:12:05</p>
          </div>
        </div>
      </header>

      <main className="p-8 max-w-[1800px] mx-auto">
        {/* Autonomous Alert Banner */}
        <AnimatePresence>
          {state === 'CRITICAL' && (
            <motion.div
              initial={{ y: -100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="mb-8"
            >
              <div className="bg-red-600 p-8 rounded-2xl flex items-center justify-between shadow-[0_0_50px_rgba(220,38,38,0.4)] relative overflow-hidden border-b-4 border-red-800">
                <motion.div 
                  animate={{ opacity: [0, 0.2, 0] }}
                  transition={{ duration: 0.3, repeat: Infinity }}
                  className="absolute inset-0 bg-white"
                />
                
                <div className="relative z-10 flex items-center gap-8">
                  <div className="p-5 bg-white/10 rounded-2xl backdrop-blur-md border border-white/20">
                    <Flame className="w-12 h-12 text-white animate-pulse" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="bg-white text-red-600 text-[11px] font-black px-3 py-1 rounded-full uppercase tracking-widest">Threat Level: Critical</span>
                      <span className="text-white/60 text-[10px] font-mono tracking-[0.3em]">CODE: RED-DELTA</span>
                    </div>
                    <h2 className="text-5xl font-black text-white uppercase tracking-tighter leading-none">FIRE DETECTED IN KITCHEN</h2>
                    <div className="flex items-center gap-3 text-red-100 font-bold text-lg bg-black/20 px-4 py-2 rounded-lg w-fit">
                      <AlertTriangle className="w-6 h-6" />
                      ACTION: Dispatch fire protocol. Evacuate Floor 2 immediately.
                    </div>
                  </div>
                </div>

                <div className="relative z-10 flex flex-col gap-3">
                  <div className="text-right mb-2">
                    <p className="text-white/60 text-[10px] font-mono uppercase">Automated Dispatch in</p>
                    <p className="text-white text-2xl font-black font-mono">00:04:12</p>
                  </div>
                  <button className="px-8 py-4 bg-white text-red-600 font-black rounded-xl hover:scale-105 transition-transform uppercase text-sm shadow-xl">
                    OVERRIDE & ACKNOWLEDGE
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Camera Grid */}
          <div className="xl:col-span-3 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <CameraFeed id="CAM 01" name="Main Lobby" isAlerting={false} isScanning={cycle % 4 === 1 && state === 'NORMAL'} />
              <CameraFeed id="CAM 02" name="Kitchen" isAlerting={state === 'CRITICAL'} isScanning={cycle % 4 === 2 && state === 'NORMAL'} />
              <CameraFeed id="CAM 03" name="Rear Entrance" isAlerting={false} isScanning={cycle % 4 === 3 && state === 'NORMAL'} />
              <CameraFeed id="CAM 04" name="Pool Deck" isAlerting={false} isScanning={cycle % 4 === 0 && cycle > 0 && state === 'NORMAL'} />
            </div>
          </div>

          {/* Alert Panel / Logs */}
          <div className="space-y-6">
            <div className="bg-slate-900/30 border border-slate-800/50 rounded-2xl flex flex-col h-[600px] backdrop-blur-sm">
              <div className="p-5 border-b border-slate-800/50 flex justify-between items-center bg-slate-900/20">
                <div className="flex items-center gap-3">
                  <Terminal className="w-4 h-4 text-slate-500" />
                  <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">Autonomous AI Logs</h3>
                </div>
                <div className="flex items-center gap-1.5">
                  <Radio className="w-3 h-3 text-emerald-500 animate-pulse" />
                  <span className="text-[9px] font-mono text-emerald-500 uppercase">Live_Stream</span>
                </div>
              </div>
              
              <div className="flex-1 p-6 font-mono text-[11px] space-y-3 overflow-y-auto scrollbar-hide">
                {logs.map((log, i) => (
                  <motion.div 
                    initial={{ x: -10, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    key={i} 
                    className={`flex gap-4 p-2 rounded ${
                      log.includes('CRITICAL') || log.includes('ALERT') ? 'bg-red-500/10 text-red-400 border-l-2 border-red-500' : 
                      log.includes('SCAN') ? 'text-emerald-400/80' : 'text-slate-500'
                    }`}
                  >
                    <span className="opacity-20 select-none">{String(i + 1).padStart(3, '0')}</span>
                    <span className="flex-1">{log}</span>
                  </motion.div>
                ))}
                <div ref={logEndRef} />
              </div>

              <div className="p-4 border-t border-slate-800/50 bg-slate-900/20">
                <div className="flex justify-between items-center text-[9px] font-mono text-slate-600">
                  <span>BUFFER: 100%</span>
                  <span>AI_CONFIDENCE: {state === 'NORMAL' ? '99.8%' : '100%'}</span>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-900/30 border border-slate-800/50 p-4 rounded-xl">
                <p className="text-[9px] font-black text-slate-600 uppercase mb-1">Active Objects</p>
                <p className="text-2xl font-black text-white font-mono">14</p>
              </div>
              <div className="bg-slate-900/30 border border-slate-800/50 p-4 rounded-xl">
                <p className="text-[9px] font-black text-slate-600 uppercase mb-1">Threat Prob.</p>
                <p className={`text-2xl font-black font-mono ${state === 'NORMAL' ? 'text-emerald-500' : 'text-red-500'}`}>
                  {state === 'NORMAL' ? '0.02%' : '100%'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 h-10 bg-[#020408] border-t border-slate-800/50 flex items-center justify-between px-8 text-[9px] font-mono text-slate-600 z-50">
        <div className="flex gap-8">
          <span className="flex items-center gap-2"><Radio className="w-3 h-3" /> NETWORK_STATUS: ENCRYPTED</span>
          <span className="flex items-center gap-2"><Crosshair className="w-3 h-3" /> TARGETING: AUTO_MODE</span>
        </div>
        <div className="flex gap-8 items-center">
          <div className="flex items-center gap-2">
            <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <motion.div 
                animate={{ width: ['20%', '80%', '40%'] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="h-full bg-emerald-500"
              />
            </div>
            <span>AI_LOAD</span>
          </div>
          <span className="text-slate-400">SESSION_TOKEN: {Math.random().toString(36).substring(7).toUpperCase()}</span>
        </div>
      </footer>
    </div>
  );
}
