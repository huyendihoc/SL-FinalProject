const Result = ({title, reviews}) => {
    if (reviews.length === 0) {
        return <></>
    }
    else if ("error" in reviews){
        return (
            <span className='search-result'>
                Result: {reviews.error}
            </span>
        )
    }
    else {
        return (
            <span className="search-result">
                {title} from {reviews[0].Platform}
            </span>
        )
    }
}

export default Result