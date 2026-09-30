export default function SubmissionList({
  title,
  submissions,
  loading,
  empty,
  renderActions,
}) {
  return (
    <section className="card">
      <h2>{title}</h2>
      {loading ? <p className="muted">Loading submissions...</p> : null}
      {!loading && submissions.length === 0 ? <p className="muted">{empty}</p> : null}
      <ul className="submission-list">
        {submissions.map((submission) => (
          <li key={submission.id}>
            <div className="submission-heading">
              <h3>{submission.title}</h3>
              <span className={`badge ${submission.status}`}>{submission.status}</span>
            </div>
            <p>{submission.body}</p>
            {submission.reviewer_note ? (
              <p className="note">Note: {submission.reviewer_note}</p>
            ) : null}
            {renderActions ? renderActions(submission) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
