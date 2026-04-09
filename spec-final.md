# SPEC — AI Product Hackathon

**Nhóm:** 63 | **Track:** VinFast

---

## Problem statement

Người cân nhắc mua xe (từ ICE sang điện, hoặc lần đầu mua VinFast) không biết model nào phù hợp với nhu cầu mình, so sánh giá như nào, pin range hay không. Hiện tại họ phải lên Google, đọc review rối rắm, hoặc vào dealership ngồi nói chuyện 30–45 phút với sales (có khi chưa mua đã bị "ép" mua bảo hiểm). AI có thể hỏi 4–5 câu (nhu cầu, budget, km/ngày, ưu tiên: giá/công nghệ/pin) → gợi ý 2–3 model phù hợp + so sánh specs/chính sách bảo dưỡng — giảm thời gian đưa ra quyết định & tăng conversion lead thành khách mua.

---

## 1. AI Product Canvas — EV Recommendation Assistant

## Canvas

| | Value | Trust | Feasibility |
|---|---|---|---|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | **User:** Người đang cân nhắc mua xe (lần đầu mua hoặc chuyển từ xe xăng sang xe điện).<br><br>**Pain:**<br>- Không biết model nào phù hợp với nhu cầu cá nhân<br>- Không hiểu rõ trade-off giữa giá - range - công nghệ<br>- Phải tự research nhiều nguồn (Google, review) -> mất thời gian, dễ rối<br>- Ngại tương tác với sales (bị bias hoặc "ép" mua)<br><br>**AI giải quyết:**<br>- User nhập nhu cầu (budget, km/ngày, ưu tiên...)<br>- AI phân tích và đưa ra 2-3 option phù hợp<br>- Giải thích rõ vì sao phù hợp / không phù hợp<br>- So sánh minh bạch (giá, range, chi phí vận hành)<br><br>**Khác biệt:** Không chỉ trả lời thông tin, mà giúp user hiểu rõ lựa chọn của mình trong 2-3 phút thay vì tự research 1-2 giờ. | **Khi AI sai:**<br>- Phân tích sai (vd: đánh giá range không đủ dù thực tế đủ)<br>- So sánh thiếu chính xác hoặc outdated<br><br>**Khi AI sai -> user bị ảnh hưởng:**<br>- Nhẹ: Mất thời gian (vì phải đọc/so sánh lại)<br>- Trung bình: Hiểu sai về trade-off (vd: nghĩ cần pin lớn hơn thực tế -> tốn thêm tiền)<br>- Nặng: Có thể chọn sai xe -> ảnh hưởng tài chính lớn (vài trăm triệu) + trải nghiệm dùng lâu dài không phù hợp<br><br>**User nhận ra sai khi:**<br>- Output không hợp lý với nhu cầu (vd: đi ít nhưng gợi ý xe đắt)<br>- So sánh mâu thuẫn với kiến thức họ đã biết<br><br>**Cách sửa:**<br>- User chỉnh lại input (budget, nhu cầu...)<br><br>- Feedback nhanh: "Không phù hợp"<br><br>**Quan trọng:** AI luôn giải thích logic, không đưa kết luận áp đặt. | **Cost:** ~ ?<br><br>**Latency:** ~5-7s<br><br>**Tech:**<br>- LLM + rule-based reasoning (constraint theo input user)<br>- Database specs xe (giá, range, policy)<br><br>**Risks:**<br>- Hallucination hoặc dùng dữ liệu cũ<br>- Giải thích sai -> mất trust<br>- Bias (recommend option không tối ưu cho user)<br><br>**Mitigation:**<br>- Hard-code các thông số quan trọng (giá, range)<br>- Output có giải thích rõ ràng<br>- Luôn đưa nhiều option (2-3) thay vì 1 |

## Automation hay Augmentation?

**Lựa chọn:** Augmentation

**Justify:**
- Quyết định mua xe là high-stake -> không thể để AI tự quyết
- AI chỉ đóng vai trò giải thích và hỗ trợ tư duy
- User có toàn quyền chỉnh input / bỏ qua gợi ý
- Cost of reject ≈ 0

Nếu AI sai, user vẫn kiểm soát được nên an toàn hơn automation.

## Learning Signal

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | User correction đi vào đâu? | Khi user sửa lại input (budget, nhu cầu, ưu tiên) -> hệ thống ghi lại để cải thiện gợi ý |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Correction: user đổi input sau khi xem kết quả |
| 3 | Data thuộc loại nào? | User-specific |

## Có Marginal Value Không? 

---

## 2. User Stories — 4 paths

### Feature 1: Tư vấn model dựa trên nhu cầu (AI Advisor)

