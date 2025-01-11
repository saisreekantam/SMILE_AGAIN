import './LandingPage.css'
import React,{ useEffect,useState } from 'react'
import image1 from './assets/Image1.jpg'
import image2 from './assets/Image2.jpg'
import image3 from './assets/Image3.jpg'
import image4 from './assets/Image4.jpg'
import image5 from './assets/Image5.jpg'
import chatbot from './assets/Chatbot.jpg'
import { useAuth } from './contexts/AuthContext'

function LandingPage() {
  const { isLoggedIn } = useAuth();
  const [showText, setShowText] = useState(false);
  const [showImages, setShowImages] = useState(false);

  useEffect(() => {
    // Show the text first
    setShowText(true);

    // Delay for showing images
    const imageDelay = setTimeout(() => {
      setShowImages(true);
    }, 1000); // 1-second delay

    return () => {
      clearTimeout(imageDelay); // Cleanup timeout
    };
  }, []);
  useEffect(() => {
    const scrollContainer = document.querySelector('.ImagesContainer');
  
    const handleMouseMove = (event) => {
      // Get the mouse position relative to the window
      const mouseX = event.clientX;
      const mouseY = event.clientY;
  
      // Calculate the maximum scrollable width and height
      const scrollWidth = scrollContainer.scrollWidth - scrollContainer.clientWidth;
      const scrollHeight = scrollContainer.scrollHeight - scrollContainer.clientHeight;
  
      // Calculate scroll positions based on mouse position
      const scrollLeftPosition = (mouseX / window.innerWidth) * scrollWidth;
      const scrollTopPosition = (mouseY / window.innerHeight) * scrollHeight;
  
      // Apply horizontal and vertical scroll positions
      scrollContainer.scrollLeft = scrollLeftPosition;
      scrollContainer.scrollTop = scrollTopPosition;
    };
  
    // Add event listener for mouse movement
    document.addEventListener('mousemove', handleMouseMove);
  
    // Clean up the event listener when the component unmounts
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);
  
  return (
    <div className="App">
      <nav className="TopNavBar">
        <div className="Logo">
          <span className="Smile">Smile</span>
          <span className="Again">Again</span>
        </div>
        <div className="Links">
          <a href="">Home</a>
          <a href="">Blogs</a>
          <a href="">Workshops</a>
          <a href="">Chats</a>
          <a href="">About us</a>
          <a href="/login">Sign In</a>
        </div>
      </nav>
      <div className="ImagesContainer">
        <div className="LeftImages">
          <div className='ImageContainer' style={{top:'70px', bottom:'100px', left:'50px'}}>
            <img src={image1} alt='Person Image' className='DisplayImages'></img>
            <div className='Description'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Eius alias qui quod enim? Sunt praesentium est molestias voluptatem, neque quam sit accusamus deserunt nobis architecto, sapiente itaque totam nihil repellat?</div>
          </div>
          <div className='ImageContainer' style={{bottom:'140px', left:'50px'}}>
            <img src={image2} alt='Person Image' className='DisplayImages'></img>
            <div className='Description'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Eius alias qui quod enim? Sunt praesentium est molestias voluptatem, neque quam sit accusamus deserunt nobis architecto, sapiente itaque totam nihil repellat?</div>
          </div>
          <div className='ImageContainer' style={{top:'380px'}}> 
            <img src={image5} alt='Person Image' className='DisplayImages'></img>
            <div className='Description'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Eius alias qui quod enim? Sunt praesentium est molestias voluptatem, neque quam sit accusamus deserunt nobis architecto, sapiente itaque totam nihil repellat?</div>
          </div>
        </div>
        <div className="center">
          <h2>To The Achievers</h2>
          <h2>Who want their</h2>
          <h2>Smile Back</h2>
        </div>
        <div className="RightImages" style={{width:'700px'}}>
          <div className='ImageContainer' style={{bottom:'140px'}}>
              <img src={image3} alt='Person Image' className='DisplayImages'></img>
              <div className='Description'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Eius alias qui quod enim? Sunt praesentium est molestias voluptatem, neque quam sit accusamus deserunt nobis architecto, sapiente itaque totam nihil repellat?</div>
          </div>
          <div className='ImageContainer' style={{top:'90px', left:'150px'}}>
            <img src={image4} alt='Person Image' className='DisplayImages'></img>
            <div className='Description'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Eius alias qui quod enim? Sunt praesentium est molestias voluptatem, neque quam sit accusamus deserunt nobis architecto, sapiente itaque totam nihil repellat?</div>
          </div>
          <div className='ImageContainer' style={{top:'380px', right:'500px'}}>
            <img src={image5} alt='Person Image' className='DisplayImages'></img>
            <div className='Description'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Eius alias qui quod enim? Sunt praesentium est molestias voluptatem, neque quam sit accusamus deserunt nobis architecto, sapiente itaque totam nihil repellat?</div>
          </div>
        </div>
        
      </div>
      <div className='ChatbotPageContainer'>
        <div className='empoweringText'>
          "Smiling isn't just an option; it's a true expression of happiness.Learn from those who lost their smiles and bravely brought them back."
        </div>
        <div className='ChatbotImageContainer'>
          <a href="/chatbot_page"><img src={chatbot} className='ChatbotImage'></img></a>
        </div>
      </div>
      <div className='WorkshopPage'>
        <div className='WorkShopJoin'>
          <p style={{font:'20px', color:'white'}}>EMPOWER YOURSELF AND BUILD</p>
          <p style={{font:'16px', color:'white'}}>Don't let someone to decide yout future</p>
          <a href="" style={{font:'16px', color:'white'}}>Join----</a>
        </div>
      </div>
      <div className='ColorDonation'>
        <div className='ColorDonationMessage' style={{top:'50px'}}>
          <h3>Life is just dark without happiness</h3>
          <p>We started this platform to find your smile back and for every smile found,we are making a life colorful.Everybody looses their smile in the bad phase but those who get them back are real winners.</p>
          <h3><a href="" style={{color:'white'}}>IF WE MADE YOUR LIFE COLORFUL----</a></h3>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;