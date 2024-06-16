import { useState, useEffect } from "react";
import axios from 'axios';


const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true
});

export default function SummaryPage() {
  const [summary, setSummary] = useState("")

  useEffect(() => { // is there a cleaner way to do this?
    getSummary();
  }, []);

  const getSummary = async() => {
    try {
        let result = await axiosInstance.get('/get_daily_summary');
        console.log("Result", result)
        setSummary(result.data)
    } catch (e) {
        console.log(e)
    }
  }

//   console.log(watch("link"))
  return (
    <div>{summary === null ? "null" : summary}</div>
  )
}