import React,{useState} from "react";
import "./ProblemDescriptionFile.css";
import NavAfterLogin from "./NavAfterLogin";
import axios from "axios";
const ProblemDescriptionForm=() => {
    const [currentStep,setCurrentStep] = useState(0);
    const [formData,setFormData] = useState({
       smile_last_time:"",
       smile_reason: "", 
    });
    const formFields = [
        {id:"smile_last_time", label:"When did you smile last time(press enter after you type this)",type:"text",required:"true"},
        {id:"smile_reason", label:"Why Did you lose your smile",type:"text",required:"true"}
    ]

    const handleChange=(e) => {
        const { id,value } =e.target;
        setFormData((prevData) => ({ ...prevData,[id]:value}));
    };
    const handleKeyDown = (e) => {
        if(e.key==="Enter"){
            e.preventDefault();
        
        const currentField=formFields[currentStep];
        if(currentField.required && !formData[currentField.id]){
            alert(`${currentField.label} is required`);
            return;
        }

        setTimeout(() => {
            if(currentStep < formFields.length-1){
                setCurrentStep((prevStep) => prevStep + 1);
                console.log(currentStep);
            }
        },10);
    }
    
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Form Submitted: ",formData);
        try{
            const response= await axios.post("http://localhost:8000/auth/problem-page",formData,{headers:{'Content-Type' : 'application/json'}});
            const message=response.data.message;
            console.log(message);
        } catch(err){
            console.error("Error posting problem: ",err);
        }
    };
    return(
        <div className="formContainer">
            <NavAfterLogin />
            <form onSubmit={handleSubmit}>
                {formFields.map((field,index) => (
                    <div key={field.id} style={{ display:index <= currentStep ? "block" : "none"}}>
                        <label htmlFor={field.id}>{field.label}</label>
                        <input id={field.id} type={field.type} value={formData[field.id]} onChange={handleChange} onKeyDown={handleKeyDown} autoFocus={index === currentStep} />
                    </div>

                ))}
                {currentStep === formFields.length-1 && (
                    <button type="submit">Submit</button>
                )}
            </form>
        </div>
    );

};

export default ProblemDescriptionForm;

