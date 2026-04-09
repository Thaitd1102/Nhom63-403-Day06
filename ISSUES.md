# GitHub Issues — Phân công 5 thành viên

---

## 🔧 Issue #1: Xây dựng LangGraph Agent Framework

**Assignee:** Thái + Huy  
**Due:** 13:00 09/04/2026 (cuối ngày D5)  
**Label:** agent, critical

### Mô tả
Xây dựng LangGraph agent orchestration framework cho chatbot VinFast.

### Checklist
- [ ] Setup `AgentState` với message history (add_messages)
- [ ] Implement `agent_node` — gọi LLM với tools binding
- [ ] Implement `tool_node` — chạy tools (query_pdf, search_models, etc.)
- [ ] Build StateGraph: START → agent → tools (conditional) → agent (loop) → END
- [ ] Integrate MemorySaver với thread_id ("main_chat") → multi-turn conversation work
- [ ] Test agent.py 10+ scenarios (VF3 giá, VF8 pin, so sánh, tính chi phí)
- [ ] Ensure system_prompt loaded từ file, tools ưu tiên query_pdf #1

### Acceptance Criteria
- Multi-turn conversation hoạt động OK (user hỏi 5+ câu liên tiếp)
- Tool call success rate ≥ 95%
- Response time < 2 sec/query
- Không crash khi RAG API key không có

---

## 📚 Issue #2: Tích hợp RAG System từ PDF

**Assignee:** Thái + Huy  
**Due:** 13:00 09/04/2026 (cuối ngày D5)  
**Label:** rag, critical

### Mô tả
Implement RAG system để AI trích thông tin chính xác từ PDF VINFAST VF1.pdf.

### Checklist
- [ ] Extract text từ PDF dùng PdfReader → test tất cả page
- [ ] Implement RecursiveCharacterTextSplitter (chunk_size=800, overlap=200)
- [ ] Setup OpenAI embeddings (hoặc fallback SimpleEmbedding nếu không có API key)
- [ ] Create Chroma vector store, persist vào `vector_db/` folder
- [ ] Setup retriever: similarity search, return top 3 chunks
- [ ] Implement `query_pdf()` tool — PRIORITY #1 trong tool list
- [ ] Test retrieval: hỏi 10 câu → accuracy ≥ 85%

### Acceptance Criteria
- Vector store tạo & load thành công
- Fallback embeddings không crash khi API key missing
- Retrieval output có relevance (không lạc đề)
- `query_pdf` được gọi trước mọi tool khác

---

## 🔨 Issue #3: Implement Tools + System Prompt

**Assignee:** Ánh  
**Due:** 12:00 09/04/2026 (trưa D5)  
**Label:** tools, system-prompt

### Mô tả
Implement 5 tools cho agent + viết system prompt hướng dẫn agent.

### Checklist
- [ ] `search_models(budget, body_type)` — tìm xe phù hợp
- [ ] `compare_models(model1, model2)` — so sánh specs 2 xe
- [ ] `calculate_total_cost(model, loan_duration, interest_rate)` — tính tổng chi phí (giá + bảo hiểm + bảo trì + điện)
- [ ] `get_vehicle_info(model_name)` — lấy thông tin xe theo tên
- [ ] Tool definitions chuẩn (docstring, parameters, return type)
- [ ] Viết system_prompt.txt — hướng dẫn agent:
  - Luôn gọi `query_pdf` trước (để lấy dữ liệu chính xác)
  - Gợi ý (augmentation) chứ không auto quyết định
  - Rejection graceful khi user hỏi out-of-scope
- [ ] Test tools: mỗi tool chạy 5+ test cases, verify output format STRING

### Acceptance Criteria
- Tất cả 5 tools return chuẩn định dạng STRING
- System prompt force agent ưu tiên query_pdf
- Tools respond < 1 sec
- Không có tool error khi invalid input

---

## 🎨 Issue #4: Build Prototype UI + Demo

**Assignee:** Hưng  
**Due:** 11:00 09/04/2026 (M2), refined 15:30  
**Label:** prototype, ui, demo

### Mô tả
Xây dựng prototype UI cho chatbot + chuẩn bị demo flow.

