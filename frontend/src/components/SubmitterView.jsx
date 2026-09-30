import { useEffect, useRef, useState } from "react";
import { createSubmission, downloadSubmission, listSubmissions } from "../api";
import SubmissionList from "./SubmissionList";

export default function SubmitterView({ userId }) {
  const fileInput = useRef(null);
  const [title, setTitle] = useState("");
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setSubmissions(await listSubmissions(userId));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [userId]);

  async function onSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const file = fileInput.current?.files?.[0];
      if (!file) {
        throw new Error("Choose a document file");
      }
      await createSubmission(userId, { title: title.trim(), file });
      setTitle("");
      fileInput.current.value = "";
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="layout">
      <form className="card" onSubmit={onSubmit}>
        <h2>New submission</h2>
        <label>
          Title
          <input value={title} onChange={(event) => setTitle(event.target.value)} required />
        </label>
        <label>
          Document
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.txt,.png,.jpg,.jpeg,.doc,.docx"
            required
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit" disabled={saving}>
          {saving ? "Submitting..." : "Submit for review"}
        </button>
      </form>
      <SubmissionList
        title="Your submissions"
        submissions={submissions}
        loading={loading}
        empty="You have not submitted a document yet."
        onDownload={async (submission) => {
          try {
            await downloadSubmission(userId, submission.id, submission.original_filename);
          } catch (err) {
            setError(err.message);
          }
        }}
      />
    </section>
  );
}
