# -*- coding: utf-8 -*-
"""چک‌یار و اقساط‌بان - نسخه اولیه اندروید (Kivy)
ذخیره‌سازی محلی؛ برای ساخت APK با Buildozer آماده شده است.
"""
import os, json, csv, hashlib, uuid
from datetime import datetime, timedelta
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty
from kivy.utils import platform
from kivy.core.window import Window

APP_TITLE = 'چک‌یار و اقساط‌بان'
LICENSE_SALT = 'FarhadNorouzi_Secret'  # برای انتشار تجاری، بهتر است اعتبارسنجی امن‌تری جایگزین شود.

KV = r'''
#:import dp kivy.metrics.dp
<RTLLabel@Label>:
    halign: 'right'
    valign: 'middle'
    text_size: self.size
    color: 0.10,0.16,0.28,1
<MainButton@Button>:
    size_hint_y: None
    height: dp(46)
    background_normal: ''
    background_color: 0.12,0.23,0.54,1
    color: 1,1,1,1
    font_size: '15sp'
<MainInput@TextInput>:
    size_hint_y: None
    height: dp(44)
    multiline: False
    halign: 'right'
    padding: dp(10), dp(10)
    font_size: '15sp'
<Screen>:
    canvas.before:
        Color:
            rgba: 0.95,0.96,0.98,1
        Rectangle:
            pos: self.pos
            size: self.size
<ActivationScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(10)
        RTLLabel:
            text: '[b]فعال‌سازی چک‌یار و اقساط‌بان[/b]'
            markup: True
            font_size: '22sp'
            size_hint_y: None
            height: dp(60)
        RTLLabel:
            text: 'شناسه نصب این برنامه را برای دریافت کد فعال‌سازی ارسال کنید:'
            size_hint_y: None
            height: dp(54)
        TextInput:
            id: install_id
            text: root.install_id
            readonly: True
            size_hint_y: None
            height: dp(48)
            halign: 'center'
        MainInput:
            id: license_key
            hint_text: 'کد فعال‌سازی'
            halign: 'center'
        MainButton:
            text: 'فعال‌سازی'
            on_release: root.activate(license_key.text)
        RTLLabel:
            text: root.status
            color: (0.7,0.1,0.1,1)

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.12,0.23,0.54,1
            Rectangle:
                pos: self.x, self.top-dp(84)
                size: self.width, dp(84)
        RTLLabel:
            text: '[b]چک‌یار و اقساط‌بان[/b]\nنسخه اندروید آفلاین'
            markup: True
            color: 1,1,1,1
            font_size: '20sp'
            size_hint_y: None
            height: dp(78)
        MainButton:
            text: 'راس‌گیری چک‌ها'
            on_release: app.root.current = 'checks'
        MainButton:
            text: 'فروش اقساطی و سود'
            on_release: app.root.current = 'installments'
        MainButton:
            text: 'محاسبه خسارت دیرکرد'
            on_release: app.root.current = 'penalty'
        MainButton:
            text: 'پشتیبان‌گیری و خروجی CSV'
            on_release: app.export_csv()
        MainButton:
            text: 'نمایش شناسه نصب / فعال‌سازی'
            on_release: app.show_license_info()
        Widget:
        RTLLabel:
            text: 'اطلاعات به‌صورت خودکار روی همین گوشی ذخیره می‌شود.'
            size_hint_y: None
            height: dp(50)

<ChecksScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(6)
        RTLLabel:
            text: '[b]راس‌گیری چک‌ها[/b]'
            markup: True
            font_size: '20sp'
            size_hint_y: None
            height: dp(42)
        MainInput:
            id: person
            hint_text: 'نام شخص'
        MainInput:
            id: reason
            hint_text: 'بابت'
        MainInput:
            id: amount
            hint_text: 'مبلغ چک (ریال)'
            input_filter: 'float'
        MainInput:
            id: date_j
            hint_text: 'تاریخ شمسی سررسید، مانند 1405/08/15'
        MainInput:
            id: days
            hint_text: 'یا تعداد روز تا سررسید'
            input_filter: 'int'
        MainButton:
            text: 'افزودن چک'
            on_release: root.add_check(person.text, reason.text, amount.text, date_j.text, days.text)
        MainButton:
            text: 'محاسبه راس و جمع کل'
            on_release: root.calculate()
        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: check_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(4)
        RTLLabel:
            id: result
            text: root.result_text
            size_hint_y: None
            height: dp(110)
        MainButton:
            text: 'حذف آخرین چک'
            on_release: root.remove_last()
        MainButton:
            text: 'بازگشت به خانه'
            on_release: app.root.current = 'home'

<InstallmentScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(6)
        RTLLabel:
            text: '[b]فروش اقساطی و سود نزولی[/b]'
            markup: True
            font_size: '20sp'
            size_hint_y: None
            height: dp(42)
        MainInput:
            id: person
            hint_text: 'نام شخص'
        MainInput:
            id: reason
            hint_text: 'بابت / شرح فروش'
        MainInput:
            id: total
            hint_text: 'قیمت کل (ریال)'
            input_filter: 'float'
        MainInput:
            id: cash
            hint_text: 'پرداخت نقدی (ریال)'
            input_filter: 'float'
        MainInput:
            id: rate
            hint_text: 'نرخ سود ماهیانه (درصد)'
            input_filter: 'float'
        MainInput:
            id: months
            hint_text: 'تعداد اقساط (ماه)'
            input_filter: 'int'
        MainInput:
            id: start_date
            hint_text: 'تاریخ اولین قسط شمسی: 1405/08/15'
        MainButton:
            text: 'محاسبه و افزودن اقساط به فهرست چک‌ها'
            on_release: root.generate(person.text, reason.text, total.text, cash.text, rate.text, months.text, start_date.text)
        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: result_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(4)
        RTLLabel:
            id: result
            text: root.result_text
            size_hint_y: None
            height: dp(75)
        MainButton:
            text: 'بازگشت به خانه'
            on_release: app.root.current = 'home'

<PenaltyScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(8)
        RTLLabel:
            text: '[b]محاسبه خسارت دیرکرد[/b]'
            markup: True
            font_size: '20sp'
            size_hint_y: None
            height: dp(48)
        MainInput:
            id: debt
            hint_text: 'مبلغ بدهی / چک (ریال)'
            input_filter: 'float'
        MainInput:
            id: days
            hint_text: 'تعداد روزهای تأخیر'
            input_filter: 'int'
        MainInput:
            id: monthly_rate
            hint_text: 'نرخ جریمه ماهیانه (درصد) - اختیاری'
            input_filter: 'float'
        MainInput:
            id: daily_rate
            hint_text: 'نرخ جریمه روزانه (درصد)'
            input_filter: 'float'
        MainButton:
            text: 'تبدیل نرخ ماهانه به روزانه'
            on_release: root.convert_rate(monthly_rate.text)
        MainButton:
            text: 'محاسبه خسارت'
            on_release: root.calculate(debt.text, days.text, daily_rate.text)
        RTLLabel:
            id: result
            text: root.result_text
            font_size: '20sp'
            size_hint_y: None
            height: dp(100)
        MainButton:
            text: 'پاک کردن فرم'
            on_release: root.clear_form()
        MainButton:
            text: 'بازگشت به خانه'
            on_release: app.root.current = 'home'
'''


