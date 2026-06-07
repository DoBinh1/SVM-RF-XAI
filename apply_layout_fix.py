import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Locate Slide 12 boundaries
start_marker = "<!-- 11 WAVEFORM -->"
end_marker = "<!-- 12 STATS -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Error: Could not locate Slide 12 boundaries in the file.")
    sys.exit(1)

slide_content = content[start_idx:end_idx]

# 2. Extract the massive img tag from Slide 12
img_match = re.search(r'<img[^>]+data-img="fig_wave"[^>]+>', slide_content)
if not img_match:
    print("Error: Could not find the <img> tag in Slide 12.")
    sys.exit(1)

original_img_tag = img_match.group(0)

# Extract the base64 src attribute from the original image tag
src_match = re.search(r'src="data:image/png;base64,[^"]+"', original_img_tag)
if not src_match:
    print("Error: Could not find the base64 src attribute.")
    sys.exit(1)

src_attribute = src_match.group(0)

# 3. Create the new updated <img> tag with a larger max-height for our new side-by-side layout
new_img_tag = f'<img class="ill" data-img="fig_wave" {src_attribute} alt="Waveform 4 trạng thái (thực tế CWRU)" style="max-height: 48vh; width: auto; max-width: 100%; object-fit: contain;">'

# 4. Construct the brand new Slide 12 HTML content
new_slide_content = f"""<!-- 11 WAVEFORM -->
  <section class="slide">
    <span class="pill">Tutorial 01 · Waveform</span>
    <h2>"Chữ ký rung" 4 trạng thái</h2>
    <div class="keyidea">Chỉ cần <b>nhìn dạng sóng</b>: Normal phẳng lặng; OR xung đều; IR xung lên–xuống theo vòng quay; Ball thưa, khó thấy.</div>
    <div class="grow grid g2 gap-lg" style="align-items: stretch; margin-top: 0.2rem;">
      <!-- Waveform Plot on the Left -->
      <div class="imgwrap" style="width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 0.6rem;">
        {new_img_tag}
        <div class="figcap" style="margin-top: 0.4rem; font-size: 0.85rem; color: var(--muted);">Dữ liệu dao động thực tế từ CWRU — Trích đoạn 60 mili giây (0 HP, lỗi 7 mils)</div>
      </div>
      
      <!-- 4 State Cards on the Right (perfectly matching the vertical subplots) -->
      <div class="grid" style="grid-template-columns: 1fr; grid-template-rows: repeat(4, 1fr); gap: 0.5rem; height: 100%;">
        <!-- Normal -->
        <div class="card" style="border-left: 4px solid var(--good); background: rgba(21, 33, 51, 0.45); padding: 0.5rem 0.8rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.15rem 0; font-size: 0.95rem; color: var(--good); display: flex; align-items: center; gap: 0.4rem; margin-top: 0;"><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--good);"></span> Normal</h4>
          <p class="small" style="font-size: 0.8rem; line-height: 1.35; margin: 0; color: var(--muted);">Biên độ dao động cực nhỏ (&lt; 0.2g), sóng phẳng đều và êm dịu, không chứa xung va đập lạ.</p>
        </div>
        
        <!-- OR -->
        <div class="card" style="border-left: 4px solid #00c0ff; background: rgba(21, 33, 51, 0.45); padding: 0.5rem 0.8rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.15rem 0; font-size: 0.95rem; color: #00c0ff; display: flex; align-items: center; gap: 0.4rem; margin-top: 0;"><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00c0ff;"></span> Outer Race (OR)</h4>
          <p class="small" style="font-size: 0.8rem; line-height: 1.35; margin: 0; color: var(--muted);">Xuất hiện chuỗi xung nhọn biên độ lớn, lặp lại rất <b>tuần hoàn và đều đặn</b> (do lỗi nằm cố định).</p>
        </div>
        
        <!-- IR -->
        <div class="card" style="border-left: 4px solid var(--accent); background: rgba(21, 33, 51, 0.45); padding: 0.5rem 0.8rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.15rem 0; font-size: 0.95rem; color: var(--accent); display: flex; align-items: center; gap: 0.4rem; margin-top: 0;"><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--accent);"></span> Inner Race (IR)</h4>
          <p class="small" style="font-size: 0.8rem; line-height: 1.35; margin: 0; color: var(--muted);">Các xung nhọn dao động bị <b>mô điều biên rõ rệt</b> (phình to thu nhỏ theo nhịp quay của trục).</p>
        </div>
        
        <!-- Ball -->
        <div class="card" style="border-left: 4px solid var(--warn); background: rgba(21, 33, 51, 0.45); padding: 0.5rem 0.8rem; text-align: left; display: flex; flex-direction: column; justify-content: center; margin: 0;">
          <h4 style="margin: 0 0 0.15rem 0; font-size: 0.95rem; color: var(--warn); display: flex; align-items: center; gap: 0.4rem; margin-top: 0;"><span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--warn);"></span> Ball (Lỗi bi)</h4>
          <p class="small" style="font-size: 0.8rem; line-height: 1.35; margin: 0; color: var(--muted);">Xung va đập biên độ nhỏ, lưa thưa và phân bố lộn xộn khó định hình (tín hiệu ồn và khó chẩn đoán nhất).</p>
        </div>
      </div>
    </div>
    <aside class="notes"><p>Đây là slide tôi thích nhất, vì nó chứng minh các bạn <strong>chưa cần thuật toán</strong> cũng đọc được bệnh. Normal: biên độ nhỏ, đều — thiết bị hoạt động ổn định và êm ái. OR: những cú va đập biên độ lớn và <em>tuần hoàn rất đều đặn</em>, vì vết lỗi đứng yên một chỗ.</p><p>IR: vẫn là xung, nhưng <em>to nhỏ theo nhịp</em> — nhớ slide nãy chứ, vết lỗi quay vào vùng tải rồi lại ra. Ball: lưa thưa, lộn xộn — ca khó nhất, tôi sẽ nhắc lại suốt khóa. Cái mắt thấy được ở đây chính là cái ta sắp dạy máy <em>đo</em> lại bằng con số.</p></aside>
  </section>
  
"""

# Replace in content
new_content = content[:start_idx] + new_slide_content + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Slide 12 layout successfully updated to elegant side-by-side split grid!")
