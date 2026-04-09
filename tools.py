from langchain_core.tools import tool
from rag import get_rag_context, initialize_rag
import re

# =================================================================
# NGUỒN DỮ LIỆU:
# ✅ PRIMARY: PDF (VINFAST VF1.pdf) query qua RAG — luôn ưu tiên
# ⚠️ FALLBACK: Hard-coded database — chỉ dùng khi RAG không tìm được
# =================================================================

@tool
def query_pdf(question: str) -> str:
    """
    🔴 ƯU TIÊN DÙNG TOOL NÀY TRƯỚC KHI GỌI BẤT KỲ TOOL NÀO KHÁC.

    CHỨC NĂNG: Truy vấn trực tiếp từ tài liệu PDF chính thức VINFAST VF1.pdf
    để lấy thông tin chính xác nhất về xe VinFast.

    Dùng khi:
    - User hỏi bất kỳ thông tin gì về xe VinFast (giá, pin, tính năng, bảo hành...)
    - Cần xác nhận thông tin trước khi dùng các tool khác
    - Thông tin trong tool search_models/compare_models cần kiểm tra lại

    Tham số:
    - question: Câu hỏi của user (VD: "VF3 giá bao nhiêu?", "VF8 pin mấy kWh?")

    OUTPUT: Đoạn văn bản trích từ PDF chứa thông tin liên quan.
    Nếu PDF không có thông tin → trả về chuỗi rỗng → dùng tool khác.
    """
    try:
        context = get_rag_context(question)
        if context and context.strip():
            return f"📖 **Thông tin từ PDF VinFast:**\n\n{context.strip()}"
        else:
            return "⚠️ PDF không có thông tin cụ thể cho câu hỏi này. Dùng database dự phòng."
    except Exception as e:
        return f"❌ Lỗi truy vấn PDF: {e}. Dùng database dự phòng."


