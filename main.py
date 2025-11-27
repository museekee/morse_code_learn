# region 패키지나 assets 다운로드
try:
    import os
    from PyQt6.QtCore import QFile
    from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QWidget, QVBoxLayout, QCheckBox, QDialogButtonBox
    from PyQt6.uic import loadUi
    from PyQt6.QtGui import QPixmap, QPainter, QFont, QFontDatabase, QTextCursor
    from PyQt6.QtCore import Qt, QByteArray, QTimer, QUrl
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6 import QtCore
    from PyQt6.QtWebSockets import QWebSocket
    import darkdetect
    import random
    import sounddevice as sd
    import soundfile as sf
    import requests
    import io
    import threading
    import json
    import winsound
    import configparser

    no_sound = True  # 모스부호 소리 안나게
    # 메모리에 저장할 asset들.....
    assets = {
        "font": {
            "Jersey25-Regular.ttf": None
        },
        "sound": {
            "beep.wav": None
        },
        "img": {
            "dark": {
                "숫자기호.svg": None,
                "알파벳.svg": None,
                "한글.svg": None
            },
            "light": {
                "숫자기호.svg": None,
                "알파벳.svg": None,
                "한글.svg": None
            },
            "correct.png": None,
            "wrong.png": None
        },
        "ui": {
            "learn.ui": None,
            "memorize.ui": None,
            "portal.ui": None,
            "play.ui": None,
            "room_connector.ui": None,
            "room.ui": None,
            "setting.ui": None
        }
    }

    # 딕셔너리 재귀는 구글에서 검색함 ㅠ
    def download_asset(data, path=None, debug=False):
        threads: list[threading.Thread] = []
        log_lock = threading.Lock()

        def download(new_path, k, debug):
            # 로그 겹쳐서 락 거니까 출력 제대로 되더라
            with log_lock:
                print("[Downloading]", "/".join(new_path))
            if debug == False:
                data[k] = requests.get(
                    f"https://github.com/museekee/morse_code_learn/raw/refs/heads/main/assets/{"/".join(new_path)}"
                ).content
            else:
                file_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "assets",
                    *new_path
                )
                with open(file_path, 'rb') as f:
                    data[k] = f.read()

            with log_lock:
                print("[Downloaded]", "/".join(new_path))

        if path == None:
            path = []

        for k, v in data.items():
            new_path = path + [k]
            if isinstance(v, dict):
                download_asset(v, new_path, debug)
            else:
                # 쓰레딩 안 쓰면 하나하나 끝날때까지 받아서 너무 느리더라
                t = threading.Thread(
                    target=lambda: download(new_path, k, debug))
                threads.append(t)
                t.start()

        # 다 다운될때까지 대기시키는거
        for t in threads:
            t.join()

    download_asset(assets, debug=True)

    assets["sound"]["beep.wav"] = sf.read(
        io.BytesIO(assets["sound"]["beep.wav"])
        # 쌤이 적재하지 말고 온라인에서 가져오래서 ㅠㅠ sd에서 쓰기 위해 오디오 데이터와 샘플링데이터로 분리하는 과정... (tuple)
    )
    sd.default.latency = "low"  # 기본 레이턴시 왜 high냐 슬프네

    config = configparser.ConfigParser()

    def load_config(reset=False):
        global config
        if not os.path.exists("1401_config.ini") or reset == True:
            config['setting'] = {
                'exclude_chars': '',  # | 로 구분
                'automatic_time_adjustment': 'true',
                'delay': 'false',
                'don_time': '100',
                'tsu_time': '300',
                'morse_gap': '100',
                'char_gap': '300',
                'word_gap': '700'
            }
            config['play'] = {
                'high_score': '0'
            }
            with open("1401_config.ini", 'w') as f:
                config.write(f)
        else:
            config.read("1401_config.ini", encoding="utf-8")

    load_config()

except ImportError:
    import pip
    import os

    print("Requirements are not installed. Installing...")
    # pyqt6, darkdetect, sounddevice, soundfile, requests 설치
    pip.main(["install", "PyQt6", "darkdetect",
             "sounddevice", "soundfile", "requests"])

    if os.system(f"python \"{__file__}\"") == 0:
        exit(0)
    elif os.system(f"py \"{__file__}\"") == 0:
        exit(0)
    elif os.system(f"python3 \"{__file__}\"") == 0:
        exit(0)
    else:
        print("인 켜지네요... 수동으로 켜주세요!")
        exit(1)
# endregion

# region IME
import time
import threading

