import axios from "axios";
import { useState } from "react"

const RelatedBlogs=() => {
    const [blogs,setBlogs]=useState({

    });
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
}