**Trigger:** User truy cập Landing Page → Click "Tìm xe phù hợp" → Hội thoại 4–5 câu → AI gợi ý.

**Chiến lược ưu tiên:** Recall (Gợi ý đa dạng để user không bỏ lỡ) kết hợp Human-in-the-loop (khi AI chưa chắc).

| Path | Câu hỏi thiết kế | Mô tả |
|---|---|---|
| **Happy — Confident** | User thấy gì? Flow kết thúc ra sao? | User nói "budget 500M, muốn xe điện, lái thành phố" → AI gợi ý **Top 2 xe** (VF e34 + VF8) **kèm giải thích lý do** (Explainability): "VF e34 tối ưu vì chi phí vận hành rẻ nhất, phù hợp lái thành phố". Nút [Đặt cọc ngay] hiện nổi bật → user convert trong 1–2 tap. |
| **Low-confidence — Detect Conflict** | System xử lý ra sao? Lỗ hổng gì? | Lỗ hổng: Nhu cầu mâu thuẫn (budget 400M nhưng muốn xe "sang xịn"). AI không gợi ý suông mà **detect conflict** → hiển thị: "Tôi tìm thấy 2 phương án nhưng có vẻ chưa khớp hoàn toàn ngân sách. Bạn muốn [Nới lỏng ngân sách thêm 100M] hay [Xem xe cũ chính hãng]?" → Human loop ↔ refined decision. |
| **Failure — Graceful + Filters** | User biết AI sai bằng cách nào? Recover ra sao? | Lỗ hổng: AI gợi ý xe SUV rộng → user nhà hẻm nhỏ không vào được. **Graceful failure** (không xin lỗi suông): User bấm nút "Không phù hợp" → AI không hỏi generic mà hiện **bảng lọc nhanh** (Filters): "Nhà tôi [hẻm nhỏ] / [Cần xe 7 chỗ] / [Khác]" → refine constraints → suggest lại. |
| **Correction — Signal2Product** | User điều chỉnh bằng cách nào? Data dùng làm gì? | Lỗ hổng: User thay đổi ý định giữa chừng (slider budget xuống từ 500M → 400M). Đây là **Correction Signal**: Hệ thống ghi lại "ngưỡng giá thực tế" của vùng miền/user segment → **báo cáo Marketing** điều chỉnh chương trình khuyến mãi (VD: "Vùng TP HCM giá threshold 450M, nên chạy flash sale"). Feedback explicit: Bấm "Không phù hợp" → correction log → retrain ranking model. |

### Feature 2: So sánh chi tiết 3 model (Specs + Giá + Highlight VinFast)

**Trigger:** User từ gợi ý hoặc Catalog → Click "So sánh" → Bảng side-by-side + Nhận xét AI.

**Chiến lược ưu tiên:** Precision (Thà thiếu thông tin còn hơn đưa thông số sai gây kiện tụng) + Transparency (Showing Work).

| Path | Câu hỏi thiết kế | Mô tả |
|---|---|---|
| **Happy — Confident** | User thấy gì? Quyết định ra sao? | Bảng so sánh 3 xe (VF8 vs VF e34 vs BYD Atto 3): pin range, giá, trang bị, bảo hành + **Highlight điểm thắng VinFast** (VD: "Bảo hành 10 năm vs 5 năm BYD"). Hiển thị "Showing Work: Đang cập nhật giá lăn bánh mới nhất tại TP.HCM..." → user thấy transparency + trust tăng → click [Đặt cọc]. |
| **Low-confidence — Boundary** | Xử lý dữ liệu đối thủ ra sao? Lỗ hổng gì? | Lỗ hổng: Dữ liệu Tesla/BYD thay đổi liên tục hoặc chưa công bố specs. Xử lý: AI hiến tag **"Tham khảo"** kèm chú thích: "Thông số đối thủ dựa trên nguồn công khai, có thể thay đổi". Nút [Hỏi Sales để đối chiếu] được ưu tiên → Human loop khi precision không đủ. |
| **Failure — Trust Recovery** | Phát hiện & Sửa lỗi ra sao? | Lỗ hổng: AI dùng dữ liệu pin cũ (430km thay vì 450km). Xử lý: Nút [Báo thông tin sai] nằm **ngay cạnh mỗi thông số**. Nếu user báo lỗi → AI phản hồi **"Cảm ơn bạn, tôi đã ghi nhận để cập nhật Catalog"** (explicit gratitude → trust recovery). Boundary: Nếu dữ liệu cũ hơn 1 tuần → show timestamp warning. |
| **Correction — Data Gold** | Data này dùng làm gì? | User chọn field sai + nhập giá trị đúng → Đây là **"Vàng" data**: Giúp **Bộ KỸ THUẬT kiểm soát chất lượng dữ liệu** (Data Quality) + **cập nhật Knowledge Base NGAY** (real-time, không biết chờ). Implicit signal: Track "correction rate by field" → Quality report giúp product team detect **field nào dữ liệu hay bị sai**. |