common_word_map = {
    'ㆍㅡㅡㅡㅡ': '1',
    'ㆍㆍㅡㅡㅡ': '2',
    'ㆍㆍㆍㅡㅡ': '3',
    'ㆍㆍㆍㆍㅡ': '4',
    'ㆍㆍㆍㆍㆍ': '5',
    'ㅡㆍㆍㆍㆍ': '6',
    'ㅡㅡㆍㆍㆍ': '7',
    'ㅡㅡㅡㆍㆍ': '8',
    'ㅡㅡㅡㅡㆍ': '9',
    'ㅡㅡㅡㅡㅡ': '0',
    'ㆍㅡㆍㅡㆍㅡ': '.',
    'ㅡㅡㆍㆍㅡㅡ': ',',
    'ㆍㆍㅡㅡㆍㆍ': '?',
    'ㅡㆍㆍㅡㆍ': '/',
    'ㅡㅡㅡㆍㆍㆍ': ':',
    'ㅡㆍㅡㆍㅡㆍ': ';',
    'ㅡㆍㅡㅡㆍ': "(",
    'ㅡㆍㅡㅡㆍㅡ': ')',
    'ㆍㅡㅡㅡㅡㅡ': "'",
    'ㆍㅡㆍㆍㅡㆍ': '"',
    'ㅡㆍㆍㆍㅡ': '=',
    'ㆍㅡㆍㅡㆍ': '+',
    'ㅡㆍㆍㆍㆍㅡ': '-',
    'ㆍㆍㅡㅡㆍㅡ': '_',

}
en_word_map = {
    'ㆍㅡ': 'A',
    'ㅡㆍㆍㆍ': 'B',
    'ㅡㆍㅡㆍ': 'C',
    'ㅡㆍㆍ': 'D',
    'ㆍ': 'E',
    'ㆍㆍㅡㆍ': 'F',
    'ㅡㅡㆍ': 'G',
    'ㆍㆍㆍㆍ': 'H',
    'ㆍㆍ': 'I',
    'ㆍㅡㅡㅡ': 'J',
    'ㅡㆍㅡ': 'K',
    'ㆍㅡㆍㆍ': 'L',
    'ㅡㅡ': 'M',
    'ㅡㆍ': 'N',
    'ㅡㅡㅡ': 'O',
    'ㆍㅡㅡㆍ': 'P',
    'ㅡㅡㆍㅡ': 'Q',
    'ㆍㅡㆍ': 'R',
    'ㆍㆍㆍ': 'S',
    'ㅡ': 'T',
    'ㆍㆍㅡ': 'U',
    'ㆍㆍㆍㅡ': 'V',
    'ㆍㅡㅡ': 'W',
    'ㅡㆍㆍㅡ': 'X',
    'ㅡㆍㅡㅡ': 'Y',
    'ㅡㅡㆍㆍ': 'Z',
}
ko_word_map = {
    'ㆍㅡㆍㆍ': 'ㄱ',
    'ㆍㆍㅡㆍ': 'ㄴ',
    'ㅡㆍㆍㆍ': 'ㄷ',
    'ㆍㆍㆍㅡ': 'ㄹ',
    'ㅡㅡ': 'ㅁ',
    'ㆍㅡㅡ': 'ㅂ',
    'ㅡㅡㆍ': 'ㅅ',
    'ㅡㆍㅡ': 'ㅇ',
    'ㆍㅡㅡㆍ': 'ㅈ',
    'ㅡㆍㅡㆍ': 'ㅊ',
    'ㅡㆍㆍㅡ': 'ㅋ',
    'ㅡㅡㆍㆍ': 'ㅌ',
    'ㅡㅡㅡ': 'ㅍ',
    'ㆍㅡㅡㅡ': 'ㅎ',
    'ㆍ': 'ㅏ',
    'ㆍㆍ': 'ㅑ',
    'ㅡ': 'ㅓ',
    'ㆍㆍㆍ': 'ㅕ',
    'ㆍㅡ': 'ㅗ',
    'ㅡㆍ': 'ㅛ',
    'ㆍㆍㆍㆍ': 'ㅜ',
    'ㆍㅡㆍ': 'ㅠ',
    'ㅡㆍㆍ': 'ㅡ',
    'ㆍㆍㅡ': 'ㅣ',
    'ㅡㅡㆍㅡ': 'ㅐ',
    'ㅡㆍㅡㅡ': 'ㅔ'
}


