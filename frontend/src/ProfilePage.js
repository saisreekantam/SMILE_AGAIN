import React, { useEffect, useState } from 'react';
import './ProfilePage.css';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavAfterLogin from './NavAfterLogin';

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const navigate=useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
    try{
        const response=await axios.get("http://localhost:8000/users/profile",{ headers: {'Content-Type' : 'application/json'},withCredentials:true});
        console.log(response.data);
        setProfile(response.data);
    } catch(err){
        console.error("Error fetching profile details: ",err);
    }
    };
    fetchProfile();

  }, []);

  const handleLogout = async () => {
    try{
      const response=await axios.post("http://localhost:8000/auth/logout",[],{headers:{"Content-Type" : "application/json"},withCredentials:true});
      navigate('/')
    }
    catch(err){
      console.log("Error while logging in ",err)
    }
  };

  if (!profile) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="profile-page">
      <NavAfterLogin />
      <div className="profile-container">
        <img
          src={profile.profilePic}
          alt={`${profile.name}'s profile`}
          className="profile-pic"
        />
        <div className="profile-details">
          <h1 className="profile-name">{profile.name}</h1>
          <p className="profile-email">Email: {profile.email}</p>
          <p className="profile-gender">Gender: {profile.gender}</p>
          <p className="profile-description">About: {profile.description}</p>
        </div>
      </div>
      <div className="friends-link">
        <Link to="/friends">View Friends</Link>
      </div>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default ProfilePage;
