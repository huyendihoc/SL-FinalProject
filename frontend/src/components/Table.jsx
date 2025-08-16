import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, Button } from '@mui/material';

const CommentCell = ({ comment }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [needsShowMore, setNeedsShowMore] = useState(false);
  const contentRef = useRef(null);

  useEffect(() => {
    if (contentRef.current) {
      const lineHeight = parseInt(getComputedStyle(contentRef.current).lineHeight);
      const maxHeight = lineHeight * 4;
      const hasOverflow = contentRef.current.scrollHeight > maxHeight;
      
      setNeedsShowMore(hasOverflow);
    }
  }, [comment]);

  return (
    <div className="comment-container">
      <div
        ref={contentRef}
        className={`comment-content ${isExpanded ? '' : 'line-clamp-4'}`}
      >
        {comment}
      </div>
      
      {needsShowMore && (
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="show-more-button"
        >
          {isExpanded ? 'Show less' : 'Show more'}
        </button>
      )}
    </div>
  );
};

const Table = ({id, reviews}) => {
  const navigate = useNavigate();
  if ((reviews.length === 0) || ('error' in reviews)) {
    return <></>;
  }

  const onClick = () => {
    if (id.trim() !== ''){
      navigate(`/dashboard/${id.trim()}`)
    }
  }

  return (
    <>
      <table className="comments-table">
        <thead>
          <tr>
            <th style={{ width: '60%' }}>Comments</th>
            <th style={{ width: '25%' }}>Date</th>
            <th style={{ width: '15%' }}>Categorized as</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map((review, index) => (
            <tr key={index}>
              <td>
                <CommentCell comment={review.Comment} />
              </td>
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
      <Grid container justifyContent="center" sx={{ mt: 2 }}>
        <Button variant="contained" onClick={onClick}>
          View Dashboard
        </Button>
      </Grid>
    </>
  );
};

export default Table;