class IME:
    don_time = int(config['setting']['don_time'])  # ㆍ(돈) 시간
    # 자동 조정 비활성화시, 수동 설정 됨. (위험)
    if not config['setting'].getboolean('automatic_time_adjustment'):
        tsu_time = int(config['setting']['tsu_time'])  # ㅡ(쓰) 시간
        morse_gap = int(config['setting']['morse_gap'])
        char_gap = int(config['setting']['char_gap'])
        word_gap = int(config['setting']['word_gap'])
    else:
        tsu_time = don_time * 3  # ㅡ(쓰) 시간
        morse_gap = don_time  # 모스부호(신호)간 간격 <= 이거보다 일찍 입력하면 입력 묵살
        char_gap = don_time * 3
        # -> ^^ <- 글자간 간격. <= morse_gap <= time <= char_gap에 입력이 없으면 글자 종료. 만약 제대로 된 문자가 안 만들어지면 그 문자는 버림.
        word_gap = don_time * 7  # 단어간 간격(이만큼 지나면 ime 초기화. (한영 정보는 유지))
    plusminus = 50  # 입력 오차 범위

    lang = "en"
    start_time = 0  # 키 누른 시간
    last_input_time = 0  # 입력을 끝낸 시간 <= 글자 간격이나 단어 간격, 모스부호간 간격 판단용

    morse_word = [[]]  # 현재 입력된 모스부호 리스트 [[ㆍ,ㆍ,ㆍ], [ㅡ,ㅡ,ㅡ], [ㆍ,ㆍ,ㆍ]] 꼴
    now_char_idx = 0  # 현재 글자 morse_word상 인덱스
    word = ""  # 모스부호간 간격이 지나면 글자 추가
    # n초뒤 실행같은거로 간격을 판단하고 만약 n초 내로 입력이 들어오면 인터럽트 시키기
    interruptable_timer = []
    ignore_key = False  # 모스부호 입력 무시 플래그 <= 신호간 간격내 입력시
    is_key_upped = True  # 키 뗌 확인 플래그
    key_down_type = None

    # callback은 나중에 websocket에서 쓸듯 / signal은 ㆍ, ㅡ 입력될때마다 호출 / ended_char는 글자 완성될때마다 호출
    def __init__(
        self,
        on_signal=(lambda signal: None),
        on_ended_char=(lambda morse, char: None),
        on_ended_word=(lambda word: None),
        on_ignored=(lambda: None)
    ):
        print("모스부호 IME 준비 완료")
        self.on_signal = on_signal
        self.on_ended_char = on_ended_char
        self.on_ended_word = on_ended_word
        self.on_ignored = on_ignored
        if not config['setting'].getboolean('delay'):
            self.morse_gap = 0

    def sync(self):
        pass

    # dontsu은 space로 하기 힘든 분들을 위해 don tsu 입력을 구분해서 할 수 있게
    def key_down(self, dontsu=None):
        if not self.is_key_upped:
            return
        if not self.ignore_key:
            self.start_beep()
        self.is_key_upped = False
        self.key_down_type = dontsu
        input_gap = int(time.time() * 1000) - self.last_input_time
        if input_gap <= self.morse_gap:
            # 신호간 간격 내 입력 됐으니 무시
            self.ignore_key = True
        elif self.morse_gap < input_gap <= self.char_gap or self.char_gap < input_gap <= self.word_gap:
            # 글자 간격 내 입력 됐으니 타이머 인터럽트(이때는 2개)
            # 문자와 단어 간격 내 입력됐으니 타이머 인터럽트{이때는 1개(단어종료 타이머)}
            for t in self.interruptable_timer:
                t.cancel()
            self.interruptable_timer = []
        self.start_time = int(time.time() * 1000)  # 키 누른 시간

    def key_up(self):
        if self.ignore_key:
            self.on_ignored()
            self.ignore_key = False
            self.is_key_upped = True
            return
        end_time = int(time.time() * 1000)  # 키 뗀 시간
        press_time = end_time - self.start_time  # 입력 시간
        # print(f"Pressed time: {press_time}ms")

        # press_time >= self.tsu_time +- self.plusminus
        if self.tsu_time - self.plusminus <= press_time <= self.tsu_time + self.plusminus or self.key_down_type == 'tsu':
            self.morse_word[self.now_char_idx].append('ㅡ')
            self.on_signal('ㅡ')
        # press_time >= self.don_time +- self.plusminus
        elif self.don_time - self.plusminus <= press_time <= self.don_time + self.plusminus or self.key_down_type == 'don':
            self.morse_word[self.now_char_idx].append('ㆍ')
            self.on_signal('ㆍ')

        self.last_input_time = end_time

        # 글자 입력 완료 시키는 타이머
        char_end_timer = threading.Timer(self.char_gap / 1000, self.char_end)
        self.interruptable_timer.append(char_end_timer)
        char_end_timer.start()

        # 단어 입력 완료 시키는 타이머
        word_end_timer = threading.Timer(self.word_gap / 1000, self.word_end)
        self.interruptable_timer.append(word_end_timer)
        word_end_timer.start()
        self.is_key_upped = True
        self.stop_beep()

    def char_end(self):
        morse = ''.join(self.morse_word[self.now_char_idx])
        word_map = en_word_map if self.lang == "en" else ko_word_map  # 언어에 맞는 모스부호 리스트를 가져옴
        if morse in word_map:  # 언어 모스부호
            self.word += word_map[morse]
            self.on_ended_char(morse, word_map[morse])  # event 보내줌
            self.now_char_idx += 1
            self.morse_word.append([])
        elif morse in common_word_map:  # 기호 숫자 등 공통 모스부호
            self.word += common_word_map[morse]
            self.on_ended_char(morse, common_word_map[morse])
            self.now_char_idx += 1
            self.morse_word.append([])
        else:  # 올바르지 않은 모스부호
            self.morse_word[self.now_char_idx] = []  # 현재 글자 모스부호 초기화

    def to_char(self, morse: str) -> str:
        word_map = en_word_map if self.lang == "en" else ko_word_map  # 언어에 맞는 모스부호 리스트를 가져옴
        if morse in word_map:  # 언어 모스부호
            return word_map[morse]
        elif morse in common_word_map:  # 기호 숫자 등 공통 모스부호
            return common_word_map[morse]
        else:
            return ""

    def word_end(self):
        # 단어 종료 시 ime 초기화
        self.on_ended_word(self.word)
        self.morse_word = [[]]
        self.now_char_idx = 0
        self.word = ""
        self.last_input_time = 0
        self.start_time = 0
        for t in self.interruptable_timer:
            t.cancel()
        self.interruptable_timer = []
        self.ignore_key = False
        self.is_key_upped = True
        self.key_down_type = None

    def stop_beep(self):
        if no_sound:
            return
        sd.stop()

    def start_beep(self):
        if no_sound:
            return
        sd.play(*assets["sound"]["beep.wav"], blocksize=1024)
# endregion


