import time
import asyncio
import os
import json
from datetime import datetime, timezone, timedelta
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from aiogram import Bot, Dispatcher, types

# 파일 경로 설정
BOT_LIST_FILE = "bot_list.json"
RUNNING_BOTS = {}

# 봇 목록 불러오기
def load_bot_list():
    if os.path.exists(BOT_LIST_FILE):
        with open(BOT_LIST_FILE, "r") as file:
            return json.load(file)
    return {}

# 봇 목록 저장하기
def save_bot_list(bot_list):
    with open(BOT_LIST_FILE, "w") as file:
        json.dump(bot_list, file, indent=4)

# 봇 등록 함수
def register_new_bot():
    TOKEN = input("Telegram Bot Token을 입력하세요: ").strip()
    url = input("웹사이트 URL을 입력하세요: ").strip()
    bot_name = input("봇의 이름을 입력하세요: ").strip()

    bot_list = load_bot_list()
    bot_list[bot_name] = {"token": TOKEN, "url": url}
    save_bot_list(bot_list)
    print(f"✅ {bot_name} 봇이 등록되었습니다!")

# Selenium 설정
def setup_driver(url):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver

# 스크린샷 캡처 함수
def capture_screenshot(driver, screenshot_path):
    try:
        driver.save_screenshot(screenshot_path)
        print("✅ 스크린샷 저장 완료!")
    except Exception as e:
        print(f"❌ 스크린샷 오류: {e}")

# 버튼 클릭 함수
def click_button(driver):
    try:
        time.sleep(10)  # 페이지 로딩 대기
        element = driver.find_element(By.TAG_NAME, "body")  # 버튼 요소 찾기
        action = ActionChains(driver)
        action.move_to_element_with_offset(element, 0, -65).click().perform()
        print("✅ 버튼 클릭 성공!")
    except Exception as e:
        print(f"❌ 클릭 오류: {e}")

# Telegram 명령어 처리기 - /screen
async def send_screenshot(message: types.Message, bot, driver, screenshot_path):
    capture_screenshot(driver, screenshot_path)
    await bot.send_message(message.chat.id, "📸 스크린샷 생성 중...")
    await bot.send_document(message.chat.id, open(screenshot_path, 'rb'))

async def start_bot(bot_name, token, url):
    screenshot_path = f"{bot_name}_screenshot.png"
    driver = setup_driver(url)

    bot = Bot(token=token)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['screen'])
    async def handle_screen(message: types.Message):
        await send_screenshot(message, bot, driver, screenshot_path)

    click_button(driver)
    print(f"✅ {bot_name} 봇 실행 중...")
    RUNNING_BOTS[bot_name] = True
    await dp.start_polling()

async def stop_bot(bot_name):
    print(f"❌ {bot_name} 봇이 중지되었습니다.")
    RUNNING_BOTS.pop(bot_name, None)

async def main():
    bot_list = load_bot_list()

    if not bot_list:
        print("⚠️ 등록된 봇이 없습니다.")
        if input("새 봇을 추가하시겠습니까? (Yes/No): ").strip().lower() == "yes":
            register_new_bot()
        else:
            print("프로그램을 종료합니다.")
            return

    while True:
        print("📋 등록된 봇 목록:")
        for idx, bot_name in enumerate(bot_list, start=1):
            status_icon = "🟢" if RUNNING_BOTS.get(bot_name) else "🔴"
            print(f"{idx}. {bot_name} {status_icon}")

        bot_choice = input("봇을 켜거나 끌 이름을 입력하세요 (종료: exit): ").strip()
        if bot_choice.lower() == "exit":
            print("프로그램을 종료합니다.")
            break

        if bot_choice in bot_list:
            if RUNNING_BOTS.get(bot_choice):
                await stop_bot(bot_choice)
            else:
                token = bot_list[bot_choice]['token']
                url = bot_list[bot_choice]['url']
                await start_bot(bot_choice, token, url)
        else:
            print("❌ 등록된 봇이 아닙니다.")

if __name__ == "__main__":
    asyncio.run(main())
