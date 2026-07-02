import os
from dotenv import load_dotenv

# 현재 경로와 시도하는 경로 출력
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, "dataset", "config", ".env"))

print(f"찾고 있는 파일 경로: {env_path}")

# 파일 존재 여부 확인
if os.path.exists(env_path):
    print("파일을 찾았습니다.")
    load_dotenv(dotenv_path=env_path)
    print("로드된 APP_KEY:", os.getenv("KIS_APP_KEY"))
else:
    print("파일을 찾을 수 없습니다. 경로를 확인하세요.")