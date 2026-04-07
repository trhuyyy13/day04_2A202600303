# Test 1 – Direct Answer (Không cần tool)

**User:** "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu."

**Kỳ vọng:** Agent chào hỏi, hỏi thêm về sở thích/ngân sách/thời gian.

Không gọi tool nào.
```text
TravelBuddy:
Chào bạn! Du lịch là một trải nghiệm tuyệt vời và có rất nhiều địa điểm thú vị để khám phá ở Việt Nam. Bạn đã có trong đầu một số địa điểm nào chưa? Hoặc bạn thích kiểu du lịch gì, như biển, núi, văn hóa hay lịch sử? Hãy cho mình biết để mình có thể tư vấn tốt hơn nhé!
```
# Test 2 – Single Tool Call

**User:** "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng"

**Kỳ vọng:** Gọi `search_flights("Hà Nội", "Đà Nẵng")`, liệt kê 4 chuyến bay.
```text
TravelBuddy:
Dưới đây là các chuyến bay từ Hà Nội đến Đà Nẵng cho bạn tham khảo:

1. **VietJet Air**: 08:30 - 09:50 | Giá: 890.000đ (hạng phổ thông)
2. **Bamboo Airways**: 11:00 - 12:20 | Giá: 1.200.000đ (hạng phổ thông)
3. **Vietnam Airlines**: 06:00 - 07:20 | Giá: 1.450.000đ (hạng phổ thông)
4. **Vietnam Airlines**: 14:00 - 15:20 | Giá: 2.800.000đ (hạng thương gia)
```
# Test 3 – Multi-Step Tool Chaining

**User:** "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"

**Kỳ vọng:** Agent phải tự chuỗi nhiều bước:

1. `search_flights("Hà Nội", "Phú Quốc")` → tìm vé rẻ nhất (1.100.000đ)
2. `search_hotels("Phú Quốc", max_price phù hợp)` → gợi ý trong tầm giá
3. `calculate_budget(5000000, "vé_bay:1100000,khách_sạn:...")` → tính còn lại

Rồi tổng hợp thành gợi ý hoàn chỉnh với bảng chi phí.
```text
TravelBuddy đang suy nghĩ...
 -> Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
 -> Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:1100000'})
 -> Gọi tool: search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 1950000})
 -> Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:1100000,khách_sạn:3000000'})
 -> Trả lời trực tiếp

TravelBuddy:
### Kế hoạch chuyến đi
**Chuyến bay:** VietJet Air | 16:00-18:15 | 1.100.000đ  
**Khách sạn:** Sol by Meliá, phòng tiêu chuẩn, 1.500.000đ/đêm (2 đêm)  
**Ngân sách:** Tổng chi phí 4.100.000đ (còn lại 900.000đ)

**Gợi ý:** Bạn có thể sử dụng số tiền còn lại để thưởng thức ẩm thực địa phương hoặc tham gia các hoạt động vui chơi giải trí tại đảo Phú Quốc! Chúc bạn có một chuyến đi thú vị!
```
# Test 4 – Missing Info / Clarification

**User:** "Tôi muốn đặt khách sạn"

**Kỳ vọng:** Agent hỏi lại: thành phố nào? bao nhiêu đêm? ngân sách bao nhiêu?
```text
TravelBuddy đang suy nghĩ...
 -> Trả lời trực tiếp

TravelBuddy:
Bạn cần tìm khách sạn ở đâu? Và có giới hạn giá tối đa nào cho mỗi đêm không?
```

# Test 5 – Guardrail / Refusal

**User:** "Giải giúp tôi bài tập lập trình Python về linked list"

**Kỳ vọng:** Từ chối lịch sự, nói rằng chỉ hỗ trợ về du lịch.
```text
TravelBuddy đang suy nghĩ...
 -> Trả lời trực tiếp

TravelBuddy:
Xin lỗi, nhưng mình không thể giúp giải bài tập lập trình. Tuy nhiên, nếu bạn cần thông tin về du lịch hoặc có bất kỳ câu hỏi nào liên quan đến chuyến đi, mình rất sẵn lòng hỗ trợ!
```