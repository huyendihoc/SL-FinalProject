import { FaSortUp } from 'react-icons/fa';

const Table = ({reviews}) => {  
  if (reviews.length == 0)
    return <table className='comments-table'></table>
  return (
    <table className="comments-table">
      <thead>
        <tr>
          <th style={{width:'60%'}}>Comments <FaSortUp /></th>
          <th style={{width:'25%'}}>Date <FaSortUp /></th>
          <th style={{width:'15%'}}>Categorized as</th>
        </tr>
      </thead>
      <tbody>
        {reviews.map((review, index) => (
          <tr key={index}>
            <td>{review.Comment}</td>
            <td>{review.Date}</td>
            <td>
              <span className={`sentiment ${review.Sentiment.toLowerCase()}`}>
                {review.Sentiment}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
} 

export default Table;