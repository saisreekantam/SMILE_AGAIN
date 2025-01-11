import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Star, Award, Clock } from 'lucide-react';
import { useParams } from 'react-router-dom';

const SmileJourneyPage = () => {
  const [journeyData, setJourneyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { community_id } = useParams();

  useEffect(() => {
    fetchJourneyData();
  }, []);

  const fetchJourneyData = async () => {
    try {
      // Assuming your user is in the "Grade Stress" community with ID 1
      console.log("id:",community_id);
      const response = await axios.get(`http://localhost:8000/journey/paths/${community_id}`, {
        withCredentials: true
      });
      
      console.log('Journey Data:', response.data); // Debug log
      setJourneyData(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching journey data:', err);
      setError(err.message || 'Failed to load journey data');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-purple-600 to-blue-500">
        <div className="text-white text-xl">Loading your journey...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 p-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error!</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 p-8">
      {/* Header Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4">
          YOUR SMILE JOURNEY
        </h1>
        <p className="text-xl text-purple-100">
          Track your progress and earn rewards
        </p>
      </div>

      {/* Journey Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {/* Progress Card */}
        <div className="bg-white rounded-lg shadow-xl p-6 transform hover:scale-105 transition-transform duration-200">
          <div className="flex items-center mb-4">
            <Star className="w-6 h-6 text-yellow-500 mr-2" />
            <h2 className="text-xl font-semibold text-gray-800">Overall Progress</h2>
          </div>
          {journeyData && journeyData[0] && (
            <div className="space-y-4">
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-purple-600 bg-purple-200">
                      {Math.round((journeyData[0].user_progress.completed_milestones / journeyData[0].total_milestones) * 100)}% Complete
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-purple-200">
                  <div 
                    style={{ width: `${(journeyData[0].user_progress.completed_milestones / journeyData[0].total_milestones) * 100}%` }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-purple-500"
                  />
                </div>
              </div>
              <div className="text-gray-600">
                {journeyData[0].user_progress.completed_milestones} of {journeyData[0].total_milestones} milestones completed
              </div>
            </div>
          )}
        </div>

        {/* Rewards Card */}
        <div className="bg-white rounded-lg shadow-xl p-6 transform hover:scale-105 transition-transform duration-200">
          <div className="flex items-center mb-4">
            <Award className="w-6 h-6 text-purple-500 mr-2" />
            <h2 className="text-xl font-semibold text-gray-800">Rewards Earned</h2>
          </div>
          {journeyData && journeyData[0] && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Coins</span>
                <span className="text-xl font-bold text-yellow-500">
                  {journeyData[0].user_progress.total_coins_earned} 🪙
                </span>
              </div>
              <div className="border-t pt-4">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Next Rewards:</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex justify-between">
                    <span>Complete Next Milestone</span>
                    <span>+{journeyData[0].coins_per_milestone} coins</span>
                  </li>
                  <li className="flex justify-between">
                    <span>7-day Streak</span>
                    <span>+100 coins</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Current Challenge Card */}
        <div className="bg-white rounded-lg shadow-xl p-6 transform hover:scale-105 transition-transform duration-200">
          <div className="flex items-center mb-4">
            <Clock className="w-6 h-6 text-green-500 mr-2" />
            <h2 className="text-xl font-semibold text-gray-800">Current Challenge</h2>
          </div>
          {journeyData && journeyData[0] && (
            <div className="space-y-4">
              <p className="text-gray-600">{journeyData[0].description}</p>
              <button 
                className="w-full bg-purple-600 text-white rounded-md py-2 hover:bg-purple-700 transition-colors"
                onClick={() => console.log('Start next milestone')}
              >
                Start Next Milestone
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Journey Path Visualization */}
      {journeyData && journeyData[0] && (
        <div className="mt-12 bg-white rounded-lg shadow-xl p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Your Journey Path</h2>
          <div className="relative">
            <div className="absolute top-0 left-1/2 h-full w-0.5 bg-purple-200 transform -translate-x-1/2" />
            {Array.from({ length: journeyData[0].total_milestones }).map((_, index) => (
              <div 
                key={index} 
                className={`flex items-center mb-8 ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}
              >
                <div className="w-5/12" />
                <div className="w-2/12 flex justify-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                    index < journeyData[0].user_progress.completed_milestones
                      ? 'border-green-500 bg-green-100'
                      : 'border-gray-300 bg-white'
                  }`}>
                    {index + 1}
                  </div>
                </div>
                <div className="w-5/12">
                  <div className={`p-4 rounded-lg ${
                    index < journeyData[0].user_progress.completed_milestones
                      ? 'bg-green-100'
                      : 'bg-gray-100'
                  }`}>
                    <h3 className="font-medium">Milestone {index + 1}</h3>
                    <p className="text-sm text-gray-600">
                      {index < journeyData[0].user_progress.completed_milestones ? '✅ Completed' : '🎯 Not Started'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SmileJourneyPage;