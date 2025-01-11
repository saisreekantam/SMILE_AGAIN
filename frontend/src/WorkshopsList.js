import React, { useEffect, useState } from "react";
import "./Workshops.css";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import NavAfterLogin from "./NavAfterLogin";

const WorkshopsList = () => {
  const [workshops, setWorkshops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showOptions, setShowOptions] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWorkshops = async () => {
      try {
        const response = await axios.get("http://localhost:8000/workshops/list", {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        });
        console.log(response.data);
        setWorkshops(response.data);
      } catch (err) {
        setError("Failed to load workshops. Please try again later.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkshops();
  }, []);

  if (loading) {
    return <div className="loading">Loading workshops...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="Containerr">
      <NavAfterLogin />
      <div className="container">
        <h1 className="header">Workshops</h1>
        <div className="workshops-list">
          {workshops.length === 0 ? (
            <p className="no-workshops-message">No Workshops Available</p>
          ) : (
            workshops.map((workshop) => (
              <div key={workshop.id} className={`workshop-card ${workshop.sponsored ? "sponsored" : ""}`}>
                {workshop.sponsored && <div className="sponsored-tag">Sponsored</div>}
                <h2 className="workshop-title">{workshop.title}</h2>
                <p className="workshop-description">{workshop.description}</p>
                {workshop.banner_url && (
                  <img src={workshop.banner_url} alt="Workshop Banner" className="workshop-banner" />
                )}
                <p className="workshop-details">
                  <strong>Created By:</strong> {workshop.created_by}
                </p>
                <p className="workshop-details">
                  <strong>Average Rating:</strong> {workshop.average_rating ? workshop.average_rating.toFixed(1) : "No Ratings"}
                </p>
                <p className="workshop-details">
                  <strong>Tag:</strong> {workshop.tag}
                </p>
                <p className="workshop-details">
                  <strong>{workshop.is_paid ? "Paid" : "Free"}</strong> {workshop.is_paid && `- $${workshop.price}`}
                </p>
                <div className="workshop-buttons">
                  <button
                    onClick={() => navigate(`/workshops/${workshop.id}/feedback`)}
                    className="view-feedback-btn"
                  >
                    View Feedback
                  </button>
                  {!workshop.is_paid && workshop.meet_link && (
                    <a
                      href={workshop.meet_link}
                      className="meet-link"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Join Workshop
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Floating Action Button */}
        <div
          className="fab-container"
          onMouseEnter={() => setShowOptions(true)}
          onMouseLeave={() => setShowOptions(false)}
        >
          <button className="fab-button">+</button>
          {showOptions && (
            <div className="fab-options">
              <button onClick={() => navigate("/workshops/create")}>Add Workshop</button>
              <button onClick={() => console.log("Delete Workshop clicked")}>Delete Workshop</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkshopsList;