VEHICLES_DB = {
    "VF e34": {
        "price": 860_000_000,  # VNĐ — cập nhật theo PDF nếu thay đổi
        "battery_kwh": 39,
        "range_km": 300,
        "charging_time_hours": 8,
        "warranty_years": 10,
        "body_type": "Sedan",
        "dimension": "4.493 x 1.786 x 1.520 mm",
        "safety_features": ["6 airbags", "ABS", "ESP", "Hill Start Assist"],
        "smart_features": ["8-inch touchscreen", "Apple CarPlay", "Android Auto", "Rear camera"],
        "annual_maintenance_cost": 2_500_000,
        "annual_insurance_cost": 3_500_000,
        "electricity_cost_per_100km": 120_000,
    },
    "VF5": {
        "price": 529_000_000,   # VNĐ — theo PDF
        "battery_kwh": 37.2,
        "range_km": 300,          # ~300km/1 lần sạc theo PDF
        "charging_time_hours": 8,  # AC 6.6kW; DC 30 phút đạt 70%
        "warranty_years": 7,       # 7 năm/160.000km theo PDF
        "body_type": "SUV mini 5-seater",
        "dimension": "4.000 x 1.720 x 1.560 mm",
        "safety_features": ["4 airbags", "ABS", "ESC", "Blind Spot Warning", "Emergency brake assist", "Hill Start Assist", "Tire pressure monitoring"],
        "smart_features": ["10-inch touchscreen", "Rear camera", "Apple CarPlay", "Android Auto"],
        "annual_maintenance_cost": 2_200_000,
        "annual_insurance_cost": 3_000_000,
        "electricity_cost_per_100km": 110_000,
    },
    "VF6": {
        "price": 675_000_000,  # Phân khúc B — cập nhật theo PDF
        "battery_kwh": 59.6,
        "range_km": 381,
        "charging_time_hours": 8,
        "warranty_years": 10,
        "body_type": "SUV 5-seater",
        "dimension": "4.238 x 1.820 x 1.594 mm",
        "safety_features": ["6 airbags", "ABS", "ESP", "Rear camera"],
        "smart_features": ["10-inch touchscreen", "Apple CarPlay", "Android Auto", "OTA update"],
        "annual_maintenance_cost": 2_800_000,
        "annual_insurance_cost": 4_000_000,
        "electricity_cost_per_100km": 150_000,
    },
    "VF7": {
        "price": 799_000_000,   # VNĐ — VF7 Eco theo PDF
        "battery_kwh": 75.3,
        "range_km": 431,
        "charging_time_hours": 9,
        "warranty_years": 10,
        "body_type": "SUV 5-seater",
        "dimension": "4.545 x 1.890 x 1.635 mm",
        "safety_features": ["8 airbags", "ABS", "ESP", "360-degree camera"],
        "smart_features": ["12.9-inch touchscreen", "Apple CarPlay", "Android Auto", "Voice control", "OTA update"],
        "annual_maintenance_cost": 3_200_000,
        "annual_insurance_cost": 5_000_000,
        "electricity_cost_per_100km": 165_000,
    },
    "VF8": {
        "price": 1_019_000_000,  # VNĐ — VF8 Eco theo PDF
        "battery_kwh": 75,
        "range_km": 471,          # Cập nhật theo PDF: 471km/1 lần sạc
        "charging_time_hours": 10,
        "warranty_years": 10,
        "body_type": "SUV 5-seater",
        "dimension": "4.650 x 1.895 x 1.675 mm",
        "safety_features": ["8 airbags", "ABS", "ESP", "360-degree camera", "Blind Spot Warning", "Emergency brake assist"],
        "smart_features": ["15.6-inch touchscreen", "Apple CarPlay", "Android Auto", "Voice control", "OTA update"],
        "annual_maintenance_cost": 3_500_000,
        "annual_insurance_cost": 5_200_000,
        "electricity_cost_per_100km": 180_000,
    },
    "VF9": {
        "price": 1_499_000_000,  # VNĐ — Eco 7 chỗ theo PDF
        "battery_kwh": 111,
        "range_km": 500,
        "charging_time_hours": 12,
        "warranty_years": 10,
        "body_type": "SUV 7-seater",
        "dimension": "4.900 x 2.000 x 1.725 mm",
        "safety_features": ["8 airbags", "ABS", "ESP", "360-degree camera", "Adaptive cruise control"],
        "smart_features": ["15.6-inch touchscreen", "Apple CarPlay", "Android Auto", "Voice control", "OTA update", "Panoramic sunroof"],
        "annual_maintenance_cost": 4_500_000,
        "annual_insurance_cost": 7_500_000,
        "electricity_cost_per_100km": 240_000,
    },
    # ⚠️ GIÁ PHẢI KHẾP VỚI PDF (VINFAST VF1.pdf) — cập nhật khi PDF thay đổi
    "VF3": {
        "price": 299_000_000,   # VNĐ — theo PDF VINFAST VF1.pdf
        "battery_kwh": 32,
        "range_km": 210,          # Cập nhật theo PDF
        "charging_time_hours": 6,
        "warranty_years": 10,
        "body_type": "Hatchback",
        "dimension": "4.038 x 1.680 x 1.450 mm",
        "safety_features": ["2 airbags", "ABS", "Rear camera"],
        "smart_features": ["7-inch touchscreen", "Rear camera"],
        "annual_maintenance_cost": 2_000_000,
        "annual_insurance_cost": 2_800_000,
        "electricity_cost_per_100km": 100_000,
    },
}

# Map tên xe viết tắt / sai chính tả → tên chuẩn trong VEHICLES_DB
MODEL_NAME_ALIASES = {
    "vf3": "VF3",
    "vf 3": "VF3",
    "vf5": "VF5",
    "vf 5": "VF5",
    "vf6": "VF6",
    "vf 6": "VF6",
    "vf7": "VF7",
    "vf 7": "VF7",
    "vfe34": "VF e34",
    "vf e34": "VF e34",
    "vfe-34": "VF e34",
    "vf8": "VF8",
    "vf 8": "VF8",
    "vf9": "VF9",
    "vf 9": "VF9",
}

# =================================================================
# HELPER FUNCTIONS – Query PDF via RAG (Primary) + Fallback
# =================================================================

def get_rag_model_context(model_name: str) -> str:
    """
    Query PDF thông qua RAG để lấy thông tin chi tiết về model.
    Return: STRING chứa thông tin từ PDF (hoặc empty string nếu không tìm)
    """
    try:
        query = f"Thông tin chi tiết về xe VinFast {model_name}: giá, pin, range, tính năng, bảo hành"
        context = get_rag_context(query)
        if context and context.strip():
            print(f"✅ RAG found context for {model_name} ({len(context)} chars)")
        return context.strip() if context else ""
    except Exception as e:
        print(f"⚠️ RAG query failed for {model_name}: {e}")
        return ""