---

### 3. Eval metrics + threshold

**Optimize precision hay recall?** [ ] Precision · [x] Recall 

**Tại sao?** Để đảm bảo lưới lọc đủ rộng, không bỏ sót bất kỳ khách hàng tiềm năng nào và giữ họ lại trong phễu tư vấn thay vì báo "không tìm thấy xe".

**Nếu sai ngược lại thì chuyện gì xảy ra?** Nếu chọn Precision nhưng low Recall -> Bot quá khắt khe, gặp yêu cầu hơi mâu thuẫn của user sẽ lập tức trả về kết quả rỗng -> User hụt hẫng, thoát khung chat -> Mất Lead (mất khách hàng).

| Metric | Threshold | Red flag (dừng khi) |
| :--- | :--- | :--- |
| **Recommendation Recall** (Tỷ lệ gợi ý trúng xe lý tưởng vào Top 2) | >= 85% | < 75% trong 3 ngày |
| **Conflict Detection Rate** (Tỷ lệ bắt đúng mâu thuẫn nhu cầu/ngân sách) | >= 90% | < 80% trong 1 tuần |
| **Graceful Recovery Rate** (Tỷ lệ user dùng Quick Filters khi AI đoán sai) | >= 40% | < 20% trong 1 tuần |  

---

# Mục 4: Top 3 Failure Modes

## 1. **Misclassification (phân loại sai mức độ nghiêm trọng) — nguy hiểm nhất**

**Mô tả:**
AI hỏi 3–4 câu nhưng:

* Đánh giá nhẹ → trong khi thực tế là lỗi nghiêm trọng (ví dụ pin, phanh, hệ thống điện)
* Hoặc ngược lại → overreact → gây hoang mang

**Hậu quả:**

* Safety risk (worst case)
* Mất niềm tin → user quay lại gọi tổng đài
* Legal risk nếu gây thiệt hại

**Nguyên nhân:**

* Input không đủ (3–4 câu quá ít cho edge cases)
* User mô tả sai triệu chứng
* Dataset chưa cover lỗi hiếm

**Mitigation:**

* “Fail-safe bias”: nghi ngờ → escalate lên CSR
* Không bao giờ khuyến nghị “tiếp tục lái xe” nếu có dấu hiệu nghiêm trọng
* Confidence threshold + fallback:
  → nếu confidence < X → luôn recommend human

---

## 2. **User Misuse / Input Noise (người dùng trả lời sai hoặc thiếu)**

**Mô tả:**

* User chọn bừa để cho nhanh
* Không hiểu câu hỏi kỹ thuật
* Không nhớ km hoặc triệu chứng chính xác

**Hậu quả:**

* "Garbage in → garbage out"
* AI bị đổ lỗi dù lỗi từ input

**Nguyên nhân:**

* UX hỏi không rõ
* Ngôn ngữ quá kỹ thuật
* Không có validation logic

**Mitigation:**

* Hỏi theo kiểu “triệu chứng thực tế” thay vì nặng thuật ngữ chuyên môn
  (vd: “xe rung khi đạp ga?” thay vì “drivetrain abnormality?”)
* Có hình ảnh / icon minh họa
* Detect inconsistency (trả lời mâu thuẫn → hỏi lại)

---

## 3. **Low Adoption / Trust Failure (người dùng không dùng hoặc không tin)**

**Mô tả:**

* Người dùng vẫn gọi tổng đài vì:

  * “AI không đáng tin”
  * “Tôi muốn nói chuyện với người thật”
* Hoặc dùng 1–2 lần rồi bỏ

**Hậu quả:**

* ROI không đạt
* Feature trở thành “dead feature” trong app

**Nguyên nhân:**

* Trải nghiệm đầu không đủ tốt
* Không giải quyết pain point rõ ràng
* Thiếu social proof / trust signal

**Mitigation:**

* Show “AI đã giúp X người xử lý trong 30s”
* Kết hợp human fallback seamless (1 click gọi CSR)
* Early win: tập trung 5–10 case phổ biến nhất trước

---

## 5. ROI — 3 kịch bản

