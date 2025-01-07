import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./FeedbacksPage.css";

const FeedbacksPage = () => {
  const { workshopId } = useParams();
  const [feedbacks, setFeedbacks] = useState([]);
  const [workshopTitle, setWorkshopTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFeedbacks = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/workshops/feedback/${workshopId}`, {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        });
        setWorkshopTitle(response.data.workshop_title);
        setFeedbacks(response.data.feedback);
      } catch (err) {
        setError("Failed to load feedback. Please try again later.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchFeedbacks();
  }, [workshopId]);

  if (loading) {
    return <div className="loading">Loading feedback...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="feedbacks-container">
      <h1 className="header">{workshopTitle}</h1>
      <div className="feedback-list">
        {feedbacks.length === 0 ? (
          <p className="no-feedback-message">No feedback available for this workshop.</p>
        ) : (
          feedbacks.map((feedback, index) => (
            <div key={index} className="feedback-card">
              <p className="feedback-user">
                <strong>User:</strong> {feedback.user}
              </p>
              <p className="feedback-comments">
                <strong>Comments:</strong> {feedback.comments}
              </p>
              <p className="feedback-rating">
                <strong>Rating:</strong> {feedback.rating}/5
              </p>
              <p className="feedback-timestamp">
                <strong>Timestamp:</strong> {new Date(feedback.timestamp).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
      <button onClick={() => navigate(`/workshops/${workshopId}/add-feedback`)} className="add-feedback-btn">
        Add Feedback
      </button>
    </div>
  );
};

export default FeedbacksPage;
