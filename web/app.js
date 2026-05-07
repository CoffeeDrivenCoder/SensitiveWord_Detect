const textInput = document.querySelector("#textInput");
const checkButton = document.querySelector("#checkButton");
const clearButton = document.querySelector("#clearButton");
const maxReasons = document.querySelector("#maxReasons");
const statusEl = document.querySelector("#status");
const verdictEl = document.querySelector("#verdict");
const summaryEl = document.querySelector("#summary");
const reasonsEl = document.querySelector("#reasons");

function setState(kind, label) {
  statusEl.className = `status ${kind}`;
  statusEl.textContent = label;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;",
  }[char]));
}

function renderResult(result) {
  reasonsEl.innerHTML = "";
  verdictEl.textContent = result.ok ? "True" : "False";
  summaryEl.className = `summary ${result.ok ? "ok" : "bad"}`;

  if (result.ok) {
    setState("ok", "通过");
    summaryEl.textContent = `输入内容未命中敏感词，共 ${result.length} 个字符。`;
    return;
  }

  setState("bad", "命中");
  const words = [...new Set(result.reasons.map((item) => item.word))];
  summaryEl.textContent = `输入内容命中 ${result.reasons.length} 条敏感词规则。问题词：${words.join("、")}`;

  reasonsEl.innerHTML = result.reasons.map((item) => `
    <div class="reason">
      <div class="badWord">
        <span>问题词</span>
        <b>${escapeHtml(item.word)}</b>
      </div>
      <strong>${escapeHtml(item.reason)}</strong>
      <div class="meta">
        <span>分类：${escapeHtml(item.category)}</span>
        <span>来源：${escapeHtml(item.source)}</span>
      </div>
    </div>
  `).join("");
}

async function checkText() {
  const text = textInput.value;
  const limit = Number(maxReasons.value || 20);

  checkButton.disabled = true;
  setState("neutral", "检测中");
  summaryEl.className = "summary";
  summaryEl.textContent = "正在检测...";
  reasonsEl.innerHTML = "";

  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text, maxReasons: limit}),
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "检测失败");
    }
    renderResult(result);
  } catch (error) {
    setState("bad", "错误");
    verdictEl.textContent = "-";
    summaryEl.className = "summary bad";
    summaryEl.textContent = error.message;
  } finally {
    checkButton.disabled = false;
  }
}

checkButton.addEventListener("click", checkText);
clearButton.addEventListener("click", () => {
  textInput.value = "";
  reasonsEl.innerHTML = "";
  verdictEl.textContent = "-";
  summaryEl.className = "summary";
  summaryEl.textContent = "输入内容后点击检测。";
  setState("neutral", "待检测");
  textInput.focus();
});

textInput.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    checkText();
  }
});
