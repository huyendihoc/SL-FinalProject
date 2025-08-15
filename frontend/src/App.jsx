import './App.css';
import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Table from './components/Table';
import Result from './components/Result';
import Dashboard from './Dashboard';
import { fetchMovie, fetchAllReviews } from './service/api';

const App = () => {
  const [platform, setPlatform] = useState('imdb');
  const [movie, setMovie] = useState('');
  const [reviews, setReviews] = useState([]);
  const [dashboardReviews, setDashboardReviews] = useState([]);
  const [id, setID] = useState('');
  const [title, setTitle] = useState('')

  const handleSearch = async () => {
    try {
      const reviews = await fetchMovie(id.trim(), platform);
      setReviews(reviews);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <div className="app">
              <Header
                platform={platform}
                setPlatform={setPlatform}
                movie={movie}
                setMovie={setMovie}
                handleSearch={handleSearch}
                id={id}
                setID={setID}
                setTitle={setTitle}
              />
              <Result title={title} reviews={reviews} />
              <Table id={id} reviews={reviews} />
            </div>
          }
        />
        <Route
          path="/dashboard/:movieId"
          element={
            <Dashboard
              id={id}
              reviews={dashboardReviews}
              setReviews={setDashboardReviews}
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App;