import axios from 'axios'

const baseURL = 'http://localhost:5000'

const fetchMovie = async (movie, platform) => {
    const res = await axios.get(`${baseURL}/${platform}/${movie}`)
    return res.data 
}

export {fetchMovie}