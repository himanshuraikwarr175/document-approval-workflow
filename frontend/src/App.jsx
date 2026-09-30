import { useEffect, useState } from "react";
import ReviewerView from "./components/ReviewerView";
import SubmitterView from "./components/SubmitterView";
import { USERS } from "./users";

const STORAGE_KEY = "approval-user-id";

export default function App() {
  const [userId, setUserId] = useState(() => {
    const saved = Number(localStorage.getItem(STORAGE_KEY));
    return USERS.some((user) => user.id === saved) ? saved : USERS[0].id;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(userId));
  }, [userId]);

  const user = USERS.find((item) => item.id === userId);

  return (
    <main className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">Document approval</p>
          <h1>Submit a document and track the review.</h1>
        </div>
        <label className="user-picker">
          Signed in as
          <select
            value={userId}
            onChange={(event) => setUserId(Number(event.target.value))}
          >
            {USERS.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} ({item.role})
              </option>
            ))}
          </select>
        </label>
      </header>
      {user.role === "submitter" ? (
        <SubmitterView userId={user.id} />
      ) : (
        <ReviewerView userId={user.id} />
      )}
    </main>
  );
}
