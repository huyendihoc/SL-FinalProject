import axios from 'axios'

const baseURL = 'http://localhost:5000'

const fetchMovie = async (imdbID, platform) => {
    const res = await axios.get(`${baseURL}/${platform}/${imdbID}`)
    return res.data 
}

const fetchSuggestions = async(query) =>{
    if (query.length > 2) {
        try {
            const res = await axios.get(`${baseURL}/autocomplete/${query}`)
            return res.data
        } catch (error) {
            console.log({'error': `API error: ${error}`});
            return [];
        }
    }
    return [];
}

export {fetchMovie, fetchSuggestions}