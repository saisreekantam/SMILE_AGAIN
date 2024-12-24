import React, { useState } from "react";
import "./RegistrationPage.css";
import axios from 'axios';
import { useNavigate } from "react-router-dom";

function RegistrationPage() {
    const [name,setName]=useState("");
    const [email,setEmail]=useState("");
    const [gender,setGender]=useState("");
    const [password,setPassword]=useState("");

    const navigate=useNavigate();
    const handleSubmit=async (e) => {
        e.preventDefault();
        const data = {
            name:name,
            email:email,
            gender:gender,
            password:password
        };
        try{
           const response = await axios.post("http://localhost:8000/auth/register",data,{headers: { 'Content-Type' : 'application/json'}});
           console.log(response.data.message);
           if(response.status===200){
            const { name } = data;
            localStorage.setItem("username",name);
            navigate('/home');
           }
        } catch (err){
            console.error('Error Saving workout: ',err);
        }

    }
    return (
        <div className="registration-container">
            <h2>Registration Page</h2>
            <form onSubmit={handleSubmit}>
                <input type="text" name="name" placeholder="Full Name" required onChange={(e) => setName(e.target.value)}/>
                <input type="email" name="email" placeholder="Email" required  onChange={(e) => setEmail(e.target.value)}/>
                <select name="gender" required onChange={(e) => setGender(e.target.value)}>
                    <option value="" disabled selected>
                        Select Gender
                    </option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                </select>
                <input type="password" name="password" placeholder="Password" required />
                <input type="password" name="confirmPassword" placeholder="Confirm Password" required onChange={(e) => setPassword(e.target.value)}/>
                <button type="submit">Register</button>
            </form>
            <a href="/login">Already have an account? Login here</a>
            <a href="/">Go back to homepage</a>
        </div>
    );
}

export default RegistrationPage;
