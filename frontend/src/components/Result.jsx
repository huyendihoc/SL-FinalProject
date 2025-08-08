const Result = ({reviews}) => {
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
                Result: {reviews[0].Title} from {reviews[0].Platform}
            </span>
        )
    }
}

export default Result