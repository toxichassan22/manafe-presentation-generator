function sendToStreamlit(value) {
  window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value }, "*");
}
function setFrameHeight(h) {
  window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: h || document.body.scrollHeight + 40 }, "*");
}
function signalReady() {
  window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }, "*");
}
function escHtml(s) {
  const d = document.createElement("div");
  d.textContent = s || "";
  return d.innerHTML;
}
