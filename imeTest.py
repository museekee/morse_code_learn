import keyboard
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
    don_time = 200  # ㆍ(돈) 시간
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
    def __init__(self, on_signal=(lambda signal: None), on_ended_char=(lambda morse, char: None), on_ended_word=(lambda word: None), on_ignored=(lambda: None)):
        print("모스부호 IME 준비 완료")
        self.on_signal = on_signal
        self.on_ended_char = on_ended_char
        self.on_ended_word = on_ended_word
        self.on_ignored = on_ignored

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


ime = IME(lambda signal: print(
    f"신호 입력: {signal}"), lambda morse, char: print(f"글자 완성: {morse} -> {char}"), lambda word: print(f"단어 완성: {word}"), lambda: print(f"입력 무시됨"))
while 1:
    event = keyboard.read_event()

    if event.name == 'esc':
        break

    if event.event_type == keyboard.KEY_DOWN:
        if event.scan_code == 32:
            ime.key_down('don')
        elif event.scan_code == 36:
            ime.key_down('tsu')
        else:
            ime.key_down()
        # print(f"키 '{event.name}'을(를) 눌렀습니다.")
    elif event.event_type == keyboard.KEY_UP:
        ime.key_up()
        # print(f"키 '{event.name}'을(를) 뗐습니다.")
