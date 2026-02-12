const form = document.querySelector("#plan-form");
const resultRoot = document.querySelector("#result");
const submitBtn = document.querySelector("#submitBtn");
const apiBaseInput = document.querySelector("#apiBase");

const CURRENCY = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
  maximumFractionDigits: 0,
});

function restoreApiBase() {
  const saved = window.localStorage.getItem("travel_mvp_api_base");
  apiBaseInput.value = saved || "http://127.0.0.1:8000";
}

function saveApiBase(value) {
  window.localStorage.setItem("travel_mvp_api_base", value);
}

function toPreferences(raw) {
  return raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function renderNeedMoreInfo(payload) {
  const missing = (payload.missing_fields || []).map((field) => `<li class="risk-item">${field}</li>`).join("");
  resultRoot.innerHTML = `
    <div class="result-head">
      <h2>输入校验</h2>
      <span class="status-pill error">信息不完整</span>
    </div>
    <p>${payload.message || "请补全参数后重试。"}</p>
    <ul class="risk-list">${missing}</ul>
  `;
}

function renderSuccess(payload) {
  const total = payload.price_breakdown.total;
  const budget = payload.request_summary.budget_cny;
  const budgetState = total <= budget ? "预算内" : "预算超出";
  const budgetClass = total <= budget ? "ok" : "warn";

  const itineraryHtml = payload.itinerary
    .map(
      (item) => `
      <li class="itinerary-item">
        <h3>Day ${item.day}</h3>
        <div class="meta">
          <span class="chip">上午：${item.morning}</span>
          <span class="chip">下午：${item.afternoon}</span>
          <span class="chip">晚间：${item.evening}</span>
        </div>
      </li>
    `
    )
    .join("");

  const riskHtml =
    payload.risk_flags.length > 0
      ? payload.risk_flags.map((risk) => `<li class="risk-item">${risk}</li>`).join("")
      : '<li class="chip">无高风险项</li>';

  resultRoot.innerHTML = `
    <div class="result-head">
      <h2>规划结果</h2>
      <span class="status-pill ${budgetClass}">${budgetState}</span>
    </div>
    <div class="cards">
      <div class="card"><strong>总价估算</strong><span>${CURRENCY.format(total)}</span></div>
      <div class="card"><strong>用户预算</strong><span>${CURRENCY.format(budget)}</span></div>
      <div class="card"><strong>人工接管</strong><span>${payload.handoff_to_human ? "是" : "否"}</span></div>
    </div>
    <div class="meta">
      <span class="chip">目的地：${payload.request_summary.destination}</span>
      <span class="chip">天数：${payload.request_summary.days}</span>
      <span class="chip">人数：${payload.request_summary.travelers}</span>
      <span class="chip">偏好：${(payload.request_summary.preferences || []).join(" / ") || "未填写"}</span>
    </div>
    <h3>行程安排</h3>
    <ul class="itinerary-list">${itineraryHtml}</ul>
    <h3>风险标签</h3>
    <ul class="risk-list">${riskHtml}</ul>
  `;
}

async function submitPlan(event) {
  event.preventDefault();
  submitBtn.disabled = true;
  submitBtn.classList.add("loading");
  submitBtn.textContent = "生成中...";

  const apiBase = apiBaseInput.value.trim().replace(/\/+$/, "");
  saveApiBase(apiBase);

  const payload = {
    destination: document.querySelector("#destination").value.trim(),
    days: Number(document.querySelector("#days").value),
    travelers: Number(document.querySelector("#travelers").value),
    budget_cny: Number(document.querySelector("#budget").value),
    preferences: toPreferences(document.querySelector("#preferences").value),
  };

  try {
    const response = await fetch(`${apiBase}/api/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`HTTP ${response.status}: ${detail}`);
    }

    const result = await response.json();
    resultRoot.classList.remove("hidden");

    if (result.status === "need_more_info") {
      renderNeedMoreInfo(result);
    } else {
      renderSuccess(result);
    }
  } catch (error) {
    resultRoot.classList.remove("hidden");
    resultRoot.innerHTML = `
      <div class="result-head">
        <h2>请求失败</h2>
        <span class="status-pill error">网络或服务异常</span>
      </div>
      <p>${error instanceof Error ? error.message : "未知错误"}</p>
      <p>请确认后端服务已启动，并且 API 地址可访问。</p>
    `;
  } finally {
    submitBtn.disabled = false;
    submitBtn.classList.remove("loading");
    submitBtn.innerHTML = `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M5 12h11.17l-3.59-3.59L14 7l6 6-6 6-1.42-1.41L16.17 14H5z"></path>
      </svg>
      生成规划
    `;
  }
}

restoreApiBase();
form.addEventListener("submit", submitPlan);