### Checklist (Prototype)
- [ ] Build HTML/CSS/JS chatbot interface (Claude Artifacts hoặc v0)
- [ ] Hiển thị conversation (user message + AI response)
- [ ] Mock test API (hoặc real API nếu backend ready)
- [ ] Input form để user hỏi (textarea + button)
- [ ] Display agent thinking (logging tools being called)

### Checklist (Demo)
- [ ] Demo script 5 phút: cái gì, tại sao, giải pháp nào
- [ ] Chạy 3 scenario:
  1. User hỏi giá xe (query_pdf + search_models)
  2. User hỏi so sánh 2 xe (compare_models)
  3. User hỏi tổng chi phí (calculate_total_cost)
- [ ] Poster/slides tóm tắt: Problem → Solution → Auto/Aug → Demo flow
- [ ] Setup poster (in hoặc digital), readable từ 2m away

### Acceptance Criteria
- Prototype chạy được live (≥ mock prototype)
- Demo narrative rõ, không bị "magic"
- Đã test 10+ lần trước demo day
- Poster/slides in sẵn hoặc digital version ready

---

## ✅ Issue #5: SPEC Final + Testing + QA

**Assignee:** Quân  
**Due:** 23:59 09/04/2026  
**Label:** spec, testing, qa

### Mô tả
Finalize SPEC document, test edge cases, và QA trước submission.

### Checklist (SPEC)
- [ ] AI Product Canvas: Value / Trust / Feasibility + learning signal
- [ ] User Stories 4 paths (Happy / Low-confidence / Failure / Correction)
- [ ] Eval metrics + threshold (Retrieval 85%, Tool call 95%, Response < 2s)
- [ ] Top 3 failure modes + mitigation:
  - PDF không có → fallback DB
  - No API key → SimpleEmbedding
  - Out-of-scope → graceful rejection
- [ ] ROI 3 kịch bản (Conservative / Realistic / Optimistic)
- [ ] Mini AI spec (1 trang tóm tắt)

### Checklist (Testing)
- [ ] Test edge cases:
  - Empty input
  - Budget = 0
  - Model không tồn tại
  - Câu hỏi out-of-scope
  - PDF query khi API key missing
- [ ] Test multi-turn: user hỏi 10+ câu liên tiếp, context không mất
- [ ] Test performance: P99 response time < 3s
- [ ] Test fallback: disable OPENAI_API_KEY → system vẫn chạy

### Acceptance Criteria
- SPEC đủ 6 phần, mỗi phần cụ thể (không generic)
- Tất cả test cases pass
- Documentation rõ (README, deployment guide)
- Code clean, comments đầy đủ

---

## 📋 Timeline tổng hợp

| Thời gian | Milestone | Owner |
|-----------|-----------|-------|
| **D5 morning** | M1: Canvas check, start build | Tất cả |
| **D5 11:00** | M2: Prototype demo ready (mock OK) | Hưng |
| **D5 12:00** | Tools + System Prompt đủ | Ánh |
| **D5 13:00** | Agent + RAG framework hoàn thành | Thái + Huy |
| **D5 evening** | SPEC draft, test edge cases | Quân |
| **D6 09:00** | M1: SPEC final review | Quân |
| **D6 11:00** | M2: Prototype chạy được (refine) | Hưng |
| **D6 13:00** | M3: SPEC final lock + demo flow draft | Quân + Hưng |
| **D6 15:30** | M4: Demo dry run + checklist | Tất cả |
| **D6 16:00-18:00** | M5-M6: Demo Round + Award | Tất cả |

---

## Dependency Graph

```
Tools + System Prompt (Ánh)  ──┐
                               ├──→ Agent Framework (Thái + Huy) ──┐
RAG System (Thái + Huy)      ──┘                                   │
                                                                  ├──→ Demo (Hưng)
                                                                  │
SPEC (Quân) ───────────────────────────────────────────────────┘
```

---

## Notes for Demo Day

- **Thái**: Giải thích Agent architecture + RAG fallback robustness
- **Huy**: Debug & support, test scenarios
- **Ánh**: Giới thiệu tools & system prompt logic
- **Hưng**: Demo UI, narrative flow, Q&A handling
- **Quân**: Present SPEC, explain metrics & failure modes
