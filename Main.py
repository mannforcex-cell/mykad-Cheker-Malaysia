import os
import sys
import re
import json
import requests
from datetime import datetime
import phonenumbers
from phonenumbers import carrier, timezone, geocoder, phonenumberutil
import hashlib
from urllib.parse import quote

class Colors:
    CYAN = '\033[96m'     
    RED = '\033[91m'      
    PURPLE = '\033[95m'    
    GREEN = '\033[92m'    
    BLUE = '\033[94m'      
    ORANGE = '\033[38;5;208m' 
    YELLOW = '\033[93m'    
    PINK = '\033[38;5;205m'   
    GOLD = '\033[38;5;220m'   
    MAGENTA = '\033[38;5;165m' 
    LIME = '\033[38;5;154m'   
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_banner():
    clear_screen()
    
    banner = f"""{Colors.PINK}
           ___---___                    .                   
       .              .--\        --.     .     .         
                    ./.;_.\     __/~ \.     
                   /;  / `-'  __\    . \                            
 .        .       / ,--'     / .   .;   \        |
                 | .|       /       __   |      -O-       .
                |__/    __ |  . ;   \ | . |      |
                |      /  \\_    . ;| \___|    
   .    o       |      \  .~\\___,--'     |           .
                 |     | . ; ~~~~\_    __|
    |             \    \   .  .  ; \  /_/   .
   -O-        .    \   /         . |  ~/                  .
    |    .          ~\ \   .      /  /~          o
  .                   ~--___ ; ___--~

{Colors.GOLD}
                        ╭───────☆───────╮
{Colors.MAGENTA}
                    🛡 PlandoxSing CyberForce 🛡
{Colors.CYAN}
                    Malaysian Intelligence Toolkit
{Colors.ORANGE}
                        Author: MFx OFFICIAL
{Colors.GOLD}
                        ╰───────☆───────╯
{Colors.RESET}"""
    print(banner)


