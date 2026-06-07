from bs4 import BeautifulSoup

def main():
    html_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU_v2.html"
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    sections = soup.find_all("section", class_="slide")
    
    target_indices = [13, 21, 25, 29, 34, 41] # 0-based indices of Slide 14, 22, 26, 30, 35, 42
    
    output_path = r"d:\[Lab] HUST\nhà máy\section_slides_html.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for idx in target_indices:
            if idx < len(sections):
                sec = sections[idx]
                f.write(f"\n================ Slide {idx+1} ================\n")
                f.write(str(sec))
                f.write("\n")

if __name__ == "__main__":
    main()
