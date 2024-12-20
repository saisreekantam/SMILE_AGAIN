import React,{useState} from "react";
import "./ProblemDescriptionFile.css";
const ProblemDescriptionForm=() => {
    const [currentStep,setCurrentStep] = useState(0);
    const [formData,setFormData] = useState({
       When:"",
       Why: "", 
    });
    const formFields = [
        {id:"When", label:"When did you smile last time",type:"text",required:"true"},
        {id:"Why", label:"Why Did you lose your smile",type:"text",required:"true"}
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
    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Form Submitted: ",formData);
    };
    return(
        <div className="formContainer">
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

