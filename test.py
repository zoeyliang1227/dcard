from selenium import webdriver
import time
import json

# 加载 .side 文件
def load_side(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 执行 .side 文件
def execute_side(driver, side_data):
    tests = side_data.get('tests', [])
    for test in tests:
        commands = test.get('commands', [])
        for command in commands:
            cmd = command.get('command', '')
            target = command.get('target', '')
            value = command.get('value', '')

            if cmd == 'open':
                driver.get(target)
            elif cmd == 'click':
                element = driver.find_element_by_css_selector(target)
                element.click()
            # 添加更多的命令处理逻辑...