def normalize_model_name(name: str) -> str | None:
    """
    Chuẩn hóa tên xe về đúng key trong VEHICLES_DB.
    So sánh exact trước, rồi alias, cuối cùng case-insensitive.
    Return: key trong VEHICLES_DB hoặc None nếu không tìm thấy.
    """
    # Exact match
    if name in VEHICLES_DB:
        return name
    # Alias map
    alias_key = name.strip().lower()
    if alias_key in MODEL_NAME_ALIASES:
        return MODEL_NAME_ALIASES[alias_key]
    # Case-insensitive fallback
    for key in VEHICLES_DB:
        if key.lower() == alias_key:
            return key
    return None


def extract_price_from_text(text: str, model_name: str) -> int | None:
    """
    Parse text từ PDF để tìm giá. Hỗ trợ định dạng: "X triệu", "X.XXX triệu", "X tỷ"
    Return: Giá tính bằng VNĐ (int), hoặc None nếu không tìm được
    """
    if not text:
        return None

    # Tìm "X tỷ" (billions)
    tỷ_match = re.search(r'(\d+[\.,]\d+|\d+)\s*(?:tỷ|tỷ đ|tỷ đồng)', text)
    if tỷ_match:
        try:
            price = float(tỷ_match.group(1).replace(',', '.'))
            return int(price * 1_000_000_000)
        except:
            pass

    # Tìm "X triệu" (millions)
    triệu_match = re.search(r'(\d+[\.,]\d+|\d+)\s*(?:triệu|triệu đ|triệu đồng)', text)
    if triệu_match:
        try:
            price = float(triệu_match.group(1).replace(',', '.'))
            return int(price * 1_000_000)
        except:
            pass

    return None