| | Conservative | Realistic | Optimistic |
|---|---|---|---|
| **Assumption** | 500 lead cân nhắc/tháng, 12% convert (60 khách mua) | 2.000 lead/tháng, 15% convert (300 khách) | 5.000 lead/tháng, 18% convert (900 khách) |
| **Cost AI** | ~$500/tháng inference + maintenance | ~$1.500/tháng | ~$3.000/tháng |
| **Benefit** | 60 × $10M margin = $600M (sau khصم trừ cost), tuy nhiên chỉ partial attribution (~50%) = $300M | 300 × $10M × 60% contrib = $1.800M | 900 × $10M × 70% contrib = $6.300M |
| **Net** | +$299.5M/tháng | +$1.798.5M/tháng | +$6.297M/tháng |
| **Payback** | 2 tháng | 1 tháng | <1 tuần |

**Kill criteria:** 
- Conversion rate drop dưới 10% trong 3 tuần liên tục (AI không giúp)
- Precision < 60% (user mất tin tưởng, request CSR override)
- Latency > 4s (user abandon)
- Product catalog accuracy < 95% (reputational risk)

---
## 6. Mini AI Spec — VinFast AI Advisor (Tư vấn mua xe)

---

## Product giải gì, cho ai?

Người cân nhắc mua VinFast (từ xe xăng sang điện, hoặc lần đầu mua VinFast) không biết model nào phù hợp nhu cầu, phải lên Google đọc review rối rắm hoặc vào dealership ngồi 30–45 phút với sales (có khi chưa mua đã bị "ép" mua bảo hiểm).

AI Advisor tích hợp trong app/landing page VinFast giải quyết 2 tình huống:
- **Tư vấn model:** Hỏi 4–5 câu (nhu cầu, budget, km/ngày, ưu tiên giá/công nghệ/pin) → gợi ý top 2–3 model phù hợp (VD: VF e34 vs VF8) kèm lý do cụ thể → nút [Đặt cọc ngay] convert trong 1–2 tap.
- **So sánh specs:** Bảng side-by-side VinFast vs đối thủ (BYD Atto 3, Toyota...) với highlight điểm thắng của VinFast + timestamp để đảm bảo dữ liệu mới nhất.

Mục tiêu: rút ngắn thời gian ra quyết định từ 30–45 phút xuống 2 phút, tăng conversion lead thành khách mua.

---

## AI làm gì — Automation hay Augmentation?

**Augmentation** — AI gợi ý, user quyết định cuối cùng. Human-in-the-loop ở mọi bước quan trọng.

Cụ thể:
- AI gợi ý model + **detect conflict ngân sách** ("budget 400M nhưng muốn xe sang") → không tự chọn hộ, hỏi lại user: "Nới lỏng ngân sách thêm 100M hay xem xe cũ chính hãng?"
- Khi dữ liệu đối thủ không chắc chắn (specs chưa công bố / thay đổi liên tục) → ưu tiên nút **"Hỏi Sales để đối chiếu"**, không tự đưa ra thông số có thể sai.
- User chọn "Không phù hợp" → AI không hỏi generic mà hiện bảng filter nhanh để refine constraints → suggest lại.

Lộ trình: V1 augmentation (hiện tại) → thu correction data → V2 tăng tự động hóa cho các segment phổ biến có độ tin cậy cao.

---

## Quality — Precision hay Recall?

**Chọn: Recall-first** — không bao giờ để AI trả lời "Tôi không tìm thấy xe nào". Gợi ý 2–3 model để user tự lựa chọn, không bỏ sót khách hàng tiềm năng, giữ họ trong phễu tư vấn.

**Nếu chọn ngược lại (Precision, low Recall):** Bot quá khắt khe → gặp yêu cầu mâu thuẫn → trả về kết quả rỗng → user hụt hẫng, thoát khung chat → mất lead.

**Feature tư vấn model: Recall** — gợi ý đa dạng, không bỏ sót option phù hợp. Ràng buộc cứng: chỉ hiển thị tối đa **2 model/lượt** (Top-K Cap = 2) dù confidence cao đến đâu — tránh user bị ngợp.

**Feature so sánh specs: Precision cao** — thà thiếu thông số còn hơn đưa thông số sai (kiện tụng, mất uy tín thương hiệu). Dữ liệu cũ hơn 1 tuần → timestamp warning; nút "Báo thông tin sai" cạnh mỗi thông số.

## Eval Metrics & Ngưỡng chấp nhận

