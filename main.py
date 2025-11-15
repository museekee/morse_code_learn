# region 패키지나 assets 다운로드
try:
    import os
    from PySide6.QtCore import QFile
    from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QWidget
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtGui import QPixmap, QPainter, QFont, QFontDatabase
    from PySide6.QtCore import Qt
    from PySide6.QtSvg import QSvgRenderer
    import darkdetect
    import random
except ImportError:
    import pip
    import os

    print("Requirements are not installed. Installing...")
    pip.main(["install", "PySide6", "darkdetect"])  # pyside6, darkdetect 설치

    if os.system(f"python \"{__file__}\"") == 0:
        exit(0)
    elif os.system(f"py \"{__file__}\"") == 0:
        exit(0)
    elif os.system(f"python3 \"{__file__}\"") == 0:
        exit(0)
    else:
        print("Failed to start application. Please run it manually.")
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
    don_time = 100  # ㆍ(돈) 시간
    tsu_time = don_time * 3  # ㅡ(쓰) 시간
    plusminus = 100  # 입력 오차 범위
    morse_gap = don_time  # 모스부호(신호)간 간격 <= 이거보다 일찍 입력하면 입력 묵살
    char_gap = don_time * 3
    # -> ^^ <- 글자간 간격. <= morse_gap <= time <= char_gap에 입력이 없으면 글자 종료. 만약 제대로 된 문자가 안 만들어지면 그 문자는 버림.
    word_gap = don_time * 7  # 단어간 간격(이만큼 지나면 ime 초기화. (한영 정보는 유지))

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
        on_ignored=(lambda: None),
        no_delay=False
    ):
        print("모스부호 IME 준비 완료")
        self.on_signal = on_signal
        self.on_ended_char = on_ended_char
        self.on_ended_word = on_ended_word
        self.on_ignored = on_ignored
        if no_delay:
            self.morse_gap = 0

    def sync(self):
        pass

    # dontsu은 space로 하기 힘든 분들을 위해 don tsu 입력을 구분해서 할 수 있게
    def key_down(self, dontsu=None):
        if not self.is_key_upped:
            return
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

    def char_end(self):
        morse = ''.join(self.morse_word[self.now_char_idx])
        word_map = en_word_map if self.lang == "en" else ko_word_map
        if morse in word_map:
            self.word += word_map[morse]
            self.on_ended_char(morse, word_map[morse])
            self.now_char_idx += 1
            self.morse_word.append([])
        elif morse in common_word_map:
            self.word += common_word_map[morse]
            self.on_ended_char(morse, common_word_map[morse])
            self.now_char_idx += 1
            self.morse_word.append([])
        else:  # 올바르지 않은 모스부호
            self.morse_word[self.now_char_idx] = []  # 현재 글자 모스부호 초기화

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
# endregion


def getPixmap(image_name: str) -> QPixmap:
    theme = "dark" if darkdetect.isDark() else "light"  # 다크모드 그거
    image_path = f"./assets/img/{theme}/{image_name}"
    return QPixmap(image_path)


def getPixmapedSvg(image_name: str, width: int, height: int) -> QPixmap:
    theme = "dark" if darkdetect.isDark() else "light"  # 다크모드면 글자 하얀거 씀.
    image_path = f"./assets/img/{theme}/{image_name}"  # svg 경로 만들기
    renderer = QSvgRenderer(image_path)  # svg 렌더러

    pixmap = QPixmap(width, height)  # 여기에 svg 박을거임
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)  # pixmap에 svg 그림
    painter.end()

    return pixmap  # 줌.


class MemorizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        self.ui = loader.load("./assets/memorize.ui", self)

        self.setLayout(self.ui.layout())
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())
        self.setFont(self.ui.font())

        self.ui.NumberImage.setPixmap(
            getPixmapedSvg("숫자기호.svg", self.width()*3, self.height()*3)
            .scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        )  # 숫자기호 사진 출력
        self.ui.EngImage.setPixmap(
            getPixmapedSvg("알파벳.svg", self.width()*3, self.height()*3)
            .scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        )  # 알파벳 사진 출력
        self.ui.HangulImage.setPixmap(
            getPixmapedSvg("한글.svg", self.width()*3, self.height()*3)
            .scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        )  # 한글 사진 출력

        self.ui.buttonBox.accepted.connect(self.on_ok_clicked)

    def on_ok_clicked(self):
        self.accept()


class LearnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        self.ui = loader.load("./assets/learn.ui", self)

        self.setGeometry(self.ui.geometry())
        self.setWindowTitle(self.ui.windowTitle())
        self.setStyleSheet(self.ui.styleSheet())
        self.setFont(self.ui.font())
        self.setFixedSize(self.ui.size())

        self.ime = IME(
            on_signal=self.on_ime_signal,
            on_ended_char=self.on_ime_ended_char,
            on_ended_word=self.on_ime_ended_word,
            no_delay=True
        )  # ime 만듦.
        self.load_new_question()  # 처음에 새거 하나 가져와야함.

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():  # 얘는 짜증나게 AutoRepeat 이런게 있더라;;
            self.ime.key_down()
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.ime.key_up()
        return super().keyReleaseEvent(event)

    def on_ime_signal(self, signal):
        print(f"Signal: {signal}")
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

        self.ui.me_morse.setText(template + ''.join(additional))
        # print(self.ime.morse_word[self.ime.now_char_idx])

    def on_ime_ended_char(self, morse, char):
        # 여기서 합불 판독
        # time sleep하면 ended_word 상쇄 될듯?
        # 가장 위로 오버레이 해서 도티낳기 게임처럼 O X를 화면 앞 크게 띄울까
        if char == self.current_question[1]:
            self.ui.me_morse.setText(" ⭕ ")
            time.sleep(0.5)
            self.ui.me_morse.setText("")
            self.load_new_question()
        else:
            self.ui.me_morse.setText(" ❌ ")
            time.sleep(0.5)
            self.ui.me_morse.setText("")

    def on_ime_ended_word(self, word):
        # print(f"Ended Word: {word}")
        pass

    def load_new_question(self):
        all_morse = list(common_word_map.items()) + list(en_word_map.items())
        morse, char = random.choice(all_morse)
        self.current_question = (morse, char)
        self.ui.target_char.setText(char)
        self.ui.target_morse.setText(morse)


class PortalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.ui = loader.load("./assets/portal.ui")
        self.setCentralWidget(self.ui.centralWidget())
        self.setGeometry(self.ui.geometry())
        self.setWindowTitle(self.ui.windowTitle())
        self.setStyleSheet(self.ui.styleSheet())
        self.setFont(self.ui.font())
        # jersey_font = QFont("Jersey 25", 48)
        # self.ui.label.setFont(jersey_font)

        self.ui.btnMemorize.clicked.connect(self.on_btnMemorize_clicked)
        self.ui.btnLearn.clicked.connect(self.on_btnLearn_clicked)

    def on_btnMemorize_clicked(self):
        dialog = MemorizeDialog(self)
        dialog.show()

    def on_btnLearn_clicked(self):
        learn_widget = LearnDialog(self)
        learn_widget.exec()


if __name__ == "__main__":
    app = QApplication([])

    font_path = os.path.join(os.path.dirname(
        __file__), "assets", "font", "Jersey25-Regular.ttf")
    id = QFontDatabase.addApplicationFont(font_path)
    jersey = QFontDatabase.applicationFontFamilies(id)[0]
    # app.setFont(QFont(jersey, 10))

    window = PortalWindow()
    window.show()
    app.exec()
