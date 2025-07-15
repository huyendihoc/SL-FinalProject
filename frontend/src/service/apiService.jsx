import axios from 'axios'

const fetchMovie = async (movie, platform) => {
    const res = await axios.get(`/${platform}/${movie}`)
    return res.data
}

export {fetchMovie}