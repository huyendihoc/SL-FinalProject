import './App.css';
import { useState } from 'react';
import Header from './components/Header' 
import Table from './components/Table' 
import { fetchMovie } from './service/api';
import Result from './components/Result';

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
      <Result reviews={reviews}/>
      <Table reviews={reviews}/>
    </div>
  );
}

export default App;