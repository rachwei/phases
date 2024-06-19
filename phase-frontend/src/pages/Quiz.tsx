import { useState, useEffect } from "react";
import axios from 'axios';
import {Quiz} from '../types'


const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true
});



export default function QuizPage() {
    const [quiz, setQuiz] = useState<Quiz | null>(null);

  const getQuiz = async() => {
    try {
        let result = await axiosInstance.get('/get_daily_quiz');
        console.log("Result", result)
        setQuiz(result.data.quiz)
    } catch (e) {
        console.log(e)
    }
  }

  const answerQuestion = async(quiz_id: string, question: string, answer: string) => {
    console.log("Answering quiz " + quiz_id + " with question: " + question + " and answer: " + answer);
    console.log(quiz_id)
    
    try {
        const quiz_contents = {user_id: 0, quiz_id: quiz_id, question: question, answer: answer}
        const result = await axiosInstance.post('/answer_question_from_quiz', { quiz_contents });
        console.log("Result", result.data);
    } catch (e) {
        console.error(e);
    }
  }

//   console.log(watch("link"))
  return (
    <div>
        <button onClick={getQuiz}>Get Quiz</button>
        <div>
            {quiz && quiz.questions.map((question, index) => (
                <div key={index}>
                    <h3>{question.question}</h3>
                    <ul>
                        {question.answers.map((answer, idx) => (
                            <button key={String(index) + " " + String(idx)} onClick={(event) => answerQuestion(quiz._id, question.question, answer)}>{answer}</button>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    </div>
  )
}