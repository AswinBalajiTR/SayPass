async function authenticate() {
  const status = document.getElementById("status");
  status.innerText = "🎤 Recording voice...";

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  let audioChunks = [];

  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("audio", audioBlob, "test_voice.wav");

    const response = await fetch("/verify", {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    status.innerText = result.status === "granted"
      ? "✅ Access Granted!"
      : "❌ Access Denied!";
  };

  audioChunks = [];
  mediaRecorder.start();
  setTimeout(() => mediaRecorder.stop(), 5000); // record for 5 seconds
}
