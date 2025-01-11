import React, { useState, useEffect } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { Progress } from 'recharts';
import { Calendar, Medal, Star, Users, Book, Brain, Heart,Trophy } from 'lucide-react';
import './SmileJourney.css'

const JourneyDashboard = () => {
  const [journeyData, setJourneyData] = useState(null);
  const [currentPath, setCurrentPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    fetchJourneyData();
  }, []);

  const fetchJourneyData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/journey/paths/${ id }`, {
        credentials: 'include'
      });
      const data = await response.json();
      console.log(data);
      setJourneyData(data);
      if (data.length > 0) {
        setCurrentPath(data[0]);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to load journey data');
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-xl text-gray-600">Loading your journey...</div>
    </div>
  );

  if (error) return (
    <div className="p-4 text-red-600 bg-red-100 rounded-lg">
      {error}
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Your Smile Journey</h1>
        <p className="text-gray-600 mt-2">Track your progress and earn rewards</p>
      </header>

      {currentPath && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <JourneyProgress path={currentPath} />
          <CurrentMilestone path={currentPath} />
          <RewardsPanel path={currentPath} />
        </div>
      )}

      <MilestonePath path={currentPath} />
      {/* <LeaderboardPanel communityId={1} /> */}
    </div>
  );
};

const JourneyProgress = ({ path }) => {
  const percentage = (path.user_progress.completed_milestones / path.total_milestones) * 100;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <Star className="w-5 h-5 mr-2 text-yellow-500" />
        Overall Progress
      </h2>
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
              {Math.round(percentage)}% Complete
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
          <div 
            style={{ width: `${percentage}%` }}
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
          />
        </div>
        <div className="text-gray-600">
          {path.user_progress.completed_milestones} of {path.total_milestones} milestones completed
        </div>
      </div>
    </div>
  );
};

const CurrentMilestone = ({ path }) => {
  const [milestone, setMilestone] = useState(null);

  useEffect(() => {
    fetchCurrentMilestone();
  }, [path]);

  const fetchCurrentMilestone = async () => {
    try {
      const response = await fetch(`http://localhost:8000/journey/progress/${path.id}`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.current_milestone) {
        setMilestone(data.current_milestone);
      }
    } catch (err) {
      console.error('Failed to fetch current milestone:', err);
    }
  };

  if (!milestone) return null;

  const getIcon = (type) => {
    switch (type) {
      case 'activity': return <Brain className="w-6 h-6 text-purple-500" />;
      case 'reflection': return <Book className="w-6 h-6 text-green-500" />;
      case 'connection': return <Users className="w-6 h-6 text-blue-500" />;
      default: return <Star className="w-6 h-6 text-yellow-500" />;
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Current Milestone</h2>
      <div className="flex items-start space-x-4">
        <div className="mt-1">{getIcon(milestone.type)}</div>
        <div>
          <h3 className="font-medium text-gray-800">{milestone.title}</h3>
          <p className="text-gray-600 text-sm mt-1">{milestone.description}</p>
          {milestone.type === 'activity' && (
            <div className="mt-3">
              <span className="text-sm font-medium">Required: {milestone.required_activities} activities</span>
            </div>
          )}
          <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            Start Activity
          </button>
        </div>
      </div>
    </div>
  );
};

const RewardsPanel = ({ path }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <Medal className="w-5 h-5 mr-2 text-yellow-500" />
        Your Rewards
      </h2>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Total Coins Earned</span>
          <span className="font-semibold text-yellow-500">
            {path.user_progress.total_coins_earned} 🪙
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Current Streak</span>
          <span className="font-semibold text-green-500">
            {path.user_progress.current_streak} days 🔥
          </span>
        </div>
        <div className="mt-4 pt-4 border-t">
          <h3 className="font-medium text-gray-700 mb-2">Next Rewards:</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex justify-between">
              <span>Complete Milestone</span>
              <span>+50 coins</span>
            </li>
            <li className="flex justify-between">
              <span>7-day Streak</span>
              <span>+100 coins</span>
            </li>
            <li className="flex justify-between">
              <span>Path Completion</span>
              <span>+500 coins</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

const MilestonePath = ({ path }) => {
  if (!path) return null;

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-6">Journey Path</h2>
      <div className="relative">
        <div className="absolute top-0 left-1/2 h-full w-px bg-gray-200 -translate-x-1/2" />
        <div className="space-y-8 relative">
          {Array.from({ length: path.total_milestones }).map((_, index) => (
            <div key={index} className={`flex items-center ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}>
              <div className="w-1/2 px-8">
                <div className={`p-4 rounded-lg ${
                  index < path.user_progress.completed_milestones 
                    ? 'bg-green-100 border-green-200' 
                    : 'bg-gray-50 border-gray-200'
                  } border`}>
                  <h3 className="font-medium">Milestone {index + 1}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {index < path.user_progress.completed_milestones 
                      ? '✅ Completed' 
                      : '🔲 Not started'}
                  </p>
                </div>
              </div>
              <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 border-gray-300">
                <span className="text-sm font-medium">{index + 1}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// const LeaderboardPanel = ({ communityId }) => {
//   const [leaderboard, setLeaderboard] = useState([]);

//   useEffect(() => {
//     fetchLeaderboard();
//   }, [communityId]);

//   const fetchLeaderboard = async () => {
//     try {
//       const response = await fetch(
//         `http://localhost:8000/journey/leaderboard/${communityId}`,
//         { credentials: 'include' }
//       );
//       const data = await response.json();
//       setLeaderboard(data.leaderboard);
//     } catch (err) {
//       console.error('Failed to fetch leaderboard:', err);
//     }
//   };

//   return (
//     <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
//       <h2 className="text-xl font-semibold mb-4 flex items-center">
//         <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
//         Community Leaderboard
//       </h2>
//       <div className="overflow-x-auto">
//         <table className="min-w-full">
//           <thead>
//             <tr className="text-left text-gray-600">
//               <th className="py-2">Rank</th>
//               <th className="py-2">Name</th>
//               <th className="py-2">Milestones</th>
//               <th className="py-2">Coins</th>
//               <th className="py-2">Streak</th>
//             </tr>
//           </thead>
//           <tbody>
//             {leaderboard.map((entry, index) => (
//               <tr key={entry.user_id} className="border-t">
//                 <td className="py-2">
//                   {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
//                 </td>
//                 <td className="py-2">{entry.name}</td>
//                 <td className="py-2">{entry.completed_milestones}</td>
//                 <td className="py-2">{entry.total_coins} 🪙</td>
//                 <td className="py-2">{entry.current_streak} 🔥</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     </div>
//   );
// };

export default JourneyDashboard;