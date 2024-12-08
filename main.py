import time
import asyncio
from datetime import datetime, timedelta, timezone
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

# 작업 스케줄 사용 여부
times = True

# 클릭 시간 목록 (러시아 모스크바 시간)
click_times = ["2:00:00", "3:00:00", "5:00:00", "6:30:00", "13:30:00", "14:30:00", "18:00:00", "20:00:00"]

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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)

# 스크린샷 캡처 함수
def capture_screenshot():
    try:
        driver.save_screenshot(screenshot_path)
    except Exception as e:
        print(f"스크린샷 생성 오류: {e}")

# 버튼 클릭 함수
def click_button():
    try:
        time.sleep(10)  # 페이지 로딩 대기
        element = driver.find_element(By.TAG_NAME, "body")  # 버튼 요소 찾기
        action = ActionChains(driver)
        action.move_to_element_with_offset(element, 0, -65).click().perform()
        print("클릭 성공!")
    except Exception as e:
        print(f"클릭 오류: {e}")

# 특정 시간까지 대기 후 클릭
async def wait_and_click(target_time: str):
    while True:
        now_utc = datetime.now(timezone.utc)
        now_msk = now_utc.astimezone(timezone(timedelta(hours=3)))  # 모스크바 시간

        target_time_obj = datetime.strptime(target_time, "%H:%M:%S").time()
        target_datetime = datetime.combine(now_msk.date(), target_time_obj, tzinfo=timezone(timedelta(hours=3)))

        if now_msk >= target_datetime:
            target_datetime += timedelta(days=1)

        wait_time = (target_datetime - now_msk).total_seconds()
        print(f"{target_time} (모스크바 시간)까지 대기: {wait_time:.2f}초")

        await asyncio.sleep(wait_time)
        click_button()

# 모든 클릭 스케줄링
async def schedule_all_clicks():
    is_between_times(click_times)
    tasks = [asyncio.create_task(wait_and_click(time)) for time in click_times]
    await asyncio.gather(*tasks)

# 현재 시간이 클릭 시간인지 확인
def is_between_times(click_times):
    click_times = [datetime.strptime(t, "%H:%M:%S").time() for t in click_times]
    now = datetime.now().time()

    for i in range(0, len(click_times), 2):
        start, end = click_times[i], click_times[i + 1]
        if start <= now <= end:
            click_button()
            break

# Telegram 명령어 처리기 - /screen
@dp.message_handler(commands=['screen'])
async def send_screenshot(message: types.Message):
    capture_screenshot()
    await message.answer("스크린샷 생성 중...")
    await message.answer_document(open(screenshot_path, 'rb'))

# 메인 실행 함수
async def main():
    if times:
        asyncio.create_task(schedule_all_clicks())  
    else:
        click_button()
    print("봇 실행 중...")
    await dp.start_polling()

# 프로그램 시작
if __name__ == "__main__":
    asyncio.run(main())
