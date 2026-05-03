import requests
import base64
import re

def is_german_or_finnish_ip(ip_info_url):
    """بررسی می‌کند که IP متعلق به آلمان (DE) یا فنلاند (FI) است یا خیر"""
    try:
        response = requests.get(ip_info_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            country_code = data.get('country_code', '')
            return country_code in ['DE', 'FI']
    except:
        pass
    return False

def decode_config(encoded_str):
    """تلاش برای دیکد کردن کانفیگ‌های base64"""
    try:
        # حذف whitespace و تلاش برای دیکد
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
    """پردازش یک سابسکریپشن لینک و برگرداندن vlessهای معتبر (آلمان/فنلاند)"""
    found_vless = []
    try:
        # دریافت محتوای سابسکریپشن
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
        
        for link in vless_links:
            # استخراج IP از لینک vless (بعد از @ و قبل از : )
            match = re.search(r'vless://[^@]+@([^:]+):', link)
            if match:
                ip = match.group(1)
                # بررسی IP با استفاده از سرویس ip-api.com
                ip_info_url = f"http://ip-api.com/json/{ip}?fields=country_code"
                if is_german_or_finnish_ip(ip_info_url):
                    found_vless.append(link)
    except Exception as e:
        print(f"خطا در پردازش {url}: {e}")
    
    return found_vless

def main():
    # آدرس فایل sub.txt در ریپازیتوری (فرض می‌کنیم در مسیر جاری است)
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
            print(f"  -> {len(vless_list)} کانفیگ vless آلمان/فنلاند پیدا شد")
            all_vless.extend(vless_list)
        else:
            print("  -> موردی یافت نشد")
    
    # ذخیره نتایج در فایل Germany_vless.txt
    output_file = "Germany_vless.txt"
    with open(output_file, 'w') as f:
        for vless in all_vless:
            f.write(vless + '\n')
    
    print(f"\nعملیات کامل شد. {len(all_vless)} کانفیگ در {output_file} ذخیره شد.")

if __name__ == "__main__":
    main()
