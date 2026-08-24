# 설치 및 실행 가이드

## Windows에서 실행

### 방법 1: Python으로 실행 (추천)

1. **Python 설치**
   - [python.org](https://www.python.org/downloads/)에서 Python 3.7 이상 다운로드
   - 설치 시 "Add Python to PATH" 체크

2. **저장소 클론**
   ```bash
   git clone https://github.com/malrang265-jpg/webp-converter.git
   cd webp-converter
   ```

3. **라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **프로그램 실행**
   ```bash
   python main.py
   ```

### 방법 2: 실행 파일 사용

1. **GitHub Releases에서 다운로드**
   - [Releases](https://github.com/malrang265-jpg/webp-converter/releases)에서 `WebP-to-MP4-Converter.exe` 다운로드

2. **프로그램 실행**
   - 다운로드한 `.exe` 파일을 더블클릭하면 실행
   - 추가 설치 불필요

## macOS에서 실행

1. **Homebrew를 이용한 Python 설치**
   ```bash
   brew install python@3.10
   ```

2. **저장소 클론**
   ```bash
   git clone https://github.com/malrang265-jpg/webp-converter.git
   cd webp-converter
   ```

3. **라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **프로그램 실행**
   ```bash
   python main.py
   ```

## Linux에서 실행

1. **Python 및 의존성 설치**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-tk
   ```

2. **저장소 클론**
   ```bash
   git clone https://github.com/malrang265-jpg/webp-converter.git
   cd webp-converter
   ```

3. **라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **프로그램 실행**
   ```bash
   python main.py
   ```

## 문제 해결

### "ModuleNotFoundError: No module named 'cv2'" 오류
```bash
pip install --upgrade opencv-python
```

### "No module named 'tkinter'" 오류

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

### OpenCV 설치 실패 시
```bash
pip install --upgrade pip
pip install --force-reinstall opencv-python
```

### 실행 파일(.exe) 생성하기

PyInstaller를 사용하여 직접 실행 파일 생성 가능:

```bash
# PyInstaller 설치
pip install pyinstaller

# 실행 파일 빌드
pyinstaller --onefile --windowed --name=WebP-to-MP4-Converter main.py

# 생성된 파일은 dist/ 폴더에 위치
```

## 필수 라이브러리

- **opencv-python**: 동영상 생성
- **Pillow**: 이미지 처리
- **numpy**: 수치 계산

모두 `requirements.txt`에 포함되어 있습니다.
