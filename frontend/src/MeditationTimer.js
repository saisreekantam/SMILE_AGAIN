import React, { useState, useEffect, useCallback } from 'react';
import { Moon, Sun, Volume2, Volume1, VolumeX, Play, Pause, RefreshCw } from 'lucide-react';
import './MeditationTimer.css'
import NavAfterLogin from './NavAfterLogin';
import { useParams } from 'react-router-dom';

const MeditationTimer = () => {
  const [duration, setDuration] = useState(300); // 5 minutes in seconds
  const [timeLeft, setTimeLeft] = useState(duration);
  const [isRunning, setIsRunning] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [selectedPreset, setSelectedPreset] = useState('5min');
  const [showCompleted, setShowCompleted] = useState(false);

  const presets = [
    { id: '1min', label: '1 min', seconds: 60 },
    { id: '2min', label: '2 min', seconds: 120 },
    { id: '5min', label: '5 min', seconds: 300 },
    { id: '10min', label: '10 min', seconds: 600 },
    { id: '15min', label: '15 min', seconds: 900 },
    { id: '20min', label: '20 min', seconds: 1200 },
    { id: '30min', label: '30min' , seconds: 1800},
    { id: '45min', label: '45min' , seconds: 2700},
    { id: '1hr', label: '1hr' , seconds: 3600},
  ];

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setIsRunning(false);
    setTimeLeft(duration);
    setShowCompleted(false);
  };

  const selectPreset = (preset) => {
    setDuration(preset.seconds);
    setTimeLeft(preset.seconds);
    setSelectedPreset(preset.id);
    setIsRunning(false);
    setShowCompleted(false);
  };

  useEffect(() => {
    let interval;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((time) => {
          if (time <= 1) {
            setIsRunning(false);
            setShowCompleted(true);
            if (soundEnabled) {
              // Play completion sound
              const audio = new Audio('/meditation-complete.mp3');
              audio.play();
            }
            return 0;
          }
          return time - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft, soundEnabled]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-indigo-950 to-purple-900 text-white p-4">
        <NavAfterLogin />
      <div className="w-full max-w-md bg-indigo-900/30 backdrop-blur-lg rounded-3xl p-8 shadow-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold mb-2">Timer</h1>
          <p className="text-indigo-200">Find your inner peace</p>
        </div>

        {/* Preset Buttons */}
        <div className="grid grid-cols-4 gap-2 mb-8" style={{marginTop:'20px',display:'flex',justifyContent:'space-evenly'}}>
          {presets.map((preset) => (
            <button
              key={preset.id}
              onClick={() => selectPreset(preset)}
              className={`py-2 px-4 rounded-lg transition-all ${
                selectedPreset === preset.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-indigo-800/40 text-indigo-200 hover:bg-indigo-700'
              }`}
              style={{height:'60px'}}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* Timer Display */}
        <div className="text-center mb-8">
          <div className="text-6xl font-bold mb-4 font-mono" style={{textAlign:'center',fontSize:'25px'}}>
            {formatTime(timeLeft)}
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-center items-center gap-4 mb-8" style={{gap:'20px',display:'flex',left:'100px'}}>
          <button
            onClick={toggleTimer}
            className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-full p-4 transition-all"
            style={{marginLeft:'520px'}}
          >
            {isRunning ? <Pause size={24} /> : <Play size={24} />}
          </button>
          <button
            onClick={resetTimer}
            className="bg-indigo-800/40 hover:bg-indigo-700 text-white rounded-full p-4 transition-all"
            style={{height:'53px'}}
          >
            <RefreshCw size={24} />
          </button>
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="bg-indigo-800/40 hover:bg-indigo-700 text-white rounded-full p-4 transition-all"
            style={{height:'53px'}}
          >
            {soundEnabled ? <Volume2 size={24} /> : <VolumeX size={24} />}
          </button>
        </div>

        {/* Completion Message */}
        {showCompleted && (
          <div className="text-center bg-indigo-800/40 rounded-lg p-4 mb-4">
            <h2 className="text-xl font-semibold mb-2">Session Complete!</h2>
            <p className="text-indigo-200">
              Well done! Take a moment to reflect on your practice.
            </p>
          </div>
        )}

        {/* Progress Bar */}
        <div className="w-full bg-indigo-800/40 rounded-full h-2 mb-4">
          <div
            className="bg-indigo-500 h-2 rounded-full transition-all duration-1000"
            style={{ width: `${(timeLeft / duration) * 100}%` }}
          />
        </div>

        {/* Breathing Guide */}
        <div className="text-center text-indigo-200 text-sm">
          {isRunning ? "Breathe in... Breathe out..." : "Press play to begin"}
        </div>
      </div>
    </div>
  );
};

export default MeditationTimer;