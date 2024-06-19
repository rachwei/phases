export interface Question {
    question: string;
    answers: string[];
    correct_answer: string;
}

export interface Quiz {
    _id: string;
    questions: Question[];
    date: string;
    created_at: string; // or Date if you handle date conversion
}