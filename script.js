const API_BASE = "https://myprotector-backend.onrender.com/v1";


document.getElementById("scanBtn").onclick = async () => {
  const prompt = document.getElementById("promptInput").value;
  const box = document.getElementById("resultBox");

  const res = await fetch(`${API_BASE}/prompt/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();

  box.className = "result " + data.decision;
  box.innerHTML = `
    <strong>${data.decision}</strong><br>
    Risk Score: ${data.risk_score}<br>
    ${data.reasons.join(", ")}
  `;
};

document.getElementById("claimApiBtn").onclick = async () => {
  const email = prompt("Enter your email to claim API key:");
  if (!email) return;

  const res = await fetch(`${API_BASE}/api/claim`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });

  const data = await res.json();
  alert("API Key:\n" + data.api_key);
};