class PhoneIntelligence:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ms-MY,ms;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def validate_malaysian_number(self, phone):
        patterns = [
            r'^\+601\d{8,9}$',
            r'^601\d{8,9}$',
            r'^01\d{8,9}$',
            r'^\+60\s?1\d{8,9}$',
        ]
        for pattern in patterns:
            if re.match(pattern, phone.strip()):
                return True
        return False
    
    def format_malaysian_number(self, phone):
        phone = phone.strip()
        phone = re.sub(r'[\s\-\.]', '', phone)
        
        if phone.startswith('01'):
            phone = '+60' + phone[1:]
        elif phone.startswith('601'):
            phone = '+60' + phone[2:]
        elif phone.startswith('60') and not phone.startswith('+60'):
            phone = '+' + phone
        elif phone.startswith('1') and len(phone) in [9, 10]:
            phone = '+60' + phone
        
        return phone
    
    def get_carrier_info(self, phone):
        try:
            parsed = phonenumbers.parse(phone, "MY")
            
            carrier_name = carrier.name_for_number(parsed, "en")
            if not carrier_name:
                prefix = phone[-9:-7] if len(phone) >= 11 else phone[-8:-6]
                carrier_map = {
                    '10': '📱 DIGI', '11': '📱 DIGI/CELCOM', '12': '📱 MAXIS',
                    '13': '📱 CELCOM', '14': '📱 DIGI', '15': '📱 DIGI',
                    '16': '📱 MAXIS', '17': '📱 MAXIS', '18': '📱 UMOBILE',
                    '19': '📱 CELCOM',
                }
                carrier_name = carrier_map.get(prefix, "❓ UNKNOWN")
            
            location = geocoder.description_for_number(parsed, "en")
            tz_list = timezone.time_zones_for_number(parsed)
            timezone_info = tz_list[0] if tz_list else "🌏 Asia/Kuala_Lumpur"
            
            number_type = phonenumbers.number_type(parsed)
            type_map = {
                0: "📞 FIXED LINE", 1: "📱 MOBILE", 2: "📱📞 MOBILE/FIXED",
                3: "🆓 TOLL FREE", 4: "💰 PREMIUM", 6: "🗣️ VOIP",
                7: "👤 PERSONAL", 8: "📟 PAGER", 10: "📩 VOICEMAIL",
                27: "❓ UNKNOWN"
            }
            line_type = type_map.get(number_type, "❓ UNKNOWN")
            
            return {
                'carrier': carrier_name,
                'line_type': line_type,
                'location': location,
                'timezone': timezone_info,
                'is_valid': phonenumbers.is_valid_number(parsed),
                'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_whatsapp(self, phone):
        try:
            clean_num = phone.replace('+', '').replace(' ', '').replace('-', '')
            url = f"https://wa.me/{clean_num}"
            
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                final_url = response.url
                if 'whatsapp.com' in final_url or 'wa.me' in final_url:
                    return {
                        'has_whatsapp': True,
                        'whatsapp_url': f"https://wa.me/{clean_num}",
                        'message_url': f"https://wa.me/{clean_num}?text=Hello"
                    }
            
            return {'has_whatsapp': False}
        except:
            return {'error': 'Connection failed'}
    
    def check_telegram(self, phone):
        try:
            clean_num = phone.replace('+', '').replace(' ', '').replace('-', '')
            url = f"https://t.me/+{clean_num}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                if 'tgme' in response.text or 'Telegram' in response.text:
                    return {
                        'has_telegram': True,
                        'telegram_url': f"https://t.me/+{clean_num}"
                    }
            
            return {'has_telegram': False}
        except:
            return {'error': 'Connection failed'}
    
    def analyze_number(self, phone):
        print(f"\n{Colors.CYAN}❯❯❯❯ Analyzing Malaysian Number: {phone}{Colors.RESET}")
        
        if not self.validate_malaysian_number(phone):
            print(f"{Colors.RED}╰── ❌ Invalid Malaysian number format{Colors.RESET}")
            return None
        
        formatted = self.format_malaysian_number(phone)
        print(f"{Colors.GREEN}╰── ✅ Formatted: {formatted}{Colors.RESET}")
        
        print(f"\n{Colors.BLUE}❯❯❯❯ Phone Information{Colors.RESET}")
        
        carrier_info = self.get_carrier_info(formatted)
        if 'error' not in carrier_info:
            print(f"  {Colors.GREEN}╰── • Carrier: {carrier_info['carrier']}{Colors.RESET}")
            print(f"  {Colors.GREEN}╰── • Line Type: {carrier_info['line_type']}{Colors.RESET}")
            print(f"  {Colors.GREEN}╰── • Location: {carrier_info['location']}{Colors.RESET}")
            print(f"  {Colors.GREEN}╰── • Timezone: {carrier_info['timezone']}{Colors.RESET}")
            print(f"  {Colors.GREEN}╰── • Valid Number: {'✅ YES' if carrier_info['is_valid'] else '❌ NO'}{Colors.RESET}")
            print(f"  {Colors.GREEN}╰── • National Format: {carrier_info['national']}{Colors.RESET}")
            print(f"  {Colors.GREEN}╰── • International: {carrier_info['international']}{Colors.RESET}")
        else:
            print(f"{Colors.RED}╰── Error: {carrier_info['error']}{Colors.RESET}")
        
        print(f"\n{Colors.PURPLE}❯❯❯❯ Social Media Presence{Colors.RESET}")
        
        whatsapp = self.check_whatsapp(formatted)
        if 'error' not in whatsapp:
            print(f"  {Colors.GREEN}╰── • WhatsApp: {'✅ YES' if whatsapp['has_whatsapp'] else '❌ NO'}{Colors.RESET}")
            if whatsapp['has_whatsapp']:
                print(f"  {Colors.BLUE}    ❯ WhatsApp URL: {whatsapp['whatsapp_url']}{Colors.RESET}")
        else:
            print(f"{Colors.RED}╰── WhatsApp Error{Colors.RESET}")
        
        telegram = self.check_telegram(formatted)
        if 'error' not in telegram:
            print(f"  {Colors.GREEN}╰── • Telegram: {'✅ YES' if telegram['has_telegram'] else '❌ NO'}{Colors.RESET}")
            if telegram['has_telegram']:
                print(f"  {Colors.BLUE}    ❯ Telegram URL: {telegram['telegram_url']}{Colors.RESET}")
        else:
            print(f"{Colors.RED}╰── Telegram Error{Colors.RESET}")
        
        print(f"\n{Colors.ORANGE}❯❯❯❯ Number Analysis{Colors.RESET}")
        
        if formatted.startswith('+60') and len(formatted) > 3:
            national = formatted[3:]
            if national.startswith('1') and len(national) >= 10:
                prefix = national[:3]
                subscriber = national[3:]
                
                print(f"  {Colors.GREEN}╰── • Country Code: +60 🇲🇾{Colors.RESET}")
                print(f"  {Colors.GREEN}╰── • Mobile Prefix: {prefix}{Colors.RESET}")
                print(f"  {Colors.GREEN}╰── • Subscriber Number: {subscriber}{Colors.RESET}")
                
                prefix_info = {
                    '010': '📱 DIGI (1995)', '011': '📱 DIGI/CELCOM (1995)',
                    '012': '📱 MAXIS (1995)', '013': '📱 CELCOM (1995)',
                    '014': '📱 DIGI (2005)', '015': '📱 DIGI (2006)',
                    '016': '📱 MAXIS (2006)', '017': '📱 MAXIS (2007)',
                    '018': '📱 UMOBILE (2008)', '019': '📱 CELCOM (2008)',
                }
                
                if prefix in prefix_info:
                    print(f"  {Colors.BLUE}    ❯ Carrier Info: {prefix_info[prefix]}{Colors.RESET}")
        
        print(f"\n{Colors.PURPLE}❯❯❯❯ Analysis Time: {datetime.now().strftime('%H:%M:%S')}{Colors.RESET}")
        return formatted


class ICIntelligence:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ms-MY,ms;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def parse_ic_detailed(self, ic):
        if len(ic) != 12 or not ic.isdigit():
            return None
            
        yy = ic[0:2]
        mm = ic[2:4]
        dd = ic[4:6]
        state_code = ic[6:8]
        seq = ic[8:11]
        gender_digit = ic[11]
        
        year = int(yy)
        if year <= 30:
            year += 2000
            generation = "🎮 Gen-Z"
        else:
            year += 1900
            if year >= 1995:
                generation = "📱 Millennial"
            elif year >= 1980:
                generation = "💼 Gen-X"
            else:
                generation = "👴 Boomer"
        
        state_map = {
            '01': '🇲🇾 Johor', '02': '🇲🇾 Kedah', '03': '🇲🇾 Kelantan', 
            '04': '🇲🇾 Melaka', '05': '🇲🇾 Negeri Sembilan', '06': '🇲🇾 Pahang',
            '07': '🇲🇾 Pulau Pinang', '08': '🇲🇾 Perak', '09': '🇲🇾 Perlis',
            '10': '🇲🇾 Selangor', '11': '🇲🇾 Terengganu', '12': '🇲🇾 Sabah',
            '13': '🇲🇾 Sarawak', '14': '🇲🇾 Kuala Lumpur', '15': '🇲🇾 Labuan',
            '16': '🇲🇾 Putrajaya',
        }
        
        month_names = {
            '01': '❄️ Januari', '02': '💝 Februari', '03': '🌸 Mac',
            '04': '🌧️ April', '05': '🌺 Mei', '06': '☀️ Jun',
            '07': '🏖️ Julai', '08': '🎋 Ogos', '09': '📚 September',
            '10': '🎃 Oktober', '11': '🍂 November', '12': '🎄 Disember'
        }
        
        zodiac = self.get_zodiac(int(mm), int(dd))
        
        return {
            'birth_date': f"{dd}/{mm}/{year} 📅",
            'birth_day': f"{dd} 📆",
            'birth_month': month_names.get(mm, f"Bulan {mm}"),
            'birth_year': f"{year} 🎂",
            'state_code': state_code,
            'state': state_map.get(state_code, '❓ Unknown'),
            'sequence_number': f"{seq} 🔢",
            'gender': '👨 Male' if int(gender_digit) % 2 == 1 else '👩 Female',
            'age': f"{datetime.now().year - year} 🎯",
            'generation': generation,
            'zodiac': zodiac,
            'ic_number': f"{ic} 🆔"
        }
    
    def get_zodiac(self, month, day):
        zodiacs = [
            ((3, 21), (4, 19), "♈ Aries"),
            ((4, 20), (5, 20), "♉ Taurus"),
            ((5, 21), (6, 20), "♊ Gemini"),
            ((6, 21), (7, 22), "♋ Cancer"),
            ((7, 23), (8, 22), "♌ Leo"),
            ((8, 23), (9, 22), "♍ Virgo"),
            ((9, 23), (10, 22), "♎ Libra"),
            ((10, 23), (11, 21), "♏ Scorpio"),
            ((11, 22), (12, 21), "♐ Sagittarius"),
            ((12, 22), (1, 19), "♑ Capricorn"),
            ((1, 20), (2, 18), "♒ Aquarius"),
            ((2, 19), (3, 20), "♓ Pisces")
        ]
        
        for start, end, name in zodiacs:
            if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
                return name
        
        return "✨ Unknown"
    
    def analyze_ic(self, ic):
        print(f"\n{Colors.CYAN}❯❯❯❯ Analyzing Malaysian IC: {ic}{Colors.RESET}")
        
        basic = self.parse_ic_detailed(ic)
        if not basic:
            print(f"{Colors.RED}╰── ❌ Invalid IC format (must be 12 digits){Colors.RESET}")
            return None
        
        print(f"\n{Colors.BLUE}❯❯❯❯ Basic Information{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • IC Number: {basic['ic_number']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Birth Date: {basic['birth_date']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Birth Day: {basic['birth_day']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Birth Month: {basic['birth_month']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Birth Year: {basic['birth_year']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Age: {basic['age']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Generation: {basic['generation']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • State Code: {basic['state_code']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • State: {basic['state']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Gender: {basic['gender']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Zodiac: {basic['zodiac']}{Colors.RESET}")
        print(f"  {Colors.GREEN}╰── • Sequence: {basic['sequence_number']}{Colors.RESET}")
        
        print(f"\n{Colors.PURPLE}❯❯❯❯ Additional Information{Colors.RESET}")
        
        age = int(basic['age'].split()[0])
        if age < 6:
            education = "🏫 Pra-Sekolah"
        elif age < 13:
            education = "🎒 Sekolah Rendah"
        elif age < 18:
            education = "📚 Sekolah Menengah"
        elif age < 22:
            education = "🎓 Pra-Universiti"
        elif age < 25:
            education = "🏛️ Ijazah Sarjana Muda"
        elif age < 40:
            education = "💼 Kerjaya"
        else:
            education = "🧓 Pengalaman"
        
        print(f"  {Colors.GREEN}╰── • Pendidikan: {education}{Colors.RESET}")
        
        state_clean = basic['state'].replace('🇲🇾 ', '').replace('❓ ', '')
        state_gdp = {
            'Johor': 'RM 120B', 'Kuala Lumpur': 'RM 150B',
            'Selangor': 'RM 141B', 'Penang': 'RM 95B',
            'Sabah': 'RM 65B', 'Sarawak': 'RM 70B',
            'Pahang': 'RM 46B'
        }
        gdp = state_gdp.get(state_clean, 'RM 50B')
        print(f"  {Colors.GREEN}╰── • GDP State: {gdp}{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}❯❯❯❯ Location Maps{Colors.RESET}")
        maps_url = f"https://maps.google.com/?q={quote(state_clean + ', Malaysia')}"
        print(f"  {Colors.BLUE}╰── • Google Maps: {maps_url}{Colors.RESET}")
        
        print(f"\n{Colors.PURPLE}❯❯❯❯ Analysis Time: {datetime.now().strftime('%H:%M:%S')}{Colors.RESET}")
        
        all_data = {
            'basic_info': basic,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return all_data


def print_menu():
    print(f"""
{Colors.GOLD}
             ╭─────────────────────────────╮
{Colors.MAGENTA}
                     PLANDOXSING MAIN MENU 
{Colors.GOLD}
             ╰─────────────────────────────╯
{Colors.RESET}
    {Colors.CYAN}❯❯❯❯ [1] {Colors.YELLOW}📱 Malaysian Phone OSINT
    {Colors.RED}❯❯❯❯ [2] {Colors.YELLOW}🆔 Malaysian IC Intelligence
    {Colors.PURPLE}❯❯❯❯ [3] {Colors.YELLOW}🔍 Bulk Phone Check
    {Colors.GREEN}❯❯❯❯ [4] {Colors.YELLOW}📊 Carrier Lookup
    {Colors.BLUE}❯❯❯❯ [5] {Colors.YELLOW}📁 Phone Format Guide
    {Colors.ORANGE}❯❯❯❯ [0] {Colors.YELLOW}🚪 Exit
{Colors.RESET}
""")

def print_compact_menu():
    print(f"""
{Colors.GOLD}
        ╭── ──╮           ╭── ──╮
{Colors.CYAN}
        ᆞ| [1]            ᆞ| [2]
{Colors.YELLOW}
        ❯ Phone OSINT     ❯ IC Intel
{Colors.GOLD}
        ╰── ──╯           ╰── ──╯

        ╭── ──╮           ╭── ──╮
{Colors.CYAN}
        ᆞ| [3]            ᆞ| [4]
{Colors.YELLOW}
        ❯ Bulk Check      ❯ Carrier
{Colors.GOLD}
        ╰── ──╯           ╰── ──╯

        ╭── ──╮           ╭── ──╮
{Colors.CYAN}
        ᆞ| [5]            ᆞ| [0]
{Colors.YELLOW}
        ❯ Format Guide    ❯ Exit
{Colors.GOLD}
        ╰── ──╯           ╰── ──╯
{Colors.RESET}
""")

def show_format_guide():
    print(f"\n{Colors.CYAN}❯❯❯❯ Malaysian Phone Format Guide{Colors.RESET}")
    print(f"{Colors.GREEN}╰── • Format: +60 1X XXX XXXX{Colors.RESET}")
    print(f"\n{Colors.BLUE}❯❯❯❯ Common Prefixes:{Colors.RESET}")
    print(f"  {Colors.GREEN}╰── • 010, 011, 014, 015 - 📱 DIGI{Colors.RESET}")
    print(f"  {Colors.GREEN}╰── • 012, 013, 016, 017 - 📱 MAXIS{Colors.RESET}")
    print(f"  {Colors.GREEN}╰── • 011, 013, 019 - 📱 CELCOM{Colors.RESET}")
    print(f"  {Colors.GREEN}╰── • 018 - 📱 UMOBILE{Colors.RESET}")
    print(f"\n{Colors.PURPLE}❯❯❯❯ Examples:{Colors.RESET}")
    print(f"  {Colors.BLUE}╰── • +601139183035{Colors.RESET}")
    print(f"  {Colors.BLUE}╰── • 601139183035{Colors.RESET}")
    print(f"  {Colors.BLUE}╰── • 011-3918 3035{Colors.RESET}")
    print(f"  {Colors.BLUE}╰── • 011 3918 3035{Colors.RESET}")

def main():
    print_banner()
    
    phone_tool = PhoneIntelligence()
    ic_tool = ICIntelligence()
    
    while True:
        print(f"\n{Colors.LIME}{'❯'*30}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}🔥 PlandoxSing - Malaysian Intelligence Toolkit 🔥{Colors.RESET}")
        print(f"{Colors.LIME}{'❯'*30}{Colors.RESET}")
        
        print_compact_menu()
        
        choice = input(f"\n{Colors.GREEN}❯❯❯❯ Select option: {Colors.RESET}").strip()
        
        if choice == '1':
            phone = input(f"{Colors.YELLOW}╰── Enter Malaysian phone number: {Colors.RESET}").strip()
            if phone:
                result = phone_tool.analyze_number(phone)
                if result:
                    input(f"\n{Colors.BLUE}❯❯❯❯ Press Enter to continue...{Colors.RESET}")
        
        elif choice == '2':
            ic = input(f"{Colors.YELLOW}╰── Enter Malaysian IC (12 digits): {Colors.RESET}").strip()
            if ic:
                result = ic_tool.analyze_ic(ic)
                if result:
                    input(f"\n{Colors.BLUE}❯❯❯❯ Press Enter to continue...{Colors.RESET}")
        
        elif choice == '3':
            phones = input(f"{Colors.YELLOW}╰── Enter phone numbers (comma separated): {Colors.RESET}").strip()
            if phones:
                phone_list = [p.strip() for p in phones.split(',')]
                print(f"\n{Colors.CYAN}❯❯❯❯ Bulk Checking {len(phone_list)} numbers...{Colors.RESET}")
                
                for i, phone in enumerate(phone_list, 1):
                    if phone:
                        print(f"\n{Colors.BLUE}❯❯❯❯ [{i}/{len(phone_list)}] Checking: {phone}{Colors.RESET}")
                        if phone_tool.validate_malaysian_number(phone):
                            formatted = phone_tool.format_malaysian_number(phone)
                            carrier_info = phone_tool.get_carrier_info(formatted)
                            whatsapp = phone_tool.check_whatsapp(formatted)
                            
                            print(f"  {Colors.GREEN}╰── • Formatted: {formatted}{Colors.RESET}")
                            if 'error' not in carrier_info:
                                print(f"  {Colors.GREEN}╰── • Carrier: {carrier_info.get('carrier', 'Unknown')}{Colors.RESET}")
                            if 'error' not in whatsapp:
                                print(f"  {Colors.GREEN}╰── • WhatsApp: {'✅ YES' if whatsapp.get('has_whatsapp') else '❌ NO'}{Colors.RESET}")
                        else:
                            print(f"  {Colors.RED}╰── • Invalid format{Colors.RESET}")
                
                input(f"\n{Colors.BLUE}❯❯❯❯ Press Enter to continue...{Colors.RESET}")
        
        elif choice == '4':
            prefix = input(f"{Colors.YELLOW}╰── Enter 3-digit prefix (010, 011, etc): {Colors.RESET}").strip()
            if prefix and len(prefix) == 3 and prefix.isdigit():
                prefix_info = {
                    '010': {'carrier': '📱 DIGI', 'launch': '1995', 'coverage': 'Nationwide'},
                    '011': {'carrier': '📱 DIGI/CELCOM', 'launch': '1995', 'coverage': 'Nationwide'},
                    '012': {'carrier': '📱 MAXIS', 'launch': '1995', 'coverage': 'Nationwide'},
                    '013': {'carrier': '📱 CELCOM', 'launch': '1995', 'coverage': 'Nationwide'},
                    '014': {'carrier': '📱 DIGI', 'launch': '2005', 'coverage': 'Nationwide'},
                    '015': {'carrier': '📱 DIGI', 'launch': '2006', 'coverage': 'Nationwide'},
                    '016': {'carrier': '📱 MAXIS', 'launch': '2006', 'coverage': 'Nationwide'},
                    '017': {'carrier': '📱 MAXIS', 'launch': '2007', 'coverage': 'Nationwide'},
                    '018': {'carrier': '📱 UMOBILE', 'launch': '2008', 'coverage': 'Major cities'},
                    '019': {'carrier': '📱 CELCOM', 'launch': '2008', 'coverage': 'Nationwide'},
                }
                
                if prefix in prefix_info:
                    info = prefix_info[prefix]
                    print(f"\n{Colors.BLUE}❯❯❯❯ Prefix {prefix} Information{Colors.RESET}")
                    print(f"  {Colors.GREEN}╰── • Carrier: {info['carrier']}{Colors.RESET}")
                    print(f"  {Colors.GREEN}╰── • Launch Year: {info['launch']}{Colors.RESET}")
                    print(f"  {Colors.GREEN}╰── • Coverage: {info['coverage']}{Colors.RESET}")
                    print(f"  {Colors.GREEN}╰── • Example: +60{prefix}xxxxxxx{Colors.RESET}")
                else:
                    print(f"{Colors.RED}╰── ❌ Prefix not found in database{Colors.RESET}")
                
                input(f"\n{Colors.BLUE}❯❯❯❯ Press Enter to continue...{Colors.RESET}")
        
        elif choice == '5':
            show_format_guide()
            input(f"\n{Colors.BLUE}❯❯❯❯ Press Enter to continue...{Colors.RESET}")
        
        elif choice == '0':
            print(f"\n{Colors.RED}❯❯❯❯ Exiting PlandoxSing...{Colors.RESET}")
            print(f"{Colors.GREEN}╰── ✨ Thank you for using!{Colors.RESET}")
            break
        
        else:
            print(f"{Colors.RED}╰── ❌ Invalid option!{Colors.RESET}")


def check_dependencies():
    missing = []
    
    try:
        import phonenumbers
    except ImportError:
        missing.append("phonenumbers")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    return missing

if __name__ == "__main__":

    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"{Colors.RED}❯❯❯❯ Missing dependencies: {', '.join(missing_deps)}{Colors.RESET}")
        print(f"{Colors.YELLOW}╰── 💡 Install with: pip install {' '.join(missing_deps)}{Colors.RESET}")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}❯❯❯❯ Program terminated{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}╰── ❌ Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
