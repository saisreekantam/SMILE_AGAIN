import axios from "axios";
import { useState } from "react"
import NavAfterLogin from "./NavAfterLogin";

const RelatedBlogs=() => {
    const [blogs,setBlogs]=useState(null);
    const fetchBlogs=async () =>{
        try{
            const response=await axios.get("http://localhost:8000/blogs",{
                headers: {'Content-Type':'application/json'}
            });
            if(response.status==200){
                console.log(response.data);
                const data=response.data;
                setBlogs(data);
            }
        } catch{

        }
    }
    return (
        <div className="BlogPageContainer">
            <NavAfterLogin />
            <div className="BlogsConatiner">
                {blogs && blogs.map((blog,index))}
            </div>
        </div>
    );
}