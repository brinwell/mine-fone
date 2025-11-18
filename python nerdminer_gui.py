import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import threading
import time
import hashlib
import random
import requests
import json
from datetime import datetime

# Горизонтальный OLED стиль NerdMiner
Window.clearcolor = get_color_from_hex('#000000')
Window.size = (600, 200)  # Горизонтальный дисплей

class HashRateGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.size_hint = (1, 0.3)
        
    def on_size(self, *args):
        self.update_graph()
        
    def add_point(self, hash_rate):
        if hash_rate > 0:
            self.points.append(hash_rate)
            if len(self.points) > 30:
                self.points.pop(0)
            self.update_graph()
        
    def update_graph(self):
        self.canvas.clear()
        if not self.points:
            return
            
        with self.canvas:
            # Фон
            Color(0.05, 0.05, 0.05, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Линия графика
            Color(0, 1, 0, 1)
            max_val = max(self.points) if max(self.points) > 0 else 1
            
            points = []
            for i, value in enumerate(self.points):
                x = self.x + (i / (len(self.points) - 1)) * self.width if len(self.points) > 1 else self.x
                y = self.y + (value / max_val) * self.height
                points.extend([x, y])
            
            if len(points) >= 4:
                Line(points=points, width=1.5)

class NetworkData:
    def __init__(self):
        self.btc_price = 0
        self.block_height = 0
        self.difficulty = "0"
        self.network_hashrate = "0 H/s"
        self.last_update = 0
        
    def fetch_btc_price(self):
        """Получение цены BTC с CoinGecko"""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.btc_price = data['bitcoin']['usd']
                return True
        except Exception as e:
            print(f"Price fetch error: {e}")
        return False
        
    def fetch_blockchain_data(self):
        """Получение данных блокчейна"""
        try:
            # Высота блока
            response = requests.get("https://blockchain.info/q/getblockcount", timeout=10)
            if response.status_code == 200:
                self.block_height = int(response.text)
            else:
                return False
            
            # Сложность
            response = requests.get("https://blockchain.info/q/getdifficulty", timeout=10)
            if response.status_code == 200:
                diff = float(response.text)
                
                # Форматирование сложности
                if diff >= 1e12:
                    self.difficulty = f"{diff/1e12:.2f}T"
                elif diff >= 1e9:
                    self.difficulty = f"{diff/1e9:.2f}G"
                elif diff >= 1e6:
                    self.difficulty = f"{diff/1e6:.2f}M"
                else:
                    self.difficulty = f"{diff:.0f}"
                
                # Расчет сетевого хешрейта
                network_hash = diff * 2**32 / 600  # хешей в секунду
                
                # Форматирование хешрейта
                if network_hash >= 1e18:
                    self.network_hashrate = f"{network_hash/1e18:.2f} EH/s"
                elif network_hash >= 1e15:
                    self.network_hashrate = f"{network_hash/1e15:.2f} PH/s"
                elif network_hash >= 1e12:
                    self.network_hashrate = f"{network_hash/1e12:.2f} TH/s"
                elif network_hash >= 1e9:
                    self.network_hashrate = f"{network_hash/1e9:.2f} GH/s"
                elif network_hash >= 1e6:
                    self.network_hashrate = f"{network_hash/1e6:.2f} MH/s"
                else:
                    self.network_hashrate = f"{network_hash:.0f} H/s"
                    
            return True
        except Exception as e:
            print(f"Blockchain data error: {e}")
        return False
        
    def update_all(self):
        """Обновление всех данных"""
        if time.time() - self.last_update > 60:  # Обновлять раз в минуту
            price_success = self.fetch_btc_price()
            blockchain_success = self.fetch_blockchain_data()
            self.last_update = time.time()
            return price_success or blockchain_success
        return False
        
    def fetch_btc_price(self):
        """Получение цены BTC с CoinGecko"""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.btc_price = data['bitcoin']['usd']
                return True
        except Exception as e:
            print(f"Price fetch error: {e}")
        return False
        
    def fetch_blockchain_data(self):
        """Получение данных блокчейна"""
        try:
            # Высота блока
            response = requests.get("https://blockchain.info/q/getblockcount", timeout=10)
            if response.status_code == 200:
                self.block_height = int(response.text)
            
            # Сложность
            response = requests.get("https://blockchain.info/q/getdifficulty", timeout=10)
            if response.status_code == 200:
                diff = float(response.text)
                if diff >= 1e12:
                    self.difficulty = f"{diff/1e12:.2f}T"
                else:
                    self.difficulty = f"{diff/1e9:.2f}G"
                
                # Расчет сетевого хешрейта
                network_hash = diff * 2**32 / 600  # хешей в секунду
                if network_hash >= 1e18:
                    self.network_hashrate = f"{network_hash/1e18:.2f}EH/s"
                else:
                    self.network_hashrate = f"{network_hash/1e15:.2f}PH/s"
                    
            return True
        except Exception as e:
            print(f"Blockchain data error: {e}")
        return False
        
    def update_all(self):
        """Обновление всех данных"""
        if time.time() - self.last_update > 60:  # Обновлять раз в минуту
            price_success = self.fetch_btc_price()
            blockchain_success = self.fetch_blockchain_data()
            self.last_update = time.time()
            return price_success or blockchain_success
        return False

class NerdMinerGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [5, 5]
        self.spacing = 5
        
        # Данные майнера
        self.mining = False
        self.screen_on = True
        self.hash_rate = 0
        self.total_hashes = 0
        self.accepted_shares = 0
        self.uptime = 0
        self.start_time = 0
        self.temperature = 42
        
        # Сетевые данные
        self.network_data = NetworkData()
        
        # Управление кнопками
        self.power_last_press = 0
        self.volume_last_press = 0
        self.volume_press_count = 0
        
        self.hash_history = []
        
        self.setup_ui()
        self.setup_keyboard()
        self.start_background_tasks()
        
    def setup_ui(self):
        # ЛЕВАЯ ЧАСТЬ - Статистика майнинга
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=2)
        
        # Заголовок
        title_label = Label(
            text='NERDMINER v2',
            font_size='16sp',
            bold=True,
            color=get_color_from_hex('#00FF00'),
            size_hint=(1, 0.15)
        )
        left_panel.add_widget(title_label)
        
        # Статус
        self.status_label = Label(
            text='STOPPED',
            font_size='14sp',
            color=get_color_from_hex('#FF0000'),
            size_hint=(1, 0.1)
        )
        left_panel.add_widget(self.status_label)
        
        # Хешрейт
        self.hashrate_label = Label(
            text='H/s: 0',
            font_size='12sp',
            color=get_color_from_hex('#00FF00'),
            size_hint=(1, 0.1)
        )
        left_panel.add_widget(self.hashrate_label)
        
        # Шары
        self.shares_label = Label(
            text='Shares: 0',
            font_size='12sp',
            color=get_color_from_hex('#FFFFFF'),
            size_hint=(1, 0.1)
        )
        left_panel.add_widget(self.shares_label)
        
        # Всего хешей
        self.total_hashes_label = Label(
            text='Total: 0',
            font_size='12sp',
            color=get_color_from_hex('#FFFFFF'),
            size_hint=(1, 0.1)
        )
        left_panel.add_widget(self.total_hashes_label)
        
        # Аптайм
        self.uptime_label = Label(
            text='Time: 00:00:00',
            font_size='12sp',
            color=get_color_from_hex('#888888'),
            size_hint=(1, 0.1)
        )
        left_panel.add_widget(self.uptime_label)
        
        # Температура
        self.temp_label = Label(
            text='Temp: 42°C',
            font_size='12sp',
            color=get_color_from_hex('#888888'),
            size_hint=(1, 0.1)
        )
        left_panel.add_widget(self.temp_label)
        
        # Информация об управлении
        controls_label = Label(
            text='PWR:Screen  VOLx2:Mine',
            font_size='10sp',
            color=get_color_from_hex('#444444'),
            size_hint=(1, 0.15)
        )
        left_panel.add_widget(controls_label)
        
        self.add_widget(left_panel)
        
        # ЦЕНТРАЛЬНАЯ ЧАСТЬ - График
        self.graph = HashRateGraph()
        self.add_widget(self.graph)
        
        # ПРАВАЯ ЧАСТЬ - Информация о сети
        right_panel = BoxLayout(orientation='vertical', size_hint=(0.3, 1), spacing=2)
        
        # Блок
        self.block_label = Label(
            text='Block: 820000',
            font_size='12sp',
            color=get_color_from_hex('#00FF00'),
            size_hint=(1, 0.15)
        )
        right_panel.add_widget(self.block_label)
        
        # Цена BTC
        self.price_label = Label(
            text='BTC: $45,000',
            font_size='12sp',
            color=get_color_from_hex('#00FF00'),
            size_hint=(1, 0.15)
        )
        right_panel.add_widget(self.price_label)
        
        # Сложность
        self.diff_label = Label(
            text='Diff: 81.73T',
            font_size='12sp',
            color=get_color_from_hex('#888888'),
            size_hint=(1, 0.15)
        )
        right_panel.add_widget(self.diff_label)
        
        # Хешрейт сети
        self.net_hash_label = Label(
            text='Net: 295EH/s',
            font_size='12sp',
            color=get_color_from_hex('#888888'),
            size_hint=(1, 0.15)
        )
        right_panel.add_widget(self.net_hash_label)
        
        # Эффективность
        self.efficiency_label = Label(
            text='Eff: 100%',
            font_size='12sp',
            color=get_color_from_hex('#888888'),
            size_hint=(1, 0.15)
        )
        right_panel.add_widget(self.efficiency_label)
        
        # Время обновления
        self.update_label = Label(
            text='Updated: --:--:--',
            font_size='9sp',
            color=get_color_from_hex('#333333'),
            size_hint=(1, 0.1)
        )
        right_panel.add_widget(self.update_label)
        
        self.add_widget(right_panel)
        
    def setup_keyboard(self):
        """Настройка обработки клавиш для тестирования"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Обработка нажатий клавиш для тестирования"""
        # P - кнопка POWER
        if keycode[1] == 'p':
            self.handle_power_button()
            return True
        # V - кнопка VOLUME
        elif keycode[1] == 'v':
            self.handle_volume_button()
            return True
        # R - принудительное обновление данных
        elif keycode[1] == 'r':
            self.network_data.last_update = 0  # Сбрасываем таймер
            self.network_data.update_all()
            return True
        # Q - выход
        elif keycode[1] == 'q':
            App.get_running_app().stop()
            return True
        return False
        
    def handle_power_button(self):
        """Обработка кнопки POWER - экран вкл/выкл"""
        current_time = time.time()
        
        # Одинарное нажатие - переключаем экран
        if current_time - self.power_last_press > 0.5:
            self.screen_on = not self.screen_on
            self.update_screen_state()
            
        self.power_last_press = current_time
        
    def handle_volume_button(self):
        """Обработка кнопки VOLUME - старт/стоп майнинг"""
        current_time = time.time()
        
        # Сбрасываем счетчик если прошло больше 1 секунды
        if current_time - self.volume_last_press > 1.0:
            self.volume_press_count = 0
            
        self.volume_press_count += 1
        self.volume_last_press = current_time
        
        # Двойное нажатие = старт/стоп майнинг
        if self.volume_press_count == 2:
            if self.mining:
                self.stop_mining()
            else:
                self.start_mining()
            self.volume_press_count = 0
            
    def update_screen_state(self):
        """Обновление состояния экрана"""
        if self.screen_on:
            # Показываем интерфейс
            for child in self.children:
                child.opacity = 1.0
        else:
            # Скрываем интерфейс (имитация выключения экрана)
            for child in self.children:
                child.opacity = 0.0
                
    def start_mining(self):
        """Запуск майнинга"""
        if not self.screen_on:
            self.screen_on = True
            self.update_screen_state()
            
        self.mining = True
        self.start_time = time.time()
        self.status_label.text = 'MINING'
        self.status_label.color = get_color_from_hex('#00FF00')
        
        mining_thread = threading.Thread(target=self.mining_worker, daemon=True)
        mining_thread.start()
        
    def stop_mining(self):
        """Остановка майнинга"""
        self.mining = False
        self.status_label.text = 'STOPPED'
        self.status_label.color = get_color_from_hex('#FF0000')
        self.hash_rate = 0
        
    def mining_worker(self):
        """Рабочий поток майнинга"""
        local_hashes = 0
        last_stat_time = time.time()
        
        while self.mining:
            # Имитация майнинга SHA-256
            data = f"nerdminer{time.time()}{random.randint(0, 1000000)}"
            hash_result = hashlib.sha256(data.encode()).hexdigest()
            
            self.total_hashes += 1
            local_hashes += 1
            
            # Обновление хешрейта каждую секунду
            current_time = time.time()
            if current_time - last_stat_time >= 1.0:
                self.hash_rate = local_hashes
                local_hashes = 0
                last_stat_time = current_time
                
            # Случайное нахождение шара
            if random.random() < 0.001:
                self.accepted_shares += 1
                
            time.sleep(0.003)
            
    def start_background_tasks(self):
        """Запуск фоновых задач"""
        Clock.schedule_interval(self.update_stats, 1.0)
        Clock.schedule_interval(self.update_network_data, 30.0)  # Обновление каждые 30 сек
        Clock.schedule_interval(self.update_temperature, 5.0)
        
    def update_stats(self, dt):
        """Обновление статистики"""
        if self.mining:
            self.uptime = time.time() - self.start_time
            
            # Хешрейт
            if self.hash_rate >= 1000:
                hr_text = f"H/s: {self.hash_rate/1000:.1f}k"
            else:
                hr_text = f"H/s: {self.hash_rate}"
            self.hashrate_label.text = hr_text
            
            # Шары
            self.shares_label.text = f'Shares: {self.accepted_shares}'
            
            # Всего хешей
            if self.total_hashes >= 1000:
                total_text = f'Total: {self.total_hashes/1000:.1f}k'
            else:
                total_text = f'Total: {self.total_hashes}'
            self.total_hashes_label.text = total_text
            
            # Время
            hours = int(self.uptime // 3600)
            minutes = int((self.uptime % 3600) // 60)
            seconds = int(self.uptime % 60)
            self.uptime_label.text = f'Time: {hours:02d}:{minutes:02d}:{seconds:02d}'
            
            # График
            self.graph.add_point(self.hash_rate)
            
    def update_network_data(self, dt):
        """Обновление сетевых данных"""
        if self.network_data.update_all():
            # Обновляем UI с реальными данными
            self.block_label.text = f'Block: {self.network_data.block_height:,}'
            self.price_label.text = f'BTC: ${self.network_data.btc_price:,.0f}'
            self.diff_label.text = f'Diff: {self.network_data.difficulty}'
            self.net_hash_label.text = f'Net: {self.network_data.network_hashrate}'
            self.update_label.text = f'Updated: {datetime.now().strftime("%H:%M:%S")}'
        
    def update_temperature(self, dt):
        """Обновление температуры"""
        if self.mining:
            base_temp = 40
            load_factor = min(self.hash_rate / 50000, 1.0)
            self.temperature = base_temp + int(load_factor * 20)
        else:
            self.temperature = max(35, self.temperature - 1)
            
        self.temp_label.text = f'Temp: {self.temperature}°C'

class NerdMinerApp(App):
    def build(self):
        self.title = 'NerdMiner v2 - Android'
        return NerdMinerGUI()

if __name__ == '__main__':
    NerdMinerApp().run()