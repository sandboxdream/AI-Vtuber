import pyautogui
import time

class game1:
    # 模拟按键按下后释放，传入字符串数组
    def simulate_key_press(self, keys, re=1):
        num = 0
        # 模拟按下释放按键
        for key in keys:
            # 限制触发的次数
            if num >= re:
                break
            pyautogui.keyDown(key)
            time.sleep(0.1)
            pyautogui.keyUp(key)

            num = num + 1
            

    # 解析字符串数组，根据字符串第一位判断是否需要转换按键后，按压按键
    def parse_keys_and_simulate_key_press(self, keys, re=1):
        # 删除数组中非 w a s d 1 2 3 的其他字符串
        def remove_needless(keys):
            for i in range(len(keys)):
                if keys[i] not in ['1', '2']:
                    keys.pop(i)
            return keys

        keys = remove_needless(keys)

        # 遍历数组
        for i in range(len(keys)):
            if keys[i] == '1':
                keys[i] = 'w'
            elif keys[i] == '2':
                keys[i] = 'up'

        self.simulate_key_press(keys, re)