import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { io } from 'socket.io-client';
import axios from 'axios';
import { Trophy, Users, Clock, Award, ArrowRight, Send } from 'lucide-react';
import './GroupGames.css'

const GroupGamesPage = () => {
  const [gameTemplates, setGameTemplates] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [socket, setSocket] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [answer, setAnswer] = useState('');
  const { groupId } = useParams();

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io('http://localhost:8000', {
      withCredentials: true
    });

    newSocket.on('connect', () => {
      console.log('Connected to game server');
    });

    newSocket.on('game_state', (state) => {
      setGameState(state);
      setParticipants(state.participants);
    });

    newSocket.on('player_joined', (data) => {
      setParticipants(prev => [...prev, { user_name: data.user_name, score: 0 }]);
    });

    newSocket.on('player_left', (data) => {
      setParticipants(prev => prev.filter(p => p.user_name !== data.user_name));
    });

    newSocket.on('game_message', (data) => {
      setMessages(prev => [...prev, data]);
    });

    newSocket.on('question_results', (data) => {
      setGameState(prev => ({
        ...prev,
        results: data.results,
        currentQuestion: data.next_question
      }));
    });

    setSocket(newSocket);

    // Fetch available game templates
    const fetchTemplates = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/games/templates`);
        console.log(response.data)
        setGameTemplates(response.data);
      } catch (error) {
        console.error('Error fetching game templates:', error);
      }
    };

    fetchTemplates();

    return () => {
      if (activeSession) {
        newSocket.emit('leave_game', { session_code: activeSession.code });
      }
      newSocket.disconnect();
    };
  }, []);

  const createGame = async (templateName) => {
    try {
      const response = await axios.post(`http://localhost:8000/games/create/${groupId}`, {
        template: templateName
      },{headers : {"Content-Type" : "application/json"},withCredentials:true});
      console.log(response.data)
      console.log("template ",templateName)
      
      const sessionCode = response.data.session_code;
      setActiveSession({ code: sessionCode, status: 'waiting' });
      socket.emit('join_game', { session_code: sessionCode });
    } catch (error) {
      console.log("template ",templateName)
      console.error('Error creating game:', error);
    }
  };

  const joinGame = async (sessionCode) => {
    try {
      await axios.post(`http://localhost:8000/games/join/${sessionCode}`);
      setActiveSession({ code: sessionCode, status: 'joined' });
      socket.emit('join_game', { session_code: sessionCode });
    } catch (error) {
      console.error('Error joining game:', error);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim()) return;
    
    try {
      await axios.post(`http://localhost:8000/games/answer/${activeSession.code}`, {
        answer: answer,
        time: gameState.currentQuestion.timeLeft
      });
      setAnswer('');
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const sendMessage = () => {
    if (!message.trim()) return;
    
    socket.emit('game_message', {
      session_code: activeSession.code,
      message: message
    });
    setMessage('');
  };

  const requestHint = () => {
    socket.emit('request_hint', {
      session_code: activeSession.code
    });
  };

  if (!activeSession) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Educational Games</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gameTemplates.map((template) => (
            <div key={template.name} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-2">{template.name}</h3>
              <p className="text-gray-600 mb-4">{template.description}</p>
              <div className="flex items-center text-sm text-gray-500 mb-4">
                <Users className="w-4 h-4 mr-1" />
                <span>{template.min_players}-{template.max_players} players</span>
              </div>
              <button
                onClick={() => createGame(template.id)}
                className="w-full bg-purple-600 text-white rounded-md py-2 hover:bg-purple-700 transition-colors"
              >
                Start Game
              </button>
            </div>
          ))}
        </div>

        <div className="mt-8 p-6 bg-white rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Join Existing Game</h2>
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter session code"
              className="flex-1 border rounded-md px-4 py-2"
              onChange={(e) => setMessage(e.target.value)}
            />
            <button
              onClick={() => joinGame(message)}
              className="bg-green-600 text-white rounded-md px-6 py-2 hover:bg-green-700 transition-colors"
            >
              Join
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-12 gap-6 p-6 max-w-7xl mx-auto">
      {/* Game Area */}
      <div className="col-span-8 bg-white rounded-lg shadow-lg p-6">
        {gameState?.currentQuestion ? (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">{gameState.currentQuestion.text}</h2>
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            
            <div className="flex gap-4">
              <input
                type="text"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Your answer..."
                className="flex-1 border rounded-md px-4 py-2"
              />
              <button
                onClick={submitAnswer}
                className="bg-purple-600 text-white rounded-md px-6 py-2 hover:bg-purple-700 transition-colors"
              >
                Submit
              </button>
              <button
                onClick={requestHint}
                className="bg-blue-600 text-white rounded-md px-6 py-2 hover:bg-blue-700 transition-colors"
              >
                Hint
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-4">Waiting for game to start...</h2>
            <p className="text-gray-600">Share the session code: {activeSession.code}</p>
          </div>
        )}

        {gameState?.results && (
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Last Question Results</h3>
            <div className="space-y-2">
              {gameState.results.map((result, index) => (
                <div key={index} className="flex justify-between items-center bg-gray-50 p-3 rounded">
                  <span>{result.user_name}</span>
                  <div className="flex items-center">
                    <span className="text-purple-600 font-semibold">{result.points_earned} pts</span>
                    {result.is_correct && <Award className="w-4 h-4 text-yellow-500 ml-2" />}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div className="col-span-4 space-y-6">
        {/* Scoreboard */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <Trophy className="w-6 h-6 text-yellow-500 mr-2" />
            <h2 className="text-xl font-semibold">Scoreboard</h2>
          </div>
          <div className="space-y-2">
            {participants.map((participant, index) => (
              <div key={index} className="flex justify-between items-center">
                <span>{participant.user_name}</span>
                <span className="font-semibold">{participant.score}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Game Chat</h2>
          <div className="h-48 overflow-y-auto mb-4 space-y-2">
            {messages.map((msg, index) => (
              <div key={index} className="text-sm">
                <span className="font-semibold">{msg.user_name}: </span>
                {msg.message}
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 border rounded-md px-3 py-2"
            />
            <button
              onClick={sendMessage}
              className="bg-gray-600 text-white rounded-md p-2 hover:bg-gray-700 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GroupGamesPage;