| Metric | Định nghĩa | Target | Kill Criteria |
|--------|-----------|--------|---------------|
| **Recommendation Recall** | % phiên AI đưa "Golden Match" vào Top 2 ngay lần đầu + có Explainability ("Tại sao") | >= 85% | < 75% trong 3 ngày |
| **Conflict Detection Rate** | % lần AI detect input mâu thuẫn (VD: budget 400M + "sang xịn") → kích hoạt prompt thương lượng | >= 90% | < 80% trong 1 tuần |
| **Graceful Recovery Rate** | % user bấm "Không phù hợp" rồi tiếp tục chọn Quick Filter thay vì thoát | >= 40% | < 20% trong 1 tuần |

**Constraint cứng vào system:**
- Top-K Cap: tối đa 2 model/lượt, không list 5 xe
- Từ khóa "Xin lỗi" bị cấm đứng một mình — luôn đi kèm action: *"Có vẻ chưa đúng ý bạn. Nhà bạn có [Hẻm nhỏ] hay cần [Xe 7 chỗ]?"*

---

## Risk chính (từ Failure Mode analysis của nhóm)

| Risk | Hậu quả | Mitigation |
|------|---------|------------|
| AI gợi ý sai model (budget conflict, nhu cầu mâu thuẫn) | User mua nhầm → hoàn trả, khiếu nại, mất niềm tin | Detect conflict + hỏi lại; luôn show lý do gợi ý (Explainability); nút filter "Không phù hợp" |
| User input noise (chọn bừa, không hiểu câu hỏi) | Garbage in → garbage out, AI bị đổ lỗi | Hỏi bằng ngôn ngữ tự nhiên + icon minh họa; detect mâu thuẫn → hỏi lại |
| Dữ liệu đối thủ lỗi thời | Specs sai → mất uy tín, kiện tụng | Tag "Tham khảo" + timestamp; nút "Báo thông tin sai" → cập nhật Knowledge Base real-time |
| Low adoption / trust failure | Feature thành "dead feature", ROI không đạt | Social proof ("AI đã giúp X người chọn xe trong 2 phút"), human fallback 1-click (Hỏi Sales), tập trung 5–10 segment phổ biến trước |

**Kill criteria:**
- Adoption kill: sau 3 tháng adoption < 15–20% hoặc repeat usage < 30%
- Trust kill: user override AI (bỏ qua gợi ý) > 40% hoặc CSAT thấp hơn dealership truyền thống
- ROI kill: cost build + maintain > savings/revenue gain sau 12–18 tháng

---

## Data Flywheel

**Vòng lặp học:**

```
User nhập nhu cầu / budget / ưu tiên
    → AI gợi ý model + detect conflict
        → User xác nhận / sửa / bấm "Không phù hợp" / kéo slider budget
            → Thu correction signal (explicit + implicit)
                → AI ranking chính xác hơn theo vùng miền / segment
                    → User tin hơn → dùng nhiều hơn → nhiều data hơn
```

**Loại signal thu được:**
- **Explicit:** Bấm "Không phù hợp" → correction log → retrain ranking model. Báo thông số sai → cập nhật Knowledge Base real-time.
- **Implicit:** Slider budget user kéo xuống → ghi nhận "ngưỡng giá thực tế" theo vùng miền → báo marketing điều chỉnh khuyến mãi (VD: "TP.HCM threshold 450M → nên chạy flash sale"). Track correction rate by field → detect field nào hay bị sai nhất.
- **Outcome:** Model user thực sự đặt cọc / mua sau khi AI gợi ý → ground truth cho ranking model.

**Marginal value:** VinFast sở hữu data hành vi mua xe VinFast thực tế (conversion, rejection pattern, budget threshold theo vùng miền) — đây là data riêng không AI chung nào có, không thể replicate.

**Base case ROI:** 40% adoption, 90% accuracy, 60% tự ra quyết định không cần gọi sales → tiết kiệm chi phí tư vấn CSR/dealership + tăng conversion rate.

---

## Feasibility

**Tech stack:** LLM + rule-based reasoning (constraint theo input user) + database specs xe (giá, range, chính sách bảo dưỡng).

**Latency:** ~5–7 giây/request — chấp nhận được cho use case tư vấn (không cần real-time).
... (17 lines left)
---
## 7. Phân công

| Thành viên | Phần phụ trách |
|---|---|
| **Ánh** | Mục 1 — AI Product Canvas (Value / Trust / Feasibility + learning signal) |
| **Thái** | Mục 2 — User Stories (4 paths × 2 features) |
| **Huy** | Mục 3 — Eval metrics + threshold |
| **Hưng** | Mục 4 — Top 3 failure modes + Mục 5 — ROI 3 kịch bản + kill criteria |
| **Quân** | Mục 6 — Mini AI spec: problem statement 1 câu + tổng hợp SPEC draft + prototype research & prompt test |

