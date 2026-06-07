import os

def main():
    files_to_delete = [
        r"d:\[Lab] HUST\nhà máy\inspect_slide_2_styling.py",
        r"d:\[Lab] HUST\nhà máy\slide_2_styling_report.txt",
        r"d:\[Lab] HUST\nhà máy\check_template_background.py",
        r"d:\[Lab] HUST\nhà máy\template_bg_report.txt",
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
