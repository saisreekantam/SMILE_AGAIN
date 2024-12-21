import React,{ useEffect } from 'react'
import LandingPage from './LandingPage';
import { Routes,Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import RegistrationPage from './RegistrationPage';
import ProblemDescription from './ProblemDescription';

function App() {
  return (
    <>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route path='/login' element={<LoginPage />} />
        <Route path='/register' element={<RegistrationPage />} />
        <Route path='/home' element={<ProblemDescription />} />
      </Routes>
    </>
  );
}

export default App;

