import os

def main():
    files_to_delete = [
        r"d:\[Lab] HUST\nhà máy\analyze_hust_template.py",
        r"d:\[Lab] HUST\nhà máy\inspect_slides_in_template.py",
        r"d:\[Lab] HUST\nhà máy\hust_template_slides_info.txt",
        r"d:\[Lab] HUST\nhà máy\parse_html_slides.py",
        r"d:\[Lab] HUST\nhà máy\html_slides_structure.txt",
        r"d:\[Lab] HUST\nhà máy\verify_hust_slides.py",
        r"d:\[Lab] HUST\nhà máy\generated_slides_verification.txt"
    ]
    
    for f in files_to_delete:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Deleted: {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

if __name__ == "__main__":
    main()
