import time
import asyncio
from datetime import datetime, timezone, timedelta
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from aiogram import Bot, Dispatcher, types

# 사용자 입력 받기
TOKEN = input("Telegram Bot Token을 입력하세요: ").strip()
url = input("웹사이트 URL을 입력하세요: ").strip()

# Telegram Bot 초기화
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Selenium 설정
screenshot_path = "screenshot.png"
options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)


# 스크린샷 캡처 함수
def capture_screenshot():
    try:
        driver.save_screenshot(screenshot_path)
        print("✅ 스크린샷 저장 완료!")
    except Exception as e:
        print(f"❌ 스크린샷 오류: {e}")


# 버튼 클릭 함수
def click_button():
    try:
        time.sleep(10)  # 페이지 로딩 대기
        element = driver.find_element(By.TAG_NAME, "body")  # 버튼 요소 찾기
        action = ActionChains(driver)
        action.move_to_element_with_offset(element, 0, -65).click().perform()
        print("✅ 버튼 클릭 성공!")
    except Exception as e:
        print(f"❌ 클릭 오류: {e}")


# Telegram 명령어 처리기 - /screen
@dp.message_handler(commands=['screen'])
async def send_screenshot(message: types.Message):
    capture_screenshot()
    await message.answer("📸 스크린샷 생성 중...")
    await message.answer_document(open(screenshot_path, 'rb'))


# 메인 실행 함수
async def main():
    # 버튼 즉시 클릭
    click_button()
    print("✅ 작업 실행 완료!")

    # Telegram 봇 시작
    print("🤖 봇 실행 중...")
    await dp.start_polling()


# 프로그램 시작
if __name__ == "__main__":
    asyncio.run(main())
