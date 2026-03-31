export default function UploadButton() {
  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: form
    });

    alert("Uploaded successfully");
  };

  return (
    <div className="upload">
      <input type="file" onChange={upload} />
    </div>
  );
}