@tool
def search_models(budget: int, km_per_day: float = 50, vehicle_type: str = "any", priority: str = "balanced") -> str:
    """
    Gọi TOOL NÀY khi và CHỈ KHI user đã NÓI RÕ ngân sách cụ thể.
    Ví dụ: "dưới 800 triệu", "budget 1 tỷ", "khoảng 600M".

    ❌ KHÔNG ĐƯỢC gọi tool này nếu user chưa nói rõ budget.
    ❌ KHÔNG tự đoán / giả định budget mặc định.
    Nếu user chưa nói budget → hỏi lại: "Bạn có ngân sách khoảng bao nhiêu?"

    CHỨC NĂNG: Tìm kiếm model VinFast xe điện phù hợp dựa trên BUDGET.

    Tham số:
    - budget: ngân sách mua xe (VNĐ) do user cung cấp — ĐÂY LÀ RÀNG BUỘC CHÍNH
    - km_per_day: km lái trung bình mỗi ngày (default 50km)
    - vehicle_type: 'sedan', 'suv', 'hatchback', 'any'
    - priority: 'price' (rẻ nhất), 'range' (pin xa), 'comfort' (thoải mái), 'balanced' (cân bằng)

    ⚠️ NGÂN SÁCH LÀ CONSTRAINT TUYỆT ĐỐI: Chỉ gợi ý xe <= budget
    """
    
    # === BƯỚC 1: Query PDF trước (PRIMARY) ===
    print(f"🔍 [search_models] Querying PDF for budget={budget/1_000_000:.0f}M...")
    rag_query = f"Danh sách xe VinFast giá dưới {budget/1_000_000:.0f} triệu đồng. Thông tin giá, pin, tầm hoạt động, tính năng từng model."
    rag_overview = get_rag_context(rag_query)
    
    # === BƯỚC 2: Build candidate list từ VEHICLES_DB (FALLBACK), cập nhật giá từ PDF ===
    models_with_specs = {}
    for model_name in VEHICLES_DB.keys():
        specs = VEHICLES_DB[model_name].copy()
        
        # Cố gắng lấy giá từ PDF
        rag_context = get_rag_model_context(model_name)
        if rag_context:
            rag_price = extract_price_from_text(rag_context, model_name)
            if rag_price:
                specs["price"] = rag_price
                specs["_from_pdf"] = True
                print(f"📖 {model_name}: giá cập nhật từ PDF → {rag_price/1_000_000:.0f}M")
        
        if specs["price"] <= budget:
            models_with_specs[model_name] = specs
    
    if not models_with_specs:
        # No models under budget
        cheapest_name, cheapest_specs = min(VEHICLES_DB.items(), key=lambda x: x[1]["price"])
        cheapest_price = cheapest_specs["price"]
        rag_ctx = get_rag_model_context(cheapest_name)
        rag_price = extract_price_from_text(rag_ctx, cheapest_name)
        if rag_price:
            cheapest_price = rag_price
        
        return f"❌ Không có model nào dưới {budget/1_000_000:.0f} triệu đồng.\n\n" \
               f"➡️ Mẫu rẻ nhất: **{cheapest_name}** - {cheapest_price/1_000_000:.0f} triệu đồng\n" \
               f"   (Tầm hoạt động {cheapest_specs['range_km']}km, bảo hành {cheapest_specs['warranty_years']} năm)\n\n" \
               f"💡 Bạn có thể tăng ngân sách hoặc xem xét mẫu này không?"
    
    # Step: Sort by priority
    if priority == "price":
        sorted_models = sorted(models_with_specs.items(), key=lambda x: x[1]["price"])
    elif priority == "range":
        sorted_models = sorted(models_with_specs.items(), key=lambda x: x[1]["range_km"], reverse=True)
    else:  # balanced
        sorted_models = sorted(models_with_specs.items(), key=lambda x: (x[1]["range_km"], -x[1]["price"]), reverse=True)
    
    # Format output for Top 2
    result = "✅ **GỢI Ý TOP 2 MODEL PHÙ HỢP**\n\n"
    
    # Nếu RAG có thông tin tổng quan → đưa vào đầu kết quả
    if rag_overview and rag_overview.strip():
        result += f"📖 *(Dữ liệu từ tài liệu PDF chính thức)*\n\n"
    
    for i, (name, specs) in enumerate(sorted_models[:2], 1):
        is_electric = specs.get("battery_kwh") is not None
        data_source = " (📖 PDF)" if specs.get("_from_pdf") else " (💾 database)"
        
        result += f"{i}. **{name}**{data_source}\n"
        result += f"   💰 Giá: {specs['price']/1_000_000:.0f} triệu đồng\n"
        
        if is_electric:
            result += f"   🔋 Pin: {specs['range_km']}km ({specs['battery_kwh']}kWh)\n"
            result += f"   ⚡ Sạc: ~{specs['charging_time_hours']}h (80%)\n"
            annual_elec = (km_per_day * 365 / 100) * specs["electricity_cost_per_100km"]
            result += f"   💡 Chi phí điện: ~{annual_elec:,.0f}đ/năm ({km_per_day:.0f}km/ngày)\n"
        else:
            fuel_consumption = specs.get("fuel_consumption_per_100km", 6.0)
            fuel_cost = specs.get("fuel_cost_per_liter", 25_000)
            annual_fuel = (km_per_day * 365 / 100) * fuel_consumption * fuel_cost
            result += f"   ⛽ Loại: Xe xăng (tầm hoạt động ~{specs['range_km']}km)\n"
            result += f"   📊 Tiêu hao: ~{fuel_consumption}L/100km\n"
            result += f"   💸 Chi phí xăng: ~{annual_fuel:,.0f}đ/năm ({km_per_day:.0f}km/ngày)\n"
        
        result += f"   🛡️ Bảo hành: {specs['warranty_years']} năm\n"
        reason = "💰 Rẻ nhất" if priority == "price" else "🔋 Pin xa nhất" if priority == "range" else "⚖️ Cân bằng"
        result += f"   ➡️ Lý do: {reason}\n\n"
    
    result += f"💡 Bạn muốn: [Xem chi tiết] / [So sánh 2 xe] / [Tính tổng chi phí]?"
    return result


