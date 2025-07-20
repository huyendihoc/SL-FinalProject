import './App.css';
import { useState } from 'react';
import Header from './components/Header' 
import Table from './components/Table' 
import { fetchMovie } from './service/api';

const App = () => {

  const [platform, setPlatform] = useState('imdb');
  const [movie, setMovie] = useState('');
  const [reviews, setReviews] = useState([])

  const handleSearch = async() => {
    try {
      const reviews = await fetchMovie(movie.trim(), platform);
      setReviews(reviews);
    } catch(error){
      console.log(error);
    }
  }

  return (
    <div className="app">
      <Header 
        platform={platform} 
        setPlatform={setPlatform} 
        movie={movie}
        setMovie={setMovie}
        handleSearch={handleSearch}
      />
      <Table reviews={reviews}/>
    </div>
  );
}

export default App;