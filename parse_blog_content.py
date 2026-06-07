from bs4 import BeautifulSoup
import re

def main():
    file_path = r"C:\Users\Admin\.gemini\antigravity\brain\0026280e-c943-441b-9795-27fb3d6330a6\.system_generated\steps\165\content.md"
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find start of HTML (content.md contains some header lines)
    html_start = content.find("<!DOCTYPE html>")
    if html_start != -1:
        html_content = content[html_start:]
    else:
        html_content = content
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    # We want to extract headings (h1, h2, h3, h4) and paragraphs from the main article
    # Usually in next.js or wordpress, it's inside <article> or elements with articleBody
    article = soup.find("article")
    
    output_path = r"d:\[Lab] HUST\nhà máy\clean_blog_content.txt"
    with open(output_path, "w", encoding="utf-8") as out:
        if article:
            out.write("--- MAIN ARTICLE CONTENT ---\n\n")
            for elem in article.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "table"]):
                if elem.name in ["h1", "h2", "h3", "h4"]:
                    out.write(f"\n\n{'#' * int(elem.name[1])} {elem.get_text(strip=True)}\n\n")
                elif elem.name == "p":
                    out.write(f"{elem.get_text(strip=True)}\n")
                elif elem.name in ["ul", "ol"]:
                    for li in elem.find_all("li"):
                        out.write(f"- {li.get_text(strip=True)}\n")
                elif elem.name == "table":
                    out.write("\n[Table found]\n")
        else:
            # Fallback: search all headers and paragraphs in the body
            out.write("--- BODY CONTENT FALLBACK ---\n\n")
            body = soup.find("body")
            if body:
                for elem in body.find_all(["h1", "h2", "h3", "p"]):
                    if elem.name in ["h1", "h2", "h3"]:
                        out.write(f"\n{'#' * int(elem.name[1])} {elem.get_text(strip=True)}\n")
                    else:
                        txt = elem.get_text(strip=True)
                        if len(txt) > 50:
                            out.write(f"{txt}\n")
                            
    print("Parsing completed.")

if __name__ == "__main__":
    main()