@tool
def compare_models(model_names: str) -> str:
    """
    🔴 BẮT BUỘC GỌITOOL KHI: User hỏi "so sánh VF e34 và VF8", "khác gì nhau?", "nên chọn model nào?"
    
    CHỨC NĂNG: So sánh CHI TIẾT 2-3 model VinFast (Specs, Giá, Pin, Tính năng, Bảo hành).
    
    📚 DỮ LIỆU: Lấy từ PDF (VINFAST VF1.pdf) + database
    """
    model_list_raw = [m.strip() for m in model_names.split(",")]
    
    # Chuẩn hóa tên xe — case-insensitive
    model_list = []
    unreachable = []
    for raw in model_list_raw:
        resolved = normalize_model_name(raw)
        if resolved:
            model_list.append(resolved)
        else:
            unreachable.append(raw)
    
    if unreachable:
        available = ", ".join(VEHICLES_DB.keys())
        return f"❌ Model {unreachable} không tìm thấy.\n\n✅ Có sẵn: {available}"
    
    # === BƯỚC 1: Lấy thông tin từ PDF (PRIMARY) ===
    print(f"🔍 [compare_models] Querying PDF for {model_list}...")
    specs_from_pdf = {}
    for model_name in model_list:
        rag_context = get_rag_model_context(model_name)
        if rag_context:
            specs_from_pdf[model_name] = rag_context
            print(f"📖 PDF context found for {model_name}")
    
    # === BƯỚC 2: Build comparison từ VEHICLES_DB, override giá từ PDF nếu có ===
    effective_specs = {}
    for model_name in model_list:
        specs = VEHICLES_DB[model_name].copy()
        if model_name in specs_from_pdf:
            rag_price = extract_price_from_text(specs_from_pdf[model_name], model_name)
            if rag_price:
                specs["price"] = rag_price
                specs["_from_pdf"] = True
        effective_specs[model_name] = specs
    
    # Build comparison table
    has_pdf = any(s.get("_from_pdf") for s in effective_specs.values())
    pdf_note = " *(📖 giá từ PDF)*" if has_pdf else " *(💾 database)*"
    result = f"📊 **SO SÁNH CHI TIẾT**{pdf_note}\n\n"
    result += "| Thông số | " + " | ".join(model_list) + " |\n"
    result += "|----------|" + "|".join(["---------"] * len(model_list)) + "|\n"
    
    specs_to_compare = ["price", "battery_kwh", "range_km", "charging_time_hours", "warranty_years"]
    labels = {"price": "Giá (triệu)", "battery_kwh": "Pin (kWh)", "range_km": "Range (km)",
              "charging_time_hours": "Sạc (h)", "warranty_years": "BH (năm)"}
    
    for spec in specs_to_compare:
        row = f"| {labels[spec]} |"
        for model in model_list:
            val = effective_specs[model][spec]
            if spec == "price":
                src = "📖" if effective_specs[model].get("_from_pdf") else "💾"
                row += f" {val/1_000_000:.0f}M {src} |"
            elif val is None:
                row += f" N/A |"
            else:
                row += f" {val} |"
        result += row + "\n"
    
    # Smart features
    result += "| Tính năng |"
    for model in model_list:
        num_features = len(VEHICLES_DB[model].get("smart_features", []))
        result += f" {num_features} |"
    result += "\n"
    
    # Insight
    if len(model_list) >= 2:
        m1, m2 = model_list[0], model_list[1]
        p1, r1 = effective_specs[m1]["price"], effective_specs[m1]["range_km"]
        p2, r2 = effective_specs[m2]["price"], effective_specs[m2]["range_km"]
        
        if p2 > p1:
            result += f"\n💡 **Nhận xét:** {m2} đắt hơn {(p2-p1)/1_000_000:.0f}M nhưng pin +{r2-r1}km. "
            result += f"Chọn {m1} nếu lái thành phố, chọn {m2} nếu đi xa."
        else:
            result += f"\n💡 **Nhận xét:** {m1} rẻ hơn {(p1-p2)/1_000_000:.0f}M và pin cũng vượt trội."
    
    # Nếu có PDF context → thêm trích dẫn
    if specs_from_pdf:
        result += "\n\n---\n📖 **Trích từ PDF:**\n"
        for model_name, ctx in specs_from_pdf.items():
            result += f"\n**{model_name}:** {ctx[:300]}...\n"
    
    return result


