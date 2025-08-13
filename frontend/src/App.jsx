// import './App.css';
// import { useState } from 'react';
// import Header from './components/Header'
// import Table from './components/Table'
// import { fetchMovie } from './service/api';
// import Result from './components/Result';
// import Dashboard from './Dashboard';
// import { BrowserRouter, Routes, Route } from 'react-router-dom';



// const App = () => {

//   const [platform, setPlatform] = useState('imdb');
//   const [movie, setMovie] = useState('');
//   const [reviews, setReviews] = useState([])
//   const [id, setID] = useState('')

//   const handleSearch = async () => {
//     try {
//       const reviews = await fetchMovie(id.trim(), platform);
//       setReviews(reviews);
//     } catch (error) {
//       console.log(error);
//     }
//   }

//   // return (
//   //   <div className="app">
//   //     <Header
//   //       platform={platform}
//   //       setPlatform={setPlatform}
//   //       movie={movie}
//   //       setMovie={setMovie}
//   //       id={id}
//   //       setID={setID}
//   //       handleSearch={handleSearch}
//   //     />
//   //     <Result reviews={reviews} />
//   //     <Table reviews={reviews} />
//   //   </div>
//   // );

//   return (
//     <Router>
//       <Routes>
//         {/* Trang chính */}
//         <Route
//           path="/"
//           element={
//             <div className="app">
//               <Header
//                 platform={platform}
//                 setPlatform={setPlatform}
//                 movie={movie}
//                 setMovie={setMovie}
//                 handleSearch={handleSearch}
//               />
//               <Result reviews={reviews} />
//               <Table reviews={reviews} />
//             </div>
//           }
//         />

//         {/* Trang Dashboard */}
//         <Route
//           path="/dashboard"
//           element={
//             <Dashboard
//               platform={platform}
//               setPlatform={setPlatform}
//               movie={movie}
//               setMovie={setMovie}
//               handleSearch={handleSearch}
//               reviews={reviews}
//             />
//           }
//         />
//       </Routes>
//     </Router>
//   );
// }

// export default App;

import './App.css';
import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Table from './components/Table';
import Result from './components/Result';
import Dashboard from './Dashboard';
import { fetchMovie } from './service/api';

const App = () => {
  const [platform, setPlatform] = useState('imdb');
  const [movie, setMovie] = useState('');
  const [reviews, setReviews] = useState([]);
  const [id, setID] = useState('');

  const handleSearch = async () => {
    try {
      const reviews = await fetchMovie(movie.trim(), platform);
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
              />
              <Result reviews={reviews} />
              <Table reviews={reviews} />
            </div>
          }
        />
        <Route
          path="/dashboard"
          element={
            <Dashboard
              platform={platform}
              setPlatform={setPlatform}
              movie={movie}
              setMovie={setMovie}
              handleSearch={handleSearch}
              reviews={reviews}
              id={id}
              setID={setID}
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
