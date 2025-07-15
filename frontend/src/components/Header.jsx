import { useState } from 'react';
import Dropdown from './Dropdown';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

const Header = ({platform, setPlatform, movie, setMovie, handleSearch}) => {
    const onClick = () => {
        if (movie.trim() !== '' && platform !== ''){
            // handleSearch();
            console.log(`${movie} from ${platform}`);
        }
    }

    return (
        <header>
        <div className="title-background"></div>
        <span className="section-title">MOVIE REVIEW</span>
        <div className="navigation">
            <Dropdown platform={platform} setPlatform={setPlatform} />
            <div className='search-box'>
                <input
                type="text"
                placeholder="Search movies..."
                value={movie}
                onChange={(e)=>{setMovie(e.target.value)}}
                className="search-input"
                />
                <FontAwesomeIcon icon={faSearch} className="search-icon" />
            </div>
            <div>
                <button className='search-button' onClick={onClick}>Search</button>
            </div>
        </div>
        </header>
    );
};

export default Header;