@tool
def get_vehicle_info(model_name: str) -> str:
    """
    🔴 BẮT BUỘC GỌITOOL KHI: User nhắc tên xe cụ thể (VD: "tư vấn VF3", "VF e34 có gì đặc biệt?", "xem mẫu VF9")
    
    CHỨC NĂNG: Lấy THÔNG TIN CƠ BẢN về một model xe cụ thể từ PDF + database (không cần budget).
    
    📚 DỮ LIỆU: 
    - PRIMARY: PDF (VINFAST VF1.pdf) được query qua RAG
    - FALLBACK: hard-coded database nếu RAG fail
    
    Tham số:
    - model_name: tên xe (VD: 'VF3', 'VF e34', 'VF8', 'VF9', 'Lux A2.0')
    
    OUTPUT: Thông tin cơ bản:
    - Giá, pin (nếu xe điện) hoặc tiêu hao (nếu xe xăng)
    - Tầm hoạt động, bảo hành
    - 2-3 tính năng chính
    
    ⚠️ NGẮN - dùng TRƯỚC khi user quyết định so sánh hay tính chi phí chi tiết
    
    Nếu model không tồn tại → báo lỗi rõ ràng
    """
    # === Chuẩn hóa tên xe (case-insensitive) ===
    resolved = normalize_model_name(model_name)
    if resolved:
        model_name = resolved

    # === Thử tìm trong DB trước ===
    if model_name not in VEHICLES_DB:
        # Fallback: query PDF trực tiếp
        rag_ctx = get_rag_context(f"{model_name} VinFast thông tin giá pin tính năng bảo hành")
        if rag_ctx and rag_ctx.strip():
            return (
                f"📖 **Thông tin về {model_name} (từ PDF VinFast):**\n\n{rag_ctx.strip()}\n\n"
                f"💡 **Bước tiếp:** [So sánh xe khác] / [Tính chi phí sở hữu] / [Liên hệ showroom]"
            )
        available = ", ".join(VEHICLES_DB.keys())
        return (
            f"❌ Model '{model_name}' không tìm thấy trong hệ thống.\n"
            f"✅ Các model có sẵn: **{available}**\n\n"
            f"💡 Hãy gõ đúng tên model, ví dụ: 'VF3', 'VF8', 'VF e34'"
        )

    specs = VEHICLES_DB[model_name]
    
    # Try to get enriched data from PDF
    rag_context = get_rag_model_context(model_name)
    data_source = " (📖 từ PDF)" if rag_context else ""
    
    # Extract PDF price if available
    rag_price = None
    if rag_context:
        rag_price = extract_price_from_text(rag_context, model_name)
    
    display_price = rag_price if rag_price else specs["price"]
    
    # Build response
    result = f"📋 **THÔNG TIN CHI TIẾT {model_name}**{data_source}\n\n"
    result += f"💰 **Giá:** {display_price/1_000_000:.0f} triệu đồng\n"
    
    is_electric = specs.get("battery_kwh") is not None
    
    if is_electric:
        # Electric vehicle
        result += f"🔋 **Pin & Sạc:**\n"
        result += f"   - Dung lượng: {specs['battery_kwh']}kWh\n"
        result += f"   - Tầm hoạt động: {specs['range_km']}km\n"
        result += f"   - Thời gian sạc: ~{specs['charging_time_hours']}h (80% tại sạc nhanh)\n"
        result += f"   - Chi phí điện: ~{specs['electricity_cost_per_100km']:,}đ/100km\n"
    else:
        # Gasoline vehicle
        fuel_consumption = specs.get("fuel_consumption_per_100km", 6.0)
        result += f"⛽ **Động cơ & Tiêu hao:**\n"
        result += f"   - Loại: Xe xăng\n"
        result += f"   - Tầm hoạt động: {specs['range_km']}km\n"
        result += f"   - Tiêu hao: {fuel_consumption}L/100km\n"
        result += f"   - Chi phí xăng: ~{specs['fuel_cost_per_liter']:,}đ/lít\n"
    
    result += f"\n🛡️ **Bảo hành:** {specs['warranty_years']} năm\n"
    
    # Key features
    features = specs.get("smart_features", [])
    if features:
        result += f"⭐ **Tính năng nổi bật:**\n"
        for feat in features[:3]:  # Top 3 features
            result += f"   - {feat}\n"
    
    result += f"\n💡 **Bước tiếp:** [So sánh xe khác] / [Tính chi phí sở hữu] / [Liên hệ showroom]"
    
    return result


