import { useState } from "react";

export default function Sidebar() {
  const [file, setFile] = useState(null);
  const [company, setCompany] = useState("quickbite");

  const handleUpload = async () => {
    if (!file) {
      alert("Select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_id", company);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      alert("Upload success");
      console.log(data);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  return (
    <div className="sidebar">
      <h2>AI Copilot</h2>

      <select onChange={(e) => setCompany(e.target.value)}>
        <option value="quickbite">QuickBite</option>
        <option value="shopkart">ShopKart</option>
      </select>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />

      <button onClick={handleUpload}>
        Upload Document
      </button>
    </div>
  );
}