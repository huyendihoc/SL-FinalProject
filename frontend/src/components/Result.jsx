const Result = ({reviews}) => {
    if (reviews.length === 0) {
        return <></>
    }
    else if ("error" in reviews){
        return (
            <div className='search-result'>
                Result: {reviews.error}
            </div>
        )
    }
    else {
        return (
            <div className="search-result">
                Result: {reviews[0].Title} from {reviews[0].Platform}
            </div>
        )
    }
}

export default Result