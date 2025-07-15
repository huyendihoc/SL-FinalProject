import { FaSortUp } from 'react-icons/fa';

const Table = () => {
  const comments = [
    { text: "Chưa đủ wow với mình lắm", date: "28/06/2025", sentiment: "NEGATIVE" },
    { text: "Phim rất trình", date: "27/06/2025", sentiment: "POSITIVE" },
    { text: "Màu phim đẹp nhưng nội dung hơi cũ", date: "25/06/2025", sentiment: "NEUTRAL" },
    { text: "Nổi da gà, độc lạ Bình Gold", date: "24/06/2025", sentiment: "POSITIVE" },
    { text: "Thà coi phim ***", date: "23/06/2025", sentiment: "NEGATIVE" },
    { text: "Phim qqjz", date: "22/06/2025", sentiment: "NEGATIVE" },
    { text: "Đáng xem", date: "21/06/2025", sentiment: "POSITIVE" },
  ];

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
        {comments.map((comment, index) => (
          <tr key={index}>
            <td>{comment.text}</td>
            <td>{comment.date}</td>
            <td>
              <span className={`sentiment ${comment.sentiment.toLowerCase()}`}>
                {comment.sentiment}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
} 

export default Table;