def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + 365 * jy + (jy // 33 * 8) + (((jy % 33) + 3) // 4) + jd
    days += (jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097); days %= 146097
    if days > 36524:
        days -= 1; gy += 100 * (days // 36524); days %= 36524
    if days > 365:
        days += 1; gy += 4 * (days // 1461); days %= 1461
    gy += 4 * (days // 1461); days %= 1461
    if days > 365:
        gy += (days - 1) // 365; days = (days - 1) % 365
    gd = days + 1
    sal = [0,31,29 if (gy%4==0 and gy%100!=0) or gy%400==0 else 28,31,30,31,30,31,31,30,31,30,31]
    gm = 0
    while gm < 13 and gd > sal[gm]:
        gd -= sal[gm]; gm += 1
    return datetime(gy, gm, gd)


def gregorian_to_jalali(gy, gm, gd):
    gdim = [31,28,31,30,31,30,31,31,30,31,30,31]
    gy2, gm2, gd2 = gy-1600, gm-1, gd-1
    gdn = 365*gy2 + (gy2+3)//4 - (gy2+99)//100 + (gy2+399)//400
    for i in range(gm2): gdn += gdim[i]
    if gm2 > 1 and ((gy%4==0 and gy%100!=0) or gy%400==0): gdn += 1
    jdn = gdn - 79; jnp = jdn // 12053; jdn %= 12053
    jy = 979 + 33*jnp + 4*(jdn//1461); jdn %= 1461
    if jdn >= 365: jy += (jdn-1)//365; jdn = (jdn-1)%365
    if jdn < 186: jm, jd = 1+jdn//31, 1+jdn%31
    else: jm, jd = 7+(jdn-186)//30, 1+(jdn-186)%30
    return jy, jm, jd


def parse_jalali(s):
    p = s.strip().replace('-', '/').split('/')
    if len(p) != 3: raise ValueError('تاریخ باید به شکل سال/ماه/روز باشد.')
    return jalali_to_gregorian(*(int(x) for x in p))


def fmt_jalali(dt):
    y,m,d = gregorian_to_jalali(dt.year, dt.month, dt.day)
    return f'{y:04d}/{m:02d}/{d:02d}'


class ActivationScreen(Screen):
    install_id = StringProperty('')
    status = StringProperty('')
    def on_pre_enter(self, *args): self.install_id = App.get_running_app().install_id
    def activate(self, key):
        app = App.get_running_app()
        if key.strip().upper() == app.expected_license():
            app.store['license'] = key.strip().upper(); app.save_store()
            app.root.current = 'home'
        else: self.status = 'کد فعال‌سازی صحیح نیست.'

class HomeScreen(Screen): pass

class ChecksScreen(Screen):
    result_text = StringProperty('')
    def on_pre_enter(self, *args): self.refresh()
    def refresh(self):
        box = self.ids.check_list; box.clear_widgets()
        from kivy.uix.label import Label
        for i,c in enumerate(App.get_running_app().store['checks']):
            box.add_widget(Label(text=f"{i+1}) {c.get('person','')} | {c.get('babat','')} | {c['amount']:,.0f} ریال | {c['date']} ({c['days']} روز)", size_hint_y=None, height=42, color=(.1,.16,.28,1), halign='right', valign='middle', text_size=(Window.width-25,None)))
    def add_check(self, person, reason, amount, date_s, days_s):
        try:
            if not amount.strip(): raise ValueError('مبلغ چک را وارد کنید.')
            amount_v = float(amount.replace(',',''))
            if date_s.strip():
                target = parse_jalali(date_s); days = (target.date()-datetime.now().date()).days; date_out = fmt_jalali(target)
            elif days_s.strip():
                days = int(days_s); date_out = fmt_jalali(datetime.now()+timedelta(days=days))
            else: raise ValueError('تاریخ سررسید یا تعداد روز را وارد کنید.')
            App.get_running_app().store['checks'].append({'person':person.strip() or '---','babat':reason.strip() or '---','amount':amount_v,'days':days,'date':date_out})
            App.get_running_app().save_store(); self.refresh(); self.calculate()
            for k in ('person','reason','amount','date_j','days'): self.ids[k].text=''
        except Exception as e: self.result_text = f'خطا: {e}'
    def calculate(self):
        checks = App.get_running_app().store['checks']
        if not checks: self.result_text='هنوز چکی ثبت نشده است.'; return
        total=sum(c['amount'] for c in checks); weighted=sum(c['amount']*c['days'] for c in checks)
        avg=round(weighted/total) if total else 0
        dt=datetime.now()+timedelta(days=avg)
        self.result_text=f'جمع کل: {total:,.0f} ریال\nمجموع مبلغ × روز: {weighted:,.0f}\nروز راس: {avg}\nتاریخ راس شمسی: {fmt_jalali(dt)}'
    def remove_last(self):
        checks=App.get_running_app().store['checks']
        if checks: checks.pop(); App.get_running_app().save_store()
        self.refresh(); self.calculate()

class InstallmentScreen(Screen):
    result_text = StringProperty('')
    def on_pre_enter(self, *args):
        if not self.ids.start_date.text: self.ids.start_date.text=fmt_jalali(datetime.now())
        self.refresh()
    def refresh(self):
        box=self.ids.result_list; box.clear_widgets()
        from kivy.uix.label import Label
        for c in App.get_running_app().store['checks'][-40:]:
            box.add_widget(Label(text=f"{c.get('person','')} | {c.get('babat','')} | {c['amount']:,.0f} ریال | {c['date']}", size_hint_y=None, height=38, color=(.1,.16,.28,1), halign='right', valign='middle', text_size=(Window.width-25,None)))
    def generate(self, person, reason, total, cash, rate, months, start):
        try:
            total_v=float(total.replace(',','')); cash_v=float(cash.replace(',','') or 0); r=float(rate)/100; n=int(months)
            principal=total_v-cash_v
            if principal<=0 or n<=0: raise ValueError('مانده بدهی و تعداد اقساط باید بیشتر از صفر باشند.')
            start_dt=parse_jalali(start); monthly=principal/n; remain=principal; interest_sum=0; new=[]
            for i in range(n):
                interest=remain*r; interest_sum+=interest
                target=start_dt+timedelta(days=30*i)
                new.append({'person':person.strip() or '---','babat':f"{reason.strip() or 'خرید'} (قسط {i+1} از {n})",'amount':monthly+interest,'days':(target.date()-datetime.now().date()).days,'date':fmt_jalali(target)})
                remain-=monthly
            app=App.get_running_app(); app.store['checks'].extend(new); app.save_store(); self.refresh()
            self.result_text=f'{n} قسط افزوده شد.\nمجموع سود: {interest_sum:,.0f} ریال | کل با سود: {principal+interest_sum:,.0f} ریال'
        except Exception as e: self.result_text=f'خطا: {e}'

class PenaltyScreen(Screen):
    result_text=StringProperty('مبلغ خسارت: ۰ ریال')
    def convert_rate(self, monthly):
        try:
            if not monthly.strip(): raise ValueError('نرخ ماهانه را وارد کنید.')
            self.ids.daily_rate.text=str(float(monthly)/30)
        except Exception as e: self.result_text=f'خطا: {e}'
    def calculate(self, debt, days, rate):
        try:
            v=float(debt.replace(',','')); d=int(days); r=float(rate)
            if v<0 or d<0 or r<0: raise ValueError('مقادیر نباید منفی باشند.')
            self.result_text=f'مبلغ کل خسارت دیرکرد:\n{v*(r/100)*d:,.0f} ریال'
        except Exception as e: self.result_text=f'خطا: {e}'
    def clear_form(self):
        for k in ('debt','days','monthly_rate','daily_rate'): self.ids[k].text=''
        self.result_text='مبلغ خسارت: ۰ ریال'

class ChekyarApp(App):
    def build(self):
        self.title=APP_TITLE
        self.store_path=os.path.join(self.user_data_dir,'chekyar_data.json')
        self.install_id=self.load_install_id()
        self.store={'checks':[],'license':''}
        try:
            with open(self.store_path,'r',encoding='utf-8') as f: self.store.update(json.load(f))
        except Exception: pass
        Builder.load_string(KV)
        sm=ScreenManager()
        sm.add_widget(ActivationScreen(name='activation')); sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ChecksScreen(name='checks')); sm.add_widget(InstallmentScreen(name='installments')); sm.add_widget(PenaltyScreen(name='penalty'))
        sm.current='home' if self.store.get('license')==self.expected_license() else 'activation'
        return sm
    def load_install_id(self):
        p=os.path.join(self.user_data_dir,'install_id.txt')
        try:
            with open(p,'r',encoding='utf-8') as f: return f.read().strip()
        except Exception:
            value=hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()[:16].upper()
            try:
                os.makedirs(self.user_data_dir,exist_ok=True)
                with open(p,'w',encoding='utf-8') as f: f.write(value)
            except Exception: pass
            return value
    def expected_license(self): return hashlib.md5((self.install_id+LICENSE_SALT).encode()).hexdigest()[:16].upper()
    def save_store(self):
        os.makedirs(self.user_data_dir,exist_ok=True)
        with open(self.store_path,'w',encoding='utf-8') as f: json.dump(self.store,f,ensure_ascii=False,indent=2)
    def export_csv(self):
        path=os.path.join(self.user_data_dir,'chekyar_backup.csv')
        with open(path,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f); w.writerow(['ردیف','نام شخص','بابت','مبلغ ریال','تاریخ سررسید شمسی','روز تا سررسید'])
            for i,c in enumerate(self.store['checks'],1): w.writerow([i,c.get('person',''),c.get('babat',''),c['amount'],c.get('date',''),c['days']])
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        Popup(title='تهیه خروجی',content=Label(text=f'فایل CSV ذخیره شد:\n{path}'),size_hint=(.9,.4)).open()
    def show_license_info(self):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        box=BoxLayout(orientation='vertical',padding=10,spacing=8)
        box.add_widget(Label(text=f'شناسه نصب:\n{self.install_id}\n\nکد فعال‌سازی این شناسه:\n{self.expected_license()}',halign='center'))
        btn=Button(text='بستن',size_hint_y=None,height=44); box.add_widget(btn)
        pop=Popup(title='اطلاعات فعال‌سازی',content=box,size_hint=(.9,.45)); btn.bind(on_release=pop.dismiss); pop.open()

if __name__ == '__main__': ChekyarApp().run()
