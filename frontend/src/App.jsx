import { useState, useRef, useEffect } from "react";
import "./App.css";
import { uploadResume, runAnalysis } from "./api";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const INITIAL_MESSAGE = { sender: "bot", text: "안녕하세요! 이력서를 업로드해주세요." };

function App() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [stage, setStage] = useState("awaiting_resume");
  const [resumeId, setResumeId] = useState(null);
  const [jdUrlInput, setJdUrlInput] = useState("");

  // 채팅창 맨 아래를 가리키는 손잡이. 메시지가 추가될 때마다 이 지점으로 스크롤한다.
  const bottomRef = useRef(null);

  function addMessage(sender, text) {
    setMessages((prev) => [...prev, { sender, text }]);
  }

  // messages, stage가 바뀔 때마다(메시지가 추가되거나 로딩 표시가 뜰 때마다)
  // 채팅창을 맨 아래로 자동 스크롤한다.
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, stage]);

  async function revealResultMessages(result) {
    await sleep(3000);
    addMessage("bot", `분석이 끝났어요! 적합도는 ${result.fit_score}점이에요.`);

    if (result.strengths && result.strengths.length > 0) {
      await sleep(3000);
      const strengthsText = result.strengths
        .map((s, i) => `${i + 1}. ${s}`)
        .join("\n");
      addMessage("bot", `강점은 이런 부분이에요:\n${strengthsText}`);
    }

    if (result.gaps && result.gaps.length > 0) {
      await sleep(3000);
      const gapsText = result.gaps.map((g, i) => `${i + 1}. ${g}`).join("\n");
      addMessage("bot", `보완하면 좋을 부분은 이런 점들이에요:\n${gapsText}`);
    }

    if (result.resume_feedback) {
      await sleep(3000);
      addMessage("bot", result.resume_feedback.overall_feedback);

      const sectionFeedbacks = result.resume_feedback.section_feedbacks || [];
      for (const feedback of sectionFeedbacks) {
        await sleep(3000);
        addMessage(
          "bot",
          `원문: "${feedback.original_text}"\n\n` +
            `아쉬운 점: ${feedback.issue}\n\n` +
            `이렇게 고치면 좋을 것 같아요:\n"${feedback.rewritten_example}"`
        );
      }
    }

    await sleep(3000);
    addMessage("bot", "여기까지가 분석 결과예요. 수고하셨어요!");
  }

  async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    addMessage("user", file.name);
    setStage("uploading");

    try {
      const resumeData = await uploadResume(file);
      setResumeId(resumeData.resume_id);
      addMessage("bot", "이력서를 잘 받았어요. 이제 채용공고 URL을 입력해주세요.");
      setStage("awaiting_jd");
    } catch (err) {
      addMessage("bot", `이력서 업로드 중 문제가 생겼어요: ${err.message}`);
      setStage("awaiting_resume");
    }
  }

  async function handleJdSubmit() {
    if (!jdUrlInput.trim()) return;

    const url = jdUrlInput.trim();
    addMessage("user", url);
    setJdUrlInput("");
    setStage("processing");

    try {
      const analysisData = await runAnalysis(url, resumeId);
      await revealResultMessages(analysisData);
      setStage("done");
    } catch (err) {
      addMessage("bot", `분석 중 문제가 생겼어요: ${err.message}`);
      setStage("awaiting_jd");
    }
  }

  function handleRestart() {
    setMessages([INITIAL_MESSAGE]);
    setStage("awaiting_resume");
    setResumeId(null);
    setJdUrlInput("");
  }

  return (
    <div className="app-container">
      <h1 className="app-title">채용공고 맞춤 이력서 분석 AI</h1>

      <div className="chat-card">
        <div className="chat-window">
          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.sender === "bot" ? "message-row fade-in" : "message-row user-row fade-in"
              }
            >
              {message.sender === "bot" && <div className="bot-avatar">AI</div>}
              <div
                className={
                  message.sender === "bot" ? "message bot-message" : "message user-message"
                }
                style={{ whiteSpace: "pre-line" }}
              >
                {message.text}
              </div>
            </div>
          ))}

          {stage === "awaiting_resume" && (
            <div className="message-row user-row">
              <label className="inline-file-button">
                이력서 파일 선택
                <input
                  type="file"
                  accept=".docx,.txt"
                  onChange={handleFileSelect}
                  style={{ display: "none" }}
                />
              </label>
            </div>
          )}

          {stage === "uploading" && (
            <div className="message-row">
              <div className="bot-avatar">AI</div>
              <div className="message bot-message">
                <span className="spinner"></span>업로드 중이에요...
              </div>
            </div>
          )}

          {stage === "awaiting_jd" && (
            <div className="message-row user-row">
              <div className="inline-jd-input">
                <input
                  type="text"
                  placeholder="채용공고 URL을 입력해주세요"
                  value={jdUrlInput}
                  onChange={(event) => setJdUrlInput(event.target.value)}
                  className="text-input"
                  onKeyDown={(event) => {
                    if (event.key === "Enter") handleJdSubmit();
                  }}
                />
                <button onClick={handleJdSubmit} className="send-button">
                  전송
                </button>
              </div>
            </div>
          )}

          {stage === "processing" && (
            <div className="message-row">
              <div className="bot-avatar">AI</div>
              <div className="message bot-message">
                <span className="spinner"></span>채용공고를 분석하고 있어요...
              </div>
            </div>
          )}

          {stage === "done" && (
            <div className="message-row">
              <button onClick={handleRestart} className="restart-button">
                다시 분석하기
              </button>
            </div>
          )}

          {/* 이 빈 div가 항상 채팅창의 맨 아래를 가리킨다. 스크롤 목표 지점. */}
          <div ref={bottomRef}></div>
        </div>
      </div>
    </div>
  );
}

export default App;