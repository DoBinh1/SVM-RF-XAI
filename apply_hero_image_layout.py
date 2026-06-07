import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# =========================================================================
# 1. UPGRADE SLIDE 16 (Tần số chữ ký) - WIDER IMAGE, COMPACT CARDS
# =========================================================================
start_s16 = "<!-- 15 SIGNATURE / LIMIT -->"
end_s16 = "<!-- 14b RESONANCE -->"

start_idx_16 = content.find(start_s16)
end_idx_16 = content.find(end_s16)

if start_idx_16 == -1 or end_idx_16 == -1:
    print("Error: Could not locate Slide 16 boundaries.")
    sys.exit(1)

slide_16_content = content[start_idx_16:end_idx_16]

# Extract the base64 src
img_match_16 = re.search(r'<img[^>]+data-img="bearing_structure"[^>]+>', slide_16_content)
if not img_match_16:
    print("Error: Could not find <img> in Slide 16.")
    sys.exit(1)

original_img_tag = img_match_16.group(0)

# Extract the base64 src attribute
src_match_16 = re.search(r'src="data:image/png;base64,[^"]+"', original_img_tag)
if not src_match_16:
    print("Error: Could not find the base64 src attribute.")
    sys.exit(1)

src_attribute = src_match_16.group(0)

# Build Slide 16 with a 1.25fr / 0.75fr split (62.5% Image, 37.5% Text)
# Image height is increased to 50vh, and cards on the right are made compact
updated_s16 = f"""<!-- 15 SIGNATURE / LIMIT -->
  <section class="slide">
    <span class="pill">Tutorial 02 · Tần số chữ ký</span>
    <h2>Mỗi lỗi một "tần số chữ ký"</h2>
    <div class="keyidea">Lý thuyết: mỗi lỗi một vạch riêng. Thực tế: FFT <b>thô</b> chỉ thấy "có bất thường", không gọi đích danh — phải dùng <b>Envelope</b>.</div>
    <div class="grow grid gap-lg" style="grid-template-columns: 1.25fr 0.75fr; align-items: stretch; margin-top: 0.1rem; gap: 1rem;">
      <!-- Hero Image Card on the Left (occupying 62.5% width) -->
      <div class="imgwrap" style="width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 0.6rem;">
        <img class="ill" data-img="bearing_structure" {src_attribute} alt="Cấu tạo ổ lăn" style="max-height: 50vh; width: auto; max-width: 100%; object-fit: contain;">
        <div class="figcap" style="margin-top: 0.4rem; font-size: 0.9rem; color: var(--muted);">Các thành phần cơ khí của ổ lăn nơi phát sinh lỗi</div>
      </div>
      
      <!-- Compact 3-Row Text Cards on the Right (occupying 37.5% width) -->
      <div class="grid" style="grid-template-columns: 1fr; grid-template-rows: repeat(3, 1fr); gap: 0.4rem; height: 100%;">
        <!-- KPI Card -->
        <div class="card" style="padding: 0.5rem 0.75rem; background: rgba(21, 33, 51, 0.45); border-left: 4px solid var(--accent); margin: 0; display: flex; flex-direction: column; justify-content: center;">
          <h4 style="margin: 0 0 0.3rem 0; font-size: 0.95rem; color: var(--accent); display: flex; align-items: center; gap: 0.3rem; margin-top: 0;">🎯 Các tần số khuyết tật lý tưởng (CWRU - 1797 RPM)</h4>
          <ul style="list-style: none; margin: 0; padding: 0; font-size: 0.8rem; line-height: 1.4; display: flex; flex-direction: column; gap: 0.25rem;">
            <li><span class="chip c-or" style="font-size: 0.8rem; padding: 0.1rem 0.4rem;">OR</span> Tần số lỗi rãnh ngoài (BPFO) ≈ <b>107.4 Hz</b> + bội số (2x, 3x...)</li>
            <li><span class="chip c-ir" style="font-size: 0.8rem; padding: 0.1rem 0.4rem;">IR</span> Tần số lỗi rãnh trong (BPFI) ≈ <b>162.2 Hz</b> + dải biên (sidebands) ± <i>f<sub>r</sub></i></li>
            <li><span class="chip c-ball" style="font-size: 0.8rem; padding: 0.1rem 0.4rem;">Ball</span> Tần số lỗi viên bi (2•BSF) ≈ <b>141.2 Hz</b> (vết nứt đập vào rãnh trong & ngoài)</li>
          </ul>
        </div>

        <!-- Blind Spot Card -->
        <div class="card" style="padding: 0.5rem 0.75rem; background: rgba(239, 68, 68, 0.08); border-left: 4px solid var(--bad); margin: 0; display: flex; flex-direction: column; justify-content: center;">
          <h4 style="margin: 0 0 0.2rem 0; font-size: 0.95rem; color: var(--bad); display: flex; align-items: center; gap: 0.3rem; margin-top: 0;">❌ Vì sao FFT thô "MÙ" với lỗi ổ lăn?</h4>
          <p class="muted" style="font-size: 0.8rem; margin: 0; line-height: 1.35;">Cú va cơ khí của khuyết tật rất ngắn (xung nhọn), gây ra sự kích thích dải tần cực rộng. Trên FFT thô, toàn bộ năng lượng vùng cộng hưởng (vài chục kHz) dâng cao, làm <b>chôn vùi vạch lỗi thực sự ở tần số thấp (~100 Hz)</b> khiến ta không thể đọc hoặc định lượng trực tiếp được.</p>
        </div>

        <!-- Envelope Solution Card -->
        <div class="card" style="padding: 0.5rem 0.75rem; background: rgba(52, 211, 153, 0.08); border-left: 4px solid var(--good); margin: 0; display: flex; flex-direction: column; justify-content: center;">
          <h4 style="margin: 0 0 0.2rem 0; font-size: 0.95rem; color: var(--good); display: flex; align-items: center; gap: 0.3rem; margin-top: 0;">✅ Phân tích bao (Envelope Analysis) cứu cánh:</h4>
          <p class="muted" style="font-size: 0.8rem; margin: 0; line-height: 1.35;">Bằng cách lọc băng thông (Bandpass) quanh vùng cộng hưởng rộng, sau đó dùng phép biến đổi Hilbert để <b>"bóc đường bao"</b> (giải điều chế) tín hiệu, toàn bộ tần số khuyết tật (BPFO, BPFI) sẽ hiện rõ sừng sững trên phổ bao, cho phép chẩn đoán chính xác.</p>
        </div>
      </div>
    </div>
    <aside class="notes"><p>Đây là điểm tôi muốn các bạn nhớ lâu nhất, nên tôi nói thật chậm. Trên <em>lý thuyết</em>, OR cho vạch ở 107 Hz, IR ở 162 Hz — hoàn hảo như lý thuyết.</p><p>Trên thực tế, cú va của ổ lăn là một xung rất ngắn, nó kích thích <strong>toàn dải tần</strong>. Nên FFT thô chỉ cho thấy: nền phổ dâng, vùng cộng hưởng kết cấu (vài kHz) sáng lên — đủ để nói "có gì đó sai", nhưng vạch 107/162 Hz bị <em>chôn</em>, không định lượng được. Envelope mới gọi đích danh tần số lỗi. Slide sau tôi chứng minh, bằng vật lý.</p></aside>
  </section>
  
"""

