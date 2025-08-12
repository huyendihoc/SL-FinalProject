import { useState, useEffect, useRef, useCallback } from 'react';
import Dropdown from './Dropdown';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { fetchSuggestions } from '../service/api';

const Header = ({platform, setPlatform, movie, setMovie, id, setID, handleSearch}) => {
    const [suggestions, setSuggestions] = useState([])
    const [showSuggestions, setShowSuggestions] = useState(false)
    const [isLoading, setIsLoading] = useState(false);
    const suggestionsRef = useRef(null);

    const debounce = (func, delay) => {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), delay)
        }
    }

    const fetchAndSetSuggestions = useCallback(debounce(async (searchTerm) => {
        if (searchTerm.length > 2) {
        setIsLoading(true);
        const data = await fetchSuggestions(searchTerm);
        setSuggestions(data);
        setShowSuggestions(data.length > 0);
        setIsLoading(false);
        } else {
        setSuggestions([]);
        setShowSuggestions(false);
        }
    }, 300), []);

    const handleInputChange = (e) => {
        const value = e.target.value;
        setMovie(value);
        fetchAndSetSuggestions(value);
    };

    const handleSuggestionClick = (suggestion) => {
        setMovie(suggestion.Title);
        setID(suggestion.id)
        setShowSuggestions(false);
    };

    const onClick = () => {
        if (movie.trim() !== '' && platform !== '') {
            console.log(`${movie} from ${platform}`);
            handleSearch();
            setMovie('');
            setSuggestions([]);
            setShowSuggestions(false);
        }
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (suggestionsRef.current && 
                !suggestionsRef.current.contains(event.target)) {
                setShowSuggestions(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <header>
        <div className="title-background"></div>
        <span className="section-title">MOVIE REVIEW</span>
        <div className="navigation">
            <Dropdown platform={platform} setPlatform={setPlatform} />
            <div className='search'>
                <div className='search-box' ref={suggestionsRef}>
                    <div className="search-input-container">
                        <input
                        type="text"
                        placeholder="Search movies..."
                        value={movie}
                        onChange={handleInputChange}
                        className="search-input"
                        onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                        />
                        <FontAwesomeIcon icon={faSearch} className="search-icon" />
                        {isLoading && (
                        <div className="loading-indicator">Loading...</div>
                        )}
                    </div>
                    
                    {showSuggestions && suggestions.length > 0 && (
                        <div className="suggestions-container">
                        {suggestions.map((suggestion, index) => (
                            <div 
                            key={index} 
                            className="suggestion-item"
                            onClick={() => handleSuggestionClick(suggestion)}
                            >
                                {suggestion.Poster ? (
                                    <img 
                                    src={suggestion.Poster} 
                                    alt={suggestion.Title} 
                                    className="suggestion-poster"
                                    />
                                ) : (
                                    <div className="poster-placeholder">No Image</div>
                                )}
                                <div className="suggestion-info">
                                    <div className="suggestion-title">{suggestion.Title}</div>
                                    <div className="suggestion-year">{suggestion.Year}</div>
                                </div>
                            </div>
                        ))}
                        </div>
                    )}
                </div>
                <div>
                    <button className='search-button' onClick={onClick}>Search</button>
                </div>
            </div>
        </div>
        </header>
    );
};

export default Header;