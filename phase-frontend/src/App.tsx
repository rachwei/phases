import React from 'react';
import logo from './logo.svg';
import './App.css';

import Form from '../src/components/Form';
import SummaryPage from './pages/Summary';

function App() {
  return (
    <div>
      <Form />
      <SummaryPage />
    </div>
  );
}

export default App;
