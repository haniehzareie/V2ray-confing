import requests
import base64
import re
import socket
import time

def is_alive_from_iran(vless_link):
    """بررسی زنده بودن کانفیگ vless از داخل ایران با تست اتصال به IP و پورت"""
    try:
        # استخراج IP و پورت از لینک vless
        match = re.search(r'vless://[^@]+@([^:]+):(\d+)', vless_link)
        if not match:
            return False
        
        ip = match.group(1)
        port = int(match.group(2))
        
        # تست اتصال با سوکت (timeout 3 ثانیه)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        # اگر result == 0 یعنی اتصال برقرار شده (پورت باز است)
        return result == 0
        
    except Exception as e:
        print(f"خطا در تست اتصال: {e}")
        return False

def decode_config(encoded_str):
    """تلاش برای دیکد کردن کانفیگ‌های base64"""
    try:
        cleaned = encoded_str.strip()
        decoded = base64.b64decode(cleaned).decode('utf-8')
        return decoded
    except:
        return None

def extract_vless_from_text(text):
    """استخراج لینک‌های vless از متن"""
    vless_pattern = r'vless://[^\s]+'
    return re.findall(vless_pattern, text)

def process_subscription_url(url):
    """پردازش یک سابسکریپشن لینک و برگرداندن vlessهای زنده از داخل ایران"""
    found_vless = []
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        
        content = resp.text
        
        # اگر محتوا base64 است، دیکد کن
        decoded_content = decode_config(content)
        if decoded_content:
            content = decoded_content
        
        # استخراج تمام لینک‌های vless
        vless_links = extract_vless_from_text(content)
        
        print(f"  {len(vless_links)} کانفیگ vless یافت شد، در حال تست اتصال...")
        
        for link in vless_links:
            # بررسی زنده بودن کانفیگ
            if is_alive_from_iran(link):
                found_vless.append(link)
                print(f"    ✓ کانفیگ زنده پیدا شد")
            time.sleep(0.5)  # تاخیر برای جلوگیری از سنگین شدن تست
            
    except Exception as e:
        print(f"خطا در پردازش {url}: {e}")
    
    return found_vless

def main():
    sub_file_path = "Sub.txt"
    
    try:
        with open(sub_file_path, 'r') as f:
            subscription_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("فایل sub.txt پیدا نشد!")
        return
    
    all_vless = []
    
    for sub_url in subscription_urls:
        print(f"در حال بررسی: {sub_url}")
        vless_list = process_subscription_url(sub_url)
        if vless_list:
            print(f"  -> {len(vless_list)} کانفیگ vless زنده پیدا شد")
            all_vless.extend(vless_list)
        else:
            print("  -> هیچ کانفیگ زنده‌ای یافت نشد")
    
    # ذخیره نتایج در فایل Live_vless.txt
    output_file = "Live_vless.txt"
    with open(output_file, 'w') as f:
        for vless in all_vless:
            f.write(vless + '\n')
    
    print(f"\nعملیات کامل شد. {len(all_vless)} کانفیگ زنده در {output_file} ذخیره شد.")

if __name__ == "__main__":
    main()
