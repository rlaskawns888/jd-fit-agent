const API_BASE_URL = "http://localhost:8000/api/v1";

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/resume/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("이력서 업로드에 실패했습니다.");
  }

  const result = await response.json();
  return result.data; // { resume_id, title, content, ... }
}

export async function runAnalysis(jdUrl, resumeId) {
  const response = await fetch(`${API_BASE_URL}/analysis/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      jd_url: jdUrl,
      resume_id: resumeId,
    }),
  });

  if (!response.ok) {
    throw new Error("JD 분석에 실패했습니다.");
  }

  const result = await response.json();
  return result.data; // AnalysisResponse
}