import React,{ useEffect } from 'react'
import LandingPage from './LandingPage';
import { Routes,Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import RegistrationPage from './RegistrationPage';
import ProblemDescriptionForm from './ProblemDescriptionForm';
import ChatBotPage from './ChatBotPage';
import ProfilePage from './ProfilePage';
import ViewFriends from './FriendsPage';

function App() {
  return (
    <>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route path='/friends' element={<ViewFriends />} />
        <Route path='/login' element={<LoginPage />} />
        <Route path='/register' element={<RegistrationPage />} />
        <Route path='/auth/problem_page' element={<ProblemDescriptionForm />} />
        <Route path='/chatbot_page' element={<ChatBotPage />} />
        <Route path='/myProfile' element={<ProfilePage />} />
      </Routes>
    </>
  );
}

export default App;