def getPixmapedSvg(image_name: str, width: int, height: int) -> QPixmap:
    theme = "dark" if darkdetect.isDark() else "light"  # 다크모드면 글자 하얀거 씀.
    renderer = QSvgRenderer(QByteArray(
        assets["img"][theme][image_name]))  # svg 렌더러

    pixmap = QPixmap(width, height)  # 여기에 svg 박을거임
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)  # pixmap에 svg 그림
    painter.end()

    return pixmap  # 줌.


class SettingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(io.BytesIO(assets["ui"]["setting.ui"]), self)

        self.setGeometry(self.geometry())
        self.setWindowTitle(self.windowTitle())
        self.setStyleSheet(self.styleSheet())
        self.setFont(self.font())
        self.setFixedSize(self.size())

        self.buttonBox.accepted.connect(self.on_accept)  # 확인 버튼(적용 후 닫기)
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Apply
        ).clicked.connect(self.on_apply)  # 적용 버튼
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Reset
        ).clicked.connect(self.reset)  # 리셋 버튼

        self.excluded = config['setting']['exclude_chars'].split(
            '|')  # 제외된 문자 목록
        if self.excluded == ['']:
            self.excluded = []
        en_word_map_keys = list(en_word_map.keys())  # 알파벳 값들 가져오기
        common_word_map_keys = list(common_word_map.keys())  # 숫자/기호 값들 가져오기

        en_checks = []
        for k in en_word_map_keys:
            v = en_word_map[k]
            check = QCheckBox(f"{v} [{k} ]", self)
            en_checks.append(check)
            check.setFont(QFont("Jersey 25", 9))
            self.abc_list.addWidget(check)
            if v in self.excluded:
                check.setChecked(False)
            else:
                check.setChecked(True)

            check.clicked.connect(
                lambda checked, char=v: self.on_ex_check_changed(checked, char)
            )

        common_checks = []
        for k in common_word_map_keys:
            v = common_word_map[k]
            check = QCheckBox(f"{v} [{k}]", self)
            common_checks.append(check)
            self.other_list.addWidget(check)
            if v in self.excluded:
                check.setChecked(False)
            else:
                check.setChecked(True)

            check.clicked.connect(
                lambda checked, char=v: self.on_ex_check_changed(checked, char)
            )

        def on_chr_clicked(checked):
            for check in en_checks:
                check.setChecked(checked)
            if checked:
                self.excluded = list(filter(
                    lambda x: x not in en_word_map.values(), self.excluded
                ))
            else:
                self.excluded += list(en_word_map.values())
            self.excluded = list(set(self.excluded))  # 중복제거

        def on_common_clicked(checked):
            for check in common_checks:
                check.setChecked(checked)
            if checked:
                self.excluded = list(filter(
                    lambda x: x not in common_word_map.values(), self.excluded
                ))
            else:
                self.excluded += list(common_word_map.values())
            self.excluded = list(set(self.excluded))  # 중복제거

        self.dis_chr.clicked.connect(lambda: on_chr_clicked(False))
        self.abl_chr.clicked.connect(lambda: on_chr_clicked(True))

        self.dis_num.clicked.connect(lambda: on_common_clicked(False))
        self.abl_num.clicked.connect(lambda: on_common_clicked(True))

        self.auto_adjust_check.setChecked(
            config['setting'].getboolean('automatic_time_adjustment')
        )
        self.auto_adjust_check.stateChanged.connect(
            self.on_auto_adjust_changed
        )
        self.delay_check.setChecked(
            config['setting'].getboolean('delay')
        )
        self.delay_check.stateChanged.connect(
            self.on_delay_changed
        )

        self.spinners = [
            ('don_time', self.don_spin),
            ('tsu_time', self.tsu_spin),
            ('morse_gap', self.morse_gap_spin),
            ('char_gap', self.char_gap_spin),
            ('word_gap', self.word_gap_spin)
        ]
        self.spinner_enable(not self.auto_adjust_check.isChecked())
        for key, spinner in self.spinners:
            spinner.setValue(int(config['setting'][key]))
            spinner.valueChanged.connect(
                lambda value, key=key, spinner=spinner:
                    self.on_spinner_changed(key, spinner)
            )

    # 스피너(시간같은거) 바뀔때
    def on_spinner_changed(self, key, spinner):
        print(f"{key} changed to {spinner.value()}")
        config['setting'][key] = str(spinner.value())

    def spinner_enable(self, enable: bool):
        for key, spinner in self.spinners[1:]:
            spinner.setEnabled(enable)

    # 문자 제외 체크박스 바뀔때
    def on_ex_check_changed(self, checked, char):
        if not checked:
            self.excluded.append(char)
        else:
            self.excluded.remove(char)

    def on_auto_adjust_changed(self):
        config['setting']['automatic_time_adjustment'] = str(
            self.auto_adjust_check.isChecked()
        ).lower()
        self.spinner_enable(not self.auto_adjust_check.isChecked())

    def on_delay_changed(self):
        config['setting']['delay'] = str(
            self.delay_check.isChecked()
        ).lower()

    def reset(self):
        load_config(reset=True)
        self.accept()
        dlg = SettingDialog(self.parent())
        dlg.exec()

    # 확인
    def on_accept(self):
        self.on_apply()
        self.accept()

    # 적용
    def on_apply(self):
        print("제외된 문자:", self.excluded)
        config['setting']['exclude_chars'] = '|'.join(self.excluded)
        with open("1401_config.ini", 'w') as f:
            config.write(f)
        pass


