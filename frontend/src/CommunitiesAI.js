import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Users, Timer, Activity, Send, History, Award } from 'lucide-react';
import axios from 'axios';
import './CommunitiesAI.css'

const CommunityActivities = () => {
  const [activities, setActivities] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [activityHistory, setActivityHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const chatContainerRef = useRef(null);
  
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [activities]);

  const handleSendMessage = async () => {
    if (!userMessage.trim() || loading) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/activities/suggest', {
        message: userMessage
      }, {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true
      });
      console.log(response.data);
      setActivities(prevActivities => [...prevActivities, {
        type: 'user',
        content: userMessage
      }, {
        type: 'bot',
        content: response.data.message.content,
        activities: response.data.metadata.suggested_activities
      }]);

      setUserMessage('');
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchActivityHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/activities/history', {
        withCredentials: true
      });
      console.log(response.data)
      setActivityHistory(response.data.activities);
      setShowHistory(true);
    } catch (error) {
      console.error('Error fetching activity history:', error);
    }
  };

  const participateInActivity = async (activityId) => {
    try {
      await axios.post('http://localhost:8000/activities/participate', {
        activity_id: activityId
      }, {
        withCredentials: true
      });
      
      // Show success message
      setActivities(prevActivities => [...prevActivities, {
        type: 'bot',
        content: "🎉 Fantastic! You've joined this activity. Get ready for some fun!",
        isNotification: true
      }]);
    } catch (error) {
      console.log(activityId);
      console.error('Error participating in activity:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 p-4 md:p-8">
      {/* Header */}
      <div className="max-w-4xl mx-auto bg-white rounded-t-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Sparkles className="text-yellow-500 w-8 h-8" />
            <h1 className="text-2xl font-bold text-gray-800">Community Activities</h1>
          </div>
          <button
            onClick={fetchActivityHistory}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-100 text-purple-600 rounded-lg hover:bg-purple-200 transition-colors"
          >
            <History className="w-5 h-5" />
            <span>Activity History</span>
          </button>
        </div>

        {/* Activity Feed */}
        <div 
          ref={chatContainerRef}
          className="h-96 overflow-y-auto mb-6 space-y-4 p-4 bg-gray-50 rounded-lg"
        >
          {activities.map((activity, index) => (
            <div
              key={index}
              className={`${
                activity.type === 'user' 
                  ? 'ml-auto bg-purple-500 text-white' 
                  : 'mr-auto bg-white border border-gray-200'
              } ${
                activity.isNotification 
                  ? 'bg-green-100 border-green-200 text-green-700' 
                  : ''
              } rounded-lg p-4 max-w-[80%] shadow-sm`}
            >
              {activity.type === 'bot' && activity.activities ? (
                <div className="space-y-4">
                  <p className="text-gray-800 mb-4">{activity.content}</p>
                  {activity.activities.map((act, idx) => (
                    <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-lg text-purple-600">{act.title}</h3>
                        <button
                          onClick={() => participateInActivity(act.id)}
                          className="px-4 py-1 bg-green-500 text-white rounded-full text-sm hover:bg-green-600 transition-colors"
                        >
                          Join Activity
                        </button>
                      </div>
                      <p className="text-gray-600 mb-3">{act.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Timer className="w-4 h-4 mr-1" />
                          {act.duration}
                        </div>
                        <div className="flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          {act.participants}
                        </div>
                        <div className="flex items-center">
                          <Activity className="w-4 h-4 mr-1" />
                          Energy: {act.energy_level}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>{activity.content}</p>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex items-center space-x-2 text-gray-500">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-500 border-t-transparent"></div>
              <span>Finding fun activities...</span>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="flex space-x-4">
          <input
            type="text"
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="What kind of activity would you like to do?"
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !userMessage.trim()}
            className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send className="w-5 h-5" />
            <span>Send</span>
          </button>
        </div>
      </div>

      {/* Activity History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Award className="text-purple-500 w-6 h-6" />
                  <h2 className="text-xl font-semibold text-gray-800">Your Activity History</h2>
                </div>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {activityHistory.length > 0 ? (
                <div className="space-y-4">
                  {activityHistory.map((item, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-purple-600">
                          {item.type === 'activity_request' ? 'Your Request' : 'Activity Suggestion'}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(item.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-gray-700">{item.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <p>No activity history yet. Start participating in activities!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommunityActivities;