import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import NavAfterLogin from './NavAfterLogin';
import './MoodTrackerPage.css';

const MoodTrackerPage = () => {
  const [moodData, setMoodData] = useState({
    mood_level: 3,
    emotions: [],
    notes: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const emotionOptions = [
    { label: 'Happy', value: 'happy' },
    { label: 'Excited', value: 'excited' },
    { label: 'Calm', value: 'calm' },
    { label: 'Content', value: 'content' },
    { label: 'Anxious', value: 'anxious' },
    { label: 'Stressed', value: 'stressed' },
    { label: 'Sad', value: 'sad' },
    { label: 'Tired', value: 'tired' },
    { label: 'Energetic', value: 'energetic' },
    { label: 'Motivated', value: 'motivated' },
    { label: 'Frustrated', value: 'frustrated' },
    { label: 'Peaceful', value: 'peaceful' }
  ];

  const moodLabels = {
    1: 'Very Low',
    2: 'Low',
    3: 'Neutral',
    4: 'Good',
    5: 'Excellent'
  };

  const handleMoodChange = (level) => {
    setMoodData(prev => ({ ...prev, mood_level: level }));
  };

  const handleEmotionToggle = (emotion) => {
    setMoodData(prev => ({
      ...prev,
      emotions: prev.emotions.includes(emotion)
        ? prev.emotions.filter(e => e !== emotion)
        : [...prev.emotions, emotion]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const response = await axios.post(
        'http://localhost:8000/mood/mood/entry',
        moodData,
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        }
      );
      console.log(response.data.message);
      if (response.data.message==="Mood entry created successfully") {
        navigate('/home'); // Redirect to chatbot after submission
      }
    } catch (err) {
      setError('Failed to save mood entry. Please try again.');
      console.error('Error saving mood entry:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mood-tracker-page">
      <NavAfterLogin />
      
      <div className="mood-journal-container">
        <div className="mood-header">
          <h1>Mood Journal</h1>
          <p style={{color:'black'}}>How are you feeling today?</p>
        </div>

        <form onSubmit={handleSubmit} className="mood-form">
          {/* Mood Level Selection */}
          <div className="mood-level-section">
            {Object.entries(moodLabels).map(([level, label]) => (
              <button
                key={level}
                type="button"
                className={`mood-button ${moodData.mood_level === parseInt(level) ? 'selected' : ''}`}
                onClick={() => handleMoodChange(parseInt(level))}
                style={{color:'black'}}
              >
                <span className="mood-number" style={{color:'black'}}>{level}</span>
                <span className="mood-label" style={{color:'black'}}>{label}</span>
              </button>
            ))}
          </div>

          {/* Emotions Selection */}
          <div className="emotions-section">
            <h3>Select emotions you're experiencing:</h3>
            <div className="emotions-grid">
              {emotionOptions.map(({ label, value }) => (
                <button
                  key={value}
                  type="button"
                  className={`emotion-tag ${moodData.emotions.includes(value) ? 'selected' : ''}`}
                  onClick={() => handleEmotionToggle(value)}
                  style={{color:'black'}}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Notes Section */}
          <div className="notes-section">
            <h3>Add notes about your day:</h3>
            <textarea
              value={moodData.notes}
              onChange={(e) => setMoodData(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="How was your day? What's on your mind?"
              rows="4"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : 'Save Entry'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MoodTrackerPage;