class RoomDialog(QDialog):
    sig_send_word = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, room_code=""):
        super().__init__(parent)
        loadUi(io.BytesIO(assets["ui"]["room.ui"]), self)

        self.setGeometry(self.geometry())
        self.setWindowTitle(self.windowTitle())
        self.setStyleSheet(self.styleSheet())
        self.setFont(self.font())

        self.ws = QWebSocket()
        self.ws.connected.connect(lambda: self.connected(room_code))
        self.ws.textMessageReceived.connect(self.on_message)
        self.ws.open(QUrl("ws://msk.dimigo.co.kr:8765"))  # 웹소켓 접속하기

        self.now_label_idx = 0
        self.was_my_turn = False
        self.messages: list[QLabel] = []
        self.sig_send_word.connect(self.send_word_message)

        self.ime = IME(
            on_signal=self.on_ime_signal,
            on_ended_char=self.on_ime_ended_char,
            on_ended_word=self.on_ime_ended_word
        )
        self.ime.word_end()

    def connected(self, room_code):
        self.ws.sendTextMessage(json.dumps(  # 방에 접속시키기.
            {"event": "join", "room": room_code}
        ))
        print("웹소켓 연결됨")

    def keyPressEvent(self, event):
        # 얘는 짜증나게 AutoRepeat 이런게 있더라;;
        if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
            self.ime.key_down()
        elif (event.key() == Qt.Key.Key_J) and not event.isAutoRepeat():
            self.ime.key_down(dontsu='tsu')
        elif (event.key() == Qt.Key.Key_D) and not event.isAutoRepeat():
            self.ime.key_down(dontsu='don')
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
            self.ime.key_up()
        elif (event.key() == Qt.Key.Key_J) and not event.isAutoRepeat():
            self.ime.key_up()
        elif (event.key() == Qt.Key.Key_D) and not event.isAutoRepeat():
            self.ime.key_up()
        return super().keyReleaseEvent(event)

    def on_ime_signal(self, signal):
        # 지금 쓰고있는 글자(char)을 문자로 변환.
        if self.was_my_turn == False:  # 저번이 남 차례였으면
            self.now_label_idx += 1  # 내 걸 적기 위해 다음 라벨로 넘기기
            self.was_my_turn = True  # 그리고 내 차례임.
        compl = "".join(self.ime.morse_word[self.ime.now_char_idx])
        self.morse_label.setText(compl)
        self.str_label.setText(
            self.ime.word + self.ime.to_char(compl))  # 지금까지 쓴 단어 + 지금 글자
        self.ws.sendTextMessage(json.dumps(
            {"event": "morse", "message": signal}  # 모스부호 누를 때마다 서버로 전송
        ))

    def on_ime_ended_char(self, morse, char):
        self.morse_label.setText("")  # 글자 하나 완성되면 morse초기화

    def on_ime_ended_word(self, word):
        self.sig_send_word.emit(word)

    def send_word_message(self, word):
        self.ws.sendTextMessage(json.dumps(
            {"event": "word", "word": word}  # 단어 완성되면 서버로 전송
        ))

        self.add_message_word(word)
        self.morse_label.setText("")
        self.str_label.setText("")

    def on_message(self, message):
        data = json.loads(message)
        if data["event"] == "morse":  # 다른사람이 보낸 모스부호
            if self.was_my_turn:  # 저번이 내 차례였으면
                self.now_label_idx += 1  # 다음 라벨로 넘기기
                self.was_my_turn = False  # 그리고 내 차례는 아님.
                # if data["message"] == 'ㆍ':
                #     winsound.Beep(700, 100)  # 비프음 재생
                # else:
                #     winsound.Beep(700, 200)  # 비프음 재생

        if data["event"] == "word":
            self.add_message_word(data["word"])

    def add_message_word(self, message):
        if self.now_label_idx >= len(self.messages):  # 새 라벨이 필요하면
            label = QLabel(self)
            self.scroll_widget.layout().addWidget(label)
            label.setObjectName(f"message_label_{self.now_label_idx}")
            label.setFont(QFont("Jersey 25", 24, QFont.Weight.Bold))
            if self.was_my_turn:
                label.setStyleSheet("color: #eee;")
            else:
                label.setStyleSheet("color: #ff8;")
            self.messages.append(label)
        else:  # 기존 라벨 사용
            label = self.messages[self.now_label_idx]

        label.setText(label.text() + " " + message)
        print("메시지 추가:", message)
        # label.moveCursor(QTextCursor.End)
        # label.ensureCursorVisible()
        scroller = self.scrollArea.verticalScrollBar()
        scroller.setValue(scroller.maximum()+999)

    def closeEvent(self, a0):
        self.ws.close()
        self.now_label_idx = 0
        self.was_my_turn = False
        self.messages = []
        self.ime.word_end()
        return super().closeEvent(a0)


class RoomConnectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(io.BytesIO(assets["ui"]["room_connector.ui"]), self)

        self.setGeometry(self.geometry())
        self.setWindowTitle(self.windowTitle())
        self.setStyleSheet(self.styleSheet())
        self.setFont(self.font())
        self.setFixedSize(self.size())

        self.buttonBox.accepted.connect(self.on_accept)

    def on_accept(self):
        room_code = self.room_id_edit.text()
        print("방 코드:", room_code)
        self.room_code = room_code
        self.accept()