@tool
def calculate_total_cost(model_name: str, km_per_day: float = 50, ownership_years: int = 5) -> str:
    """
    🔴 BẮT BUỘC GỌITOOL KHI: User hỏi "tổng chi phí bao nhiêu?", "nuôi xe bao tiền?"
    
    CHỨC NĂNG: Tính TỔNG CHI PHÍ SỬ DỤNG XE (TCO) trong n năm.
    """
    # === BƯỚC 1: Chuẩn hóa tên xe (case-insensitive) ===
    resolved = normalize_model_name(model_name)
    if resolved:
        model_name = resolved
    
    # === BƯỚC 2: Thử tìm trong DB trước ===
    if model_name not in VEHICLES_DB:
        # === BƯỚC 3: Thử query PDF xem có không ===
        rag_ctx = get_rag_context(f"{model_name} VinFast thông tin giá tính năng")
        if rag_ctx and rag_ctx.strip():
            return (
                f"📖 **Thông tin về {model_name} (từ PDF VinFast):**\n\n{rag_ctx.strip()}\n\n"
                f"⚠️ Lưu ý: Model này chưa có trong database của chúng tôi, "
                f"thông tin trên được lấy trực tiếp từ tài liệu PDF."
            )
        # Không tìm thấy ở đâu
        available = ", ".join(VEHICLES_DB.keys())
        return (
            f"❌ Model '{model_name}' không tìm thấy trong hệ thống.\n"
            f"✅ Các model có sẵn: **{available}**\n\n"
            f"💡 Hãy gõ đúng tên model, ví dụ: 'VF3', 'VF8', 'VF e34'"
        )
    
    # Validate inputs
    if km_per_day < 0 or km_per_day > 1000:
        return f"⚠️ Km/ngày không hợp lý ({km_per_day}km)."
    if ownership_years < 1:
        return f"⚠️ Năm sở hữu phải ≥ 1."
    
    specs = VEHICLES_DB[model_name]
    
    # Calculate costs
    purchase_cost = specs["price"]
    maintenance_cost = specs["annual_maintenance_cost"] * ownership_years
    insurance_cost = specs["annual_insurance_cost"] * ownership_years
    annual_km = km_per_day * 365
    
    # Handle electricity vs fuel
    is_electric = specs.get("battery_kwh") is not None
    if is_electric:
        annual_electricity = (annual_km / 100) * specs["electricity_cost_per_100km"]
        electricity_cost = annual_electricity * ownership_years
        fuel_cost = 0
    else:
        fuel_consumption = specs.get("fuel_consumption_per_100km", 6.0)
        fuel_cost_per_liter = specs.get("fuel_cost_per_liter", 25_000)
        annual_fuel = (annual_km / 100) * fuel_consumption * fuel_cost_per_liter
        fuel_cost = annual_fuel * ownership_years
        electricity_cost = 0
    
    total_cost = purchase_cost + maintenance_cost + insurance_cost + electricity_cost + fuel_cost
    monthly_cost = total_cost / (ownership_years * 12)
    
    # Format output
    result = f"💰 **CHI PHÍ SỬ DỤNG {model_name}** ({ownership_years} năm, ~{km_per_day:.0f}km/ngày)\n\n"
    result += "📋 **Chi tiết:**\n"
    result += f"- Mua xe: {purchase_cost:,}đ\n"
    result += f"- Bảo dưỡng: {maintenance_cost:,}đ ({specs['annual_maintenance_cost']:,}đ/năm × {ownership_years})\n"
    result += f"- Bảo hiểm: {insurance_cost:,}đ ({specs['annual_insurance_cost']:,}đ/năm × {ownership_years})\n"
    
    if is_electric:
        result += f"- Điện: {electricity_cost:,.0f}đ ({annual_km*ownership_years:,.0f}km ÷ 100 × {specs['electricity_cost_per_100km']:,}đ/100km)\n"
    else:
        fuel_consumption = specs.get("fuel_consumption_per_100km", 6.0)
        result += f"- Xăng: {fuel_cost:,.0f}đ ({annual_km*ownership_years:,.0f}km ÷ 100 × {fuel_consumption}L × {specs['fuel_cost_per_liter']:,}đ/L)\n"
    
    result += f"\n{'─' * 50}\n"
    result += f"🎯 **TỔNG TCO: {total_cost:,.0f}đ** ({total_cost/1_000_000:.1f}M)\n"
    result += f"📊 **Đơn vị/tháng: {monthly_cost:,.0f}đ**\n"
    result += f"\n💡 Giả định: {km_per_day:.0f}km/ngày, {ownership_years} năm sở hữu"
    
    return result