content = content[:start_idx_16] + updated_s16 + content[end_idx_16:]


# =========================================================================
# 2. UPGRADE SLIDE 12 (Waveform 4 trạng thái) - WIDER IMAGE, COMPACT CARDS
# =========================================================================
start_s12 = "<!-- 11 WAVEFORM -->"
end_s12 = "<!-- 12 STATS -->"

start_idx_12 = content.find(start_s12)
end_idx_12 = content.find(end_s12)

if start_idx_12 != -1 and end_idx_12 != -1:
    slide_12_content = content[start_idx_12:end_idx_12]
    
    # Extract the base64 src
    img_match_12 = re.search(r'<img[^>]+data-img="fig_wave"[^>]+>', slide_12_content)
    if img_match_12:
        src_match_12 = re.search(r'src="data:image/png;base64,[^"]+"', img_match_12.group(0))
        if src_match_12:
            src_attr_12 = src_match_12.group(0)
            
            # Build Slide 12 with a 1.25fr / 0.75fr split (62.5% Image, 37.5% Text)
            # Image height is increased to 50vh, and cards on the right are made compact
            updated_s12 = f"""<!-- 11 WAVEFORM -->
  <section class="slide">
    <span class="pill">Tutorial 01 · Waveform</span>
    <h2>"Chữ ký rung" 4 trạng thái</h2>
    <div class="keyidea">Chỉ cần <b>nhìn dạng sóng</b>: Normal phẳng lặng; OR xung đều; IR xung lên–xuống theo vòng quay; Ball thưa, khó thấy.</div>
    <div class="grow grid gap-lg" style="grid-template-columns: 1.25fr 0.75fr; align-items: stretch; margin-top: 0.1rem; gap: 1rem;">
      <!-- Hero Image Card on the Left (occupying 62.5% width) -->
      <div class="imgwrap" style="width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 0.6rem;">
        <img class="ill" data-img="fig_wave" {src_attr_12} alt="Waveform 4 trạng thái (thực tế CWRU)" style="max-height: 50vh; width: auto; max-width: 100%; object-fit: contain;">
        <div class="figcap" style="margin-top: 0.4rem; font-size: 0.85rem; color: var(--muted);">Dữ liệu dao động thực tế từ CWRU — Trích đoạn 60 mili giây (0 HP, lỗi 7 mils)</div>
      </div>
      
      <!-- Compact 4-Row Text Cards on the Right (occupying 37.5% width) -->
      <div class="grid" style="grid-template-columns: 1fr; grid-template-rows: repeat(4, 1fr); gap: 0.35rem; height: 100%;">
        <!-- Normal -->
        <div class="card" style="border-left: 4px solid var(--good); background: rgba(21, 33, 51, 0.45); padding: 0.4rem 0.7rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.1rem 0; font-size: 0.95rem; color: var(--good); display: flex; align-items: center; gap: 0.3rem; margin-top: 0;"><span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--good);"></span> Normal</h4>
          <p class="small" style="font-size: 0.76rem; line-height: 1.3; margin: 0; color: var(--muted);">Biên độ dao động cực nhỏ (&lt; 0.2g), sóng phẳng đều và êm dịu, không chứa xung va đập lạ.</p>
        </div>
        
        <!-- OR -->
        <div class="card" style="border-left: 4px solid #00c0ff; background: rgba(21, 33, 51, 0.45); padding: 0.4rem 0.7rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.1rem 0; font-size: 0.95rem; color: #00c0ff; display: flex; align-items: center; gap: 0.3rem; margin-top: 0;"><span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #00c0ff;"></span> Outer Race (OR)</h4>
          <p class="small" style="font-size: 0.76rem; line-height: 1.3; margin: 0; color: var(--muted);">Xuất hiện chuỗi xung nhọn biên độ lớn, lặp lại rất <b>tuần hoàn và đều đặn</b> (do lỗi nằm cố định).</p>
        </div>
        
        <!-- IR -->
        <div class="card" style="border-left: 4px solid var(--accent); background: rgba(21, 33, 51, 0.45); padding: 0.4rem 0.7rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.15rem 0; font-size: 0.95rem; color: var(--accent); display: flex; align-items: center; gap: 0.3rem; margin-top: 0;"><span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--accent);"></span> Inner Race (IR)</h4>
          <p class="small" style="font-size: 0.76rem; line-height: 1.3; margin: 0; color: var(--muted);">Các xung nhọn dao động bị <b>mô điều biên rõ rệt</b> (phình to thu nhỏ theo nhịp quay của trục).</p>
        </div>
        
        <!-- Ball -->
        <div class="card" style="border-left: 4px solid var(--warn); background: rgba(21, 33, 51, 0.45); padding: 0.4rem 0.7rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.1rem 0; font-size: 0.95rem; color: var(--warn); display: flex; align-items: center; gap: 0.3rem; margin-top: 0;"><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--warn);"></span> Ball (Lỗi bi)</h4>
          <p class="small" style="font-size: 0.76rem; line-height: 1.3; margin: 0; color: var(--muted);">Xung va đập biên độ nhỏ, lưa thưa và phân bố lộn xộn khó định hình (tín hiệu ồn và khó chẩn đoán nhất).</p>
        </div>
      </div>
    </div>
    <aside class="notes"><p>Đây là slide tôi thích nhất, vì nó chứng minh các bạn <strong>chưa cần thuật toán</strong> cũng đọc được bệnh. Normal: biên độ nhỏ, đều — thiết bị hoạt động ổn định và êm ái. OR: những cú va đập biên độ lớn và <em>tuần hoàn rất đều đặn</em>, vì vết lỗi đứng yên một chỗ.</p><p>IR: vẫn là xung, nhưng <em>to nhỏ theo nhịp</em> — nhớ slide nãy chứ, vết lỗi quay vào vùng tải rồi lại ra. Ball: lưa thưa, lộn xộn — ca khó nhất, tôi sẽ nhắc lại suốt khóa. Cái mắt thấy được ở đây chính là cái ta sắp dạy máy <em>đo</em> lại bằng con số.</p></aside>
  </section>
  
"""
            content = content[:start_idx_12] + updated_s12 + content[end_idx_12:]
            print("Slide 12 layout successfully updated to hero image layout!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Both Slide 12 and Slide 16 successfully updated to elegant Hero Image Layout (62.5% / 37.5%)!")