class PlayNote(QLabel):
    def __init__(self, parent=None, char="A", lane=0):
        super().__init__(parent)
        self.setText(char)
        self.setGeometry(200+(100*lane), self.height(), 100, 50)
        bg_color = "#ffa"
        if lane % 2 == 0:
            bg_color = "#aaf"
        text_color = "#000"
        self.setStyleSheet(
            rf"width: 100px; height: 50px; background-color: {bg_color}; border: 2px solid #000; border-radius: 10px; font-size: 24px; font-weight: bold; text-align: center; color: {text_color};"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lower()

    def down(self):
        pass


class PlayDialog(QDialog):
    sig_set_level = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(io.BytesIO(assets["ui"]["play.ui"]), self)

        self.sig_set_level.connect(self.real_update_level)

        self.setGeometry(self.geometry())
        self.setWindowTitle(self.windowTitle())
        self.setStyleSheet(self.styleSheet())
        self.setFont(self.font())
        self.setFixedSize(self.size())

        self.max_life = 5
        self.life = self.max_life
        self.chong_note = 0
        self.notes: list[PlayNote] = []
        self.score = 0
        self.combo = 0
        self.level = 1

        self.ime = IME(
            on_signal=self.on_ime_signal,
            on_ended_char=self.on_ime_ended_char,
            on_ended_word=self.on_ime_ended_word
        )  # ime
        self.ime.word_gap = self.ime.don_time * 4
        self.morse = ""

        self.generate_note()  # 처음에 하나 생성

        self.down_timer = QTimer(self)
        self.down_timer.setInterval(100)  # 100ms마다 노트 내려감
        self.down_timer.timeout.connect(self.on_down_timer)
        self.down_timer.start()

        self.gen_note_timer = QTimer(self)
        self.gen_note_timer.setInterval(4000)  # 4초마다 노트 생성
        self.gen_note_timer.timeout.connect(self.generate_note)
        self.gen_note_timer.start()

        self.dead_line = QLabel(self)
        self.dead_line.setGeometry(0, self.height() - 110, self.width(), 10)
        self.dead_line.setStyleSheet("background-color: red;")
        self.dead_line.raise_()

        # Todo: 점수를 올리고 점수는 단계에 배율. 단계는 점수에 따라 차등.

    def generate_note(self):
        lane = random.randint(0, 3)
        all_morse = list(common_word_map.items()) + list(en_word_map.items())
        all_morse = list(filter(
            lambda item: item[1] not in config['setting']['exclude_chars'], all_morse
        ))
        all_morse = [item[1] for item in all_morse]
        char = random.choice(all_morse)
        note = PlayNote(self, char, lane)
        self.notes.append(note)
        note.show()
        self.chong_note += 1

    def on_down_timer(self):
        for i in range(len(self.notes) - 1, -1, -1):
            note = self.notes[i]
            note.move(note.x(), note.y() + 5)  # 노트 아래로 5픽셀 이동
            if note.y() > self.dead_line.y() - note.height():  # 노트가 데드라인에 닿을 때
                self.notes.pop(i)  # 리스트에서 제거
                note.deleteLater()  # Qt 객체 메모리 해제
                self.life -= 1
                self.heart_label.setText(
                    "❤️" * self.life + "🖤" * (self.max_life - self.life))
                if self.life <= 0:
                    self.on_dead()

    def on_dead(self):
        self.gen_note_timer.stop()
        self.down_timer.stop()
        self.ime.ignore_key = True
        self.override_back = QLabel(self)
        self.override_back.setGeometry(0, 0, self.width(), self.height())
        self.override_back.setStyleSheet("background-color: black;")
        self.override_back.raise_()
        self.override_back.show()
        self.override_back.setFocus()

        self.override_score = QLabel(self)
        self.override_score.setGeometry(0, 0, self.width(), self.height())
        self.override_score.setStyleSheet(
            "color: white; font-size: 48px; font-weight: bold;")
        self.override_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.override_score.setText(
            f"게임 오-버!\n점수: {self.score}/\n최고 점수: {config['play']['high_score']}")
        self.override_score.setFont(QFont("Jersey 25", 48))
        self.override_score.raise_()
        self.override_score.show()
        # 최고 점수 기록 하기
        config['play']['high_score'] = str(max(
            self.score, int(config['play']['high_score'])
        ))
        with open('1401_config.ini', 'w') as configfile:
            config.write(configfile)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
            self.ime.key_down()
        elif (event.key() == Qt.Key.Key_J) and not event.isAutoRepeat():
            self.ime.key_down(dontsu='tsu')
        elif (event.key() == Qt.Key.Key_D) and not event.isAutoRepeat():
            self.ime.key_down(dontsu='don')
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
            self.ime.key_up()
        elif (event.key() == Qt.Key.Key_J) and not event.isAutoRepeat():
            self.ime.key_up()
        elif (event.key() == Qt.Key.Key_D) and not event.isAutoRepeat():
            self.ime.key_up()
        return super().keyReleaseEvent(event)

    def on_ime_signal(self, signal):
        self.morse += signal
        self.morse_label.setText(self.morse)
        self.char_label.setText(self.ime.to_char(self.morse))

    def on_ime_ended_char(self, morse, char):
        pass

    def on_ime_ended_word(self, word):
        self.ime.ignore_key = True
        for note in self.notes:
            if note.text() == word:
                self.combo += 1
                self.add_score(1, level=1, note_y=note.y())
                self.notes.remove(note)  # 리스트에서 제거
                note.deleteLater()  # Qt 객체 메모리 해제
                break
        else:
            self.combo = 0  # 콤보 초기화
            self.combo_label.setText(f"Combo: {self.combo}")
        if self.score >= 1000:
            self.set_level(2)
        if self.score >= 3000:
            self.set_level(3)
        if self.score >= 6000:
            self.set_level(4)
        if self.score >= 10000:
            self.set_level(5)
        self.morse = ""
        self.morse_label.setText("")
        self.char_label.setText("")
        self.ime.ignore_key = False

    def add_score(self, amount=1, level=1, note_y=750):
        jjeonda = 1
        # 얼마나 먼저 해치웠느냐에 따라 가중치 차등 부여
        if 0 <= note_y < 150:
            jjeonda = 100
        elif 150 <= note_y < 300:
            jjeonda = 70
        elif 300 <= note_y < 450:
            jjeonda = 50
        elif 450 <= note_y < 600:
            jjeonda = 30
        elif 600 <= note_y < 750:
            jjeonda = 10
        else:
            jjeonda = 1
        if level == 1:
            jjeonda *= 1
        elif level == 2:
            jjeonda *= 1.4
        elif level == 3:
            jjeonda *= 1.8
        elif level == 4:
            jjeonda *= 2.2
        elif level == 5:
            jjeonda *= 2.5
        jjeonda *= self.combo * 0.5 + 1  # 콤보 배율
        self.score += int(amount * jjeonda)
        self.score_label.setText(f"{self.score}".rjust(6, '0'))
        self.combo_label.setText(f"Combo: {self.combo}")

    def set_level(self, level):
        self.sig_set_level.emit(level)

    def real_update_level(self, level):
        if self.level >= 5 or level <= self.level:
            return
        self.level = level

        # 같은 스레드에서 죽이고 시작하도록 죽이기.
        self.gen_note_timer.stop()
        self.down_timer.stop()

        if self.level == 2:
            self.gen_note_timer.setInterval(3500)
            self.down_timer.setInterval(80)
        elif self.level == 3:
            self.gen_note_timer.setInterval(3000)
            self.down_timer.setInterval(70)
        elif self.level == 4:
            self.gen_note_timer.setInterval(2500)
            self.down_timer.setInterval(60)
        elif self.level == 5:
            self.gen_note_timer.setInterval(2000)
            self.down_timer.setInterval(50)

        self.gen_note_timer.start()
        self.down_timer.start()
        self.level_label.setText(f"Lv {self.level}/5")


class LearnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(io.BytesIO(assets["ui"]["learn.ui"]), self)

        self.setGeometry(self.geometry())
        self.setWindowTitle(self.windowTitle())
        self.setStyleSheet(self.styleSheet())
        self.setFont(self.font())
        self.setFixedSize(self.size())

        self.ime = IME(
            on_signal=self.on_ime_signal,
            on_ended_char=self.on_ime_ended_char,
            on_ended_word=self.on_ime_ended_word
        )  # ime 만듦.
        self.ime.word_gap = self.ime.don_time * 4

        self.correct = QLabel(self)
        self.correct.setGeometry(0, 0, 800, 750)
        correct_pixmap = QPixmap()
        correct_pixmap.loadFromData(QByteArray(assets["img"]["correct.png"]))
        self.correct.setPixmap(
            correct_pixmap.scaled(800, 750))
        self.correct.raise_()

        self.wrong = QLabel(self)
        self.wrong.setGeometry(0, 0, 800, 750)
        wrong_pixmap = QPixmap()
        wrong_pixmap.loadFromData(QByteArray(assets["img"]["wrong.png"]))
        self.wrong.setPixmap(
            wrong_pixmap.scaled(800, 750))
        self.wrong.raise_()
        self.correct.hide()
        self.wrong.hide()

        self.load_new_question()  # 처음에 새거 하나 가져와야함.

    def ox(self, is_o: bool):
        if is_o:
            self.correct.show()
            self.wrong.hide()
        else:
            self.correct.hide()
            self.wrong.show()

    def remove_ox(self):
        self.correct.hide()
        self.wrong.hide()

    def keyPressEvent(self, event):
        # 얘는 짜증나게 AutoRepeat 이런게 있더라;;
        if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
            self.ime.key_down()
        elif (event.key() == Qt.Key.Key_J) and not event.isAutoRepeat():
            self.ime.key_down(dontsu='tsu')
        elif (event.key() == Qt.Key.Key_D) and not event.isAutoRepeat():
            self.ime.key_down(dontsu='don')
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
            self.ime.key_up()
        elif (event.key() == Qt.Key.Key_J) and not event.isAutoRepeat():
            self.ime.key_up()
        elif (event.key() == Qt.Key.Key_D) and not event.isAutoRepeat():
            self.ime.key_up()
        return super().keyReleaseEvent(event)

    def on_ime_signal(self, signal):
        # print(f"Signal: {signal}")
        template = "<style>body {margin: 0;}brown {color: #643;}red {color: #ff0000;}</style>"
        additional = []
        for i, s in enumerate(self.ime.morse_word[self.ime.now_char_idx]):
            if i >= len(self.current_question[0]):
                additional.append(f"<red>{s}</red>")
                continue
            elif s == self.current_question[0][i]:
                additional.append(f"<brown>{s}</brown>")
            else:
                additional.append(f"<red>{s}</red>")

        self.me_morse.setText(template + ''.join(additional))
        # print(self.ime.morse_word[self.ime.now_char_idx])

    def on_ime_ended_char(self, morse, char):
        # 여기서 합불 판독
        # time sleep하면 ended_word 상쇄 될듯?
        # 가장 위로 오버레이 해서 도티낳기 게임처럼 O X를 화면 앞 크게 띄울까
        pass

    # 어려웠던 점 1. 틀렸는데 틀린걸 알 수 없음. ime_ended_char에서는 정상적인 모스부호만 호출해주기 때문에 없는걸 써서 틀린건 알 수 없음.
    # 그래서 ime_ended_word의 시간을 char급으로 줄이고 word에서 판독하게 함. word는 틀리든 맞든 전체 결과를 출력하는 것이기 때문.
    def on_ime_ended_word(self, word):
        self.ime.ignore_key = True
        if word == self.current_question[1]:
            self.ox(True)
            time.sleep(0.5)
            self.remove_ox()
            self.load_new_question()
        else:
            self.ox(False)
            time.sleep(0.5)
            self.remove_ox()
            self.me_morse.setText("")
        self.ime.ignore_key = False
        pass

    def load_new_question(self):
        all_morse = list(common_word_map.items()) + list(en_word_map.items())
        all_morse = list(filter(
            lambda item: item[1] not in config['setting']['exclude_chars'], all_morse
        ))
        morse, char = random.choice(all_morse)
        self.current_question = (morse, char)
        self.target_char.setText(char)
        self.target_morse.setText(morse)
        self.me_morse.setText("")


class MemorizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(io.BytesIO(assets["ui"]["memorize.ui"]), self)

        self.setLayout(self.layout())
        self.setWindowTitle(self.windowTitle())
        self.resize(self.size())
        self.setFont(self.font())

        self.NumberImage.setPixmap(
            getPixmapedSvg("숫자기호.svg", self.width()*3, self.height()*3)
            .scaled(self.width(), self.height())
        )  # 숫자기호 사진 출력
        self.EngImage.setPixmap(
            getPixmapedSvg("알파벳.svg", self.width()*3, self.height()*3)
            .scaled(self.width(), self.height())
        )  # 알파벳 사진 출력
        self.HangulImage.setPixmap(
            getPixmapedSvg("한글.svg", self.width()*3, self.height()*3)
            .scaled(self.width(), self.height())
        )  # 한글 사진 출력

        self.buttonBox.accepted.connect(self.on_ok_clicked)

    def on_ok_clicked(self):
        self.accept()


class PortalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(io.BytesIO(assets["ui"]["portal.ui"]), self)
        self.setCentralWidget(self.centralWidget())
        self.setGeometry(self.geometry())
        self.setWindowTitle(self.windowTitle())
        self.setStyleSheet(self.styleSheet())
        self.setFont(self.font())
        # jersey_font = QFont("Jersey 25", 48)
        # self.ui.label.setFont(jersey_font)
        self.btnMemorize.clicked.disconnect()
        self.btnLearn.clicked.disconnect()
        self.btn_play.clicked.disconnect()
        self.btn_together.clicked.disconnect()
        self.btn_setting.clicked.disconnect()

        self.btnMemorize.clicked.connect(self.on_btnMemorize_clicked)
        self.btnLearn.clicked.connect(self.on_btnLearn_clicked)
        self.btn_play.clicked.connect(self.on_btn_play_clicked)
        self.btn_together.clicked.connect(self.on_btn_together_clicked)
        self.btn_setting.clicked.connect(self.on_btn_setting_clicked)

    def on_btnMemorize_clicked(self):
        dialog = MemorizeDialog(self)
        dialog.show()

    def on_btnLearn_clicked(self):
        learn_widget = LearnDialog(self)
        learn_widget.ime.word_end()  # dialog 다시 실행될 때 초기화
        learn_widget.exec()

    def on_btn_play_clicked(self):
        play_dialog = PlayDialog(self)
        # play_dialog.ime.word_end()  # dialog 다시 실행될 때 초기화
        play_dialog.exec()

    def on_btn_together_clicked(self):
        room_connector = RoomConnectorDialog(self)
        if room_connector.exec() == QDialog.DialogCode.Accepted:
            room = RoomDialog(self, room_connector.room_code)
            room.exec()

    def on_btn_setting_clicked(self):
        setting_dialog = SettingDialog(self)
        setting_dialog.exec()


# 일화 2: 멀티 기능을 클라이언트가 서버 노릇도 하고 클라이언트 노릇도 하게 만들려 했는데,
# 코드가 복잡해질 것 같아 서버로 따로 뺌 ㅎㅎ
if __name__ == "__main__":
    app = QApplication([])

    id = QFontDatabase.addApplicationFontFromData(
        QByteArray(assets["font"]["Jersey25-Regular.ttf"]))
    jersey = QFontDatabase.applicationFontFamilies(id)[0]
    # app.setFont(QFont(jersey, 10))

    window = PortalWindow()
    window.show()
    app.exec()
