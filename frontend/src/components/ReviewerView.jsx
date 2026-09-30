import { useEffect, useState } from "react";
import { decideSubmission, downloadSubmission, listSubmissions } from "../api";
import SubmissionList from "./SubmissionList";

const FILTERS = [
  { id: "pending", label: "Pending" },
  { id: "approved", label: "Approved" },
  { id: "rejected", label: "Rejected" },
  { id: "", label: "All" },
];

export default function ReviewerView({ userId }) {
  const [status, setStatus] = useState("pending");
  const [submissions, setSubmissions] = useState([]);
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");

  async function load(nextStatus = status) {
    setLoading(true);
    setError("");
    try {
      setSubmissions(await listSubmissions(userId, nextStatus || undefined));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(status);
  }, [userId, status]);

  async function decide(submissionId, nextStatus) {
    setBusyId(submissionId);
    setError("");
    try {
      await decideSubmission(userId, submissionId, nextStatus, notes[submissionId]);
      setNotes((current) => ({ ...current, [submissionId]: "" }));
      await load(status);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="stack">
      <div className="filters">
        {FILTERS.map((filter) => (
          <button
            key={filter.label}
            type="button"
            className={status === filter.id ? "active" : ""}
            onClick={() => setStatus(filter.id)}
          >
            {filter.label}
          </button>
        ))}
      </div>
      {error ? <p className="error">{error}</p> : null}
      <SubmissionList
        title="Submissions"
        submissions={submissions}
        loading={loading}
        empty="No submissions in this view."
        onDownload={async (submission) => {
          try {
            await downloadSubmission(userId, submission.id, submission.original_filename);
          } catch (err) {
            setError(err.message);
          }
        }}
        renderActions={(submission) =>
          submission.status === "pending" ? (
            <div className="actions">
              <input
                placeholder="Optional note"
                value={notes[submission.id] || ""}
                onChange={(event) =>
                  setNotes((current) => ({
                    ...current,
                    [submission.id]: event.target.value,
                  }))
                }
              />
              <button
                type="button"
                disabled={busyId === submission.id}
                onClick={() => decide(submission.id, "approved")}
              >
                {busyId === submission.id ? "Saving..." : "Approve"}
              </button>
              <button
                type="button"
                className="danger"
                disabled={busyId === submission.id}
                onClick={() => decide(submission.id, "rejected")}
              >
                Reject
              </button>
            </div>
          ) : null
        }
      />
    </section>
  );
}
