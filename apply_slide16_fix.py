import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Locate Slide 16 boundaries
start_marker = "<!-- 15 SIGNATURE / LIMIT -->"
end_marker = "<!-- 14b RESONANCE -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Error: Could not locate Slide 16 boundaries in the file.")
    sys.exit(1)

slide_content = content[start_idx:end_idx]

# 2. Extract the image tag with bearing_structure data-img
img_match = re.search(r'<img[^>]+data-img="bearing_structure"[^>]+>', slide_content)
if not img_match:
    print("Error: Could not find the <img> tag in Slide 16.")
    sys.exit(1)

original_img_tag = img_match.group(0)

# Extract the base64 src attribute
src_match = re.search(r'src="data:image/png;base64,[^"]+"', original_img_tag)
if not src_match:
    print("Error: Could not find the base64 src attribute.")
    sys.exit(1)

src_attribute = src_match.group(0)

# 3. Create the new updated <img> tag with a larger 52vh max-height
new_img_tag = f'<img class="ill" data-img="bearing_structure" {src_attribute} alt="Cấu tạo ổ lăn" style="max-height: 52vh; width: auto; max-width: 100%; object-fit: contain;">'

# 4. Construct the brand new Slide 16 HTML content with enlarged boxes and text sizes
new_slide_content = f"""<!-- 15 SIGNATURE / LIMIT -->
  <section class="slide">
    <span class="pill">Tutorial 02 · Tần số chữ ký</span>
    <h2>Mỗi lỗi một "tần số chữ ký"</h2>
    <div class="keyidea">Lý thuyết: mỗi lỗi một vạch riêng. Thực tế: FFT <b>thô</b> chỉ thấy "có bất thường", không gọi đích danh — phải dùng <b>Envelope</b>.</div>
    <div class="grid g5 grow" style="align-items: stretch; margin-top: 0.2rem;">
      <!-- Large Image Card on the Left -->
      <div class="imgwrap" style="width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 0.8rem;">
        {new_img_tag}
        <div class="figcap" style="margin-top: 0.6rem; font-size: 0.95rem; color: var(--muted);">Các thành phần cơ khí của ổ lăn nơi phát sinh lỗi</div>
      </div>
      
      <!-- Larger, High-Impact Cards on the Right (perfectly matching in height) -->
      <div class="grid" style="grid-template-columns: 1fr; grid-template-rows: repeat(3, 1fr); gap: 0.6rem; height: 100%;">
        <!-- KPI / Stats Box -->
        <div class="card" style="padding: 0.9rem 1.1rem; background: rgba(21, 33, 51, 0.45); border-left: 5px solid var(--accent); margin: 0; display: flex; flex-direction: column; justify-content: center;">
          <h4 style="margin: 0 0 0.5rem 0; font-size: 1.18rem; color: var(--accent); display: flex; align-items: center; gap: 0.4rem; margin-top: 0;">🎯 Các tần số khuyết tật lý tưởng (CWRU - 1797 RPM)</h4>
          <ul style="list-style: none; margin: 0; padding: 0; font-size: 0.96rem; line-height: 1.5; display: flex; flex-direction: column; gap: 0.5rem;">
            <li><span class="chip c-or" style="font-size: 0.95rem; padding: 0.2rem 0.6rem;">OR</span> Tần số lỗi rãnh ngoài (BPFO) ≈ <b>107.4 Hz</b> + bội số (2x, 3x...)</li>
            <li><span class="chip c-ir" style="font-size: 0.95rem; padding: 0.2rem 0.6rem;">IR</span> Tần số lỗi rãnh trong (BPFI) ≈ <b>162.2 Hz</b> + dải biên (sidebands) ± <i>f<sub>r</sub></i></li>
            <li><span class="chip c-ball" style="font-size: 0.95rem; padding: 0.2rem 0.6rem;">Ball</span> Tần số lỗi viên bi (2•BSF) ≈ <b>141.2 Hz</b> (vết nứt đập vào rãnh trong & ngoài)</li>
          </ul>
        </div>

        <!-- Blind Spot Explanation -->
        <div class="card" style="padding: 0.9rem 1.1rem; background: rgba(239, 68, 68, 0.08); border-left: 5px solid var(--bad); margin: 0; display: flex; flex-direction: column; justify-content: center;">
          <h4 style="margin: 0 0 0.4rem 0; font-size: 1.18rem; color: var(--bad); display: flex; align-items: center; gap: 0.4rem; margin-top: 0;">❌ Vì sao FFT thô "MÙ" với lỗi ổ lăn?</h4>
          <p class="muted" style="font-size: 0.94rem; margin: 0; line-height: 1.45;">Cú va cơ khí của khuyết tật rất ngắn (xung nhọn), gây ra sự kích thích dải tần cực rộng. Trên FFT thô, toàn bộ năng lượng vùng cộng hưởng (vài chục kHz) dâng cao, làm <b>chôn vùi vạch lỗi thực sự ở tần số thấp (~100 Hz)</b> khiến ta không thể đọc hoặc định lượng trực tiếp được.</p>
        </div>

        <!-- Envelope Analysis Solution -->
        <div class="card" style="padding: 0.9rem 1.1rem; background: rgba(52, 211, 153, 0.08); border-left: 5px solid var(--good); margin: 0; display: flex; flex-direction: column; justify-content: center;">
          <h4 style="margin: 0 0 0.4rem 0; font-size: 1.18rem; color: var(--good); display: flex; align-items: center; gap: 0.4rem; margin-top: 0;">✅ Phân tích bao (Envelope Analysis) cứu cánh:</h4>
          <p class="muted" style="font-size: 0.94rem; margin: 0; line-height: 1.45;">Bằng cách lọc băng thông (Bandpass) quanh vùng cộng hưởng rộng, sau đó dùng phép biến đổi Hilbert để <b>"bóc đường bao"</b> (giải điều chế) tín hiệu, toàn bộ tần số khuyết tật (BPFO, BPFI) sẽ hiện rõ sừng sững trên phổ bao, cho phép chẩn đoán chính xác.</p>
        </div>
      </div>
    </div>
    <aside class="notes"><p>Đây là điểm tôi muốn các bạn nhớ lâu nhất, nên tôi nói thật chậm. Trên <em>lý thuyết</em>, OR cho vạch ở 107 Hz, IR ở 162 Hz — hoàn hảo như lý thuyết.</p><p>Trên thực tế, cú va của ổ lăn là một xung rất ngắn, nó kích thích <strong>toàn dải tần</strong>. Nên FFT thô chỉ cho thấy: nền phổ dâng, vùng cộng hưởng kết cấu (vài kHz) sáng lên — đủ để nói "có gì đó sai", nhưng vạch 107/162 Hz bị <em>chôn</em>, không định lượng được. Envelope mới gọi đích danh tần số lỗi. Slide sau tôi chứng minh, bằng vật lý.</p></aside>
  </section>
  
"""

# Replace in content
new_content = content[:start_idx] + new_slide_content + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Slide 16 box and text sizes successfully enlarged for maximum legibility!")
