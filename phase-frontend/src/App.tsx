import React from 'react';
import logo from './logo.svg';
import './App.css';

import Form from '../src/components/Form';
import SummaryPage from './pages/Summary';
import QuizPage from './pages/Quiz';

function App() {
  return (
    <div>
      <Form />
      <SummaryPage />
      <QuizPage />
    </div>
  );
}

export default App;
