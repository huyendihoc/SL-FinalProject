import { useState } from 'react';
import imdbLogo from '../assets/IMDB_Logo_2016.svg';
import rottenTomatoesLogo from '../assets/Rotten_Tomatoes_logo.svg';
import metacriticLogo from '../assets/Metacritic_logo.svg';

const Dropdown = ({platform, setPlatform}) => {
  const [isOpen, setIsOpen] = useState(false);

  const platforms = [
    { name: 'IMDb', logo: imdbLogo },
    { name: 'Rotten Tomatoes', logo: rottenTomatoesLogo },
    { name: 'Metacritic', logo: metacriticLogo },
  ];

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleSelect = (platform) => {
    setPlatform(platform.name);
    setIsOpen(false);
  };

  return (
    <div className="custom-dropdown">
      <div className="dropdown-header" onClick={toggleDropdown}>
        <img
          src={platforms.find((p) => p.name === platform).logo}
          alt={platform}
          className="dropdown-logo"
        />
      </div>
      {isOpen && (
        <ul className="dropdown-list">
          {platforms.map((p) => (
            <li
              key={p.name}
              className="dropdown-item"
              onClick={() => handleSelect(p)}
            >
              <img
                src={p.logo}
                alt={p.name}
                className="dropdown-logo"
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Dropdown;