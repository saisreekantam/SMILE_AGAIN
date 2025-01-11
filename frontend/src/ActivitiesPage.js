import React from "react";
import { Calendar, Activity, Heart, ArrowUp, Clock, Target } from "lucide-react";
import { AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, Area, ResponsiveContainer } from "recharts";
import "./ActivitiesPage.css";
import MeditationTimer from "./MeditationTimer";
import { useNavigate } from "react-router-dom";
import NavAfterLogin from "./NavAfterLogin";

const EnhancedActivityDashboard = () => {
  const navigate=useNavigate();
  const mockActivities = [
    {
      id: 1,
      title: "Mindful Breathing",
      description: "A simple breathing exercise to help you relax and focus",
      duration_minutes: 10,
      category: "Meditation",
      difficulty_level: "Easy",
    },
    {
      id: 2,
      title: "Gratitude Journal",
      description: "Write down three things you're grateful for today",
      duration_minutes: 15,
      category: "Reflection",
      difficulty_level: "Medium",
    },
    {
      id: 3,
      title: "Nature Walk",
      description: "Take a peaceful walk in nature",
      duration_minutes: 30,
      category: "Exercise",
      difficulty_level: "Easy",
    },
  ];

  const mockMoodData = [
    // { name: "Mon", mood: 6 },
    // { name: "Tue", mood: 7 },
    // { name: "Wed", mood: 6.5 },
    // { name: "Thu", mood: 8 },
    // { name: "Fri", mood: 7.5 },
    // { name: "Sat", mood: 8.5 },
    { name: "Sun", mood: 9 },
  ];

  return (
    <div className="centered-container">
      <NavAfterLogin />
      <div className="centered-content">
        {/* Header */}
        <div className="text-center border-container">
          <h1 className="text-4xl font-bold mb-4 text-white uppercase">Your Wellness Journey</h1>
          <p className="text-gray-400 mt-2">
            Track your progress and discover activities tailored just for you
          </p>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="card">
            <Calendar className="w-6 h-6 text-white mb-3" />
            <h3 className="card-title">Current Streak</h3>
            <p className="text-3xl font-bold text-green-500">1 day</p>
          </div>

          <div className="card">
            <Activity className="w-6 h-6 text-white mb-3" />
            <h3 className="card-title">Total Activities</h3>
            <p className="text-3xl font-bold text-green-500">2</p>
          </div>

          <div className="card">
            <Heart className="w-6 h-6 text-white mb-3" />
            <h3 className="card-title">Mood Improvement</h3>
            <p className="text-3xl font-bold text-green-500">+15%</p>
          </div>
        </div>

        {/* Mood Progress Chart */}
        <div className="border-container chart-container">
          <h3 className="text-xl font-bold mb-4 text-white">Mood Progress</h3>
          <ResponsiveContainer width="100%" height="95%">
            <AreaChart data={mockMoodData}>
              <defs>
                <linearGradient id="colorMood" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip />
              <Area type="monotone" dataKey="mood" stroke="#4f46e5" fill="url(#colorMood)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Activities Section */}
        <div className="border-container">
          <h2 className="text-2xl font-bold mb-6 text-white">Recommended for You</h2>
          <div className="activity-grid">
            {mockActivities.map((activity) => (
              <div key={activity.id} className="card">
                <h3 className="card-title">{activity.title}</h3>
                <p className="card-description">{activity.description}</p>
                <button className="card-button" onClick={() => navigate('/meditation_timer')}>Start</button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedActivityDashboard;
