import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import threading
import os
import cv2
from PIL import Image
import numpy as np
from datetime import datetime
from pathlib import Path
import gc  # 메모리 관리


class WebPToMP4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("WebP to MP4 Converter")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.webp_files = []
        self.failed_files = []
        self.is_converting = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # 상단 프레임
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # 폴더 선택
        ttk.Button(top_frame, text="📁 WebP 폴더 선택", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        self.folder_label = ttk.Label(top_frame, text="선택된 폴더: 없음", foreground="blue")
        self.folder_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 설정 프레임
        settings_frame = ttk.LabelFrame(self.root, text="변환 설정", padding=10)
        settings_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # FPS 설정
        fps_frame = ttk.Frame(settings_frame)
        fps_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fps_frame, text="재생 속도 (FPS):", width=15).pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=24)
        ttk.Spinbox(fps_frame, from_=1, to=60, textvariable=self.fps_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(fps_frame, text="(원본 설정: 24)", foreground="gray").pack(side=tk.LEFT)
        
        # 반복 횟수 설정
        repeat_frame = ttk.Frame(settings_frame)
        repeat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(repeat_frame, text="WebP 반복 횟수:", width=15).pack(side=tk.LEFT)
        self.repeat_var = tk.IntVar(value=1)
        ttk.Spinbox(repeat_frame, from_=1, to=100, textvariable=self.repeat_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(repeat_frame, text="(각 이미지를 몇 프레임씩 반복할지)", foreground="gray").pack(side=tk.LEFT)
        
        # 출력 파일명
        output_frame = ttk.Frame(settings_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="출력 파일명:", width=15).pack(side=tk.LEFT)
        self.output_var = tk.StringVar(value="output.mp4")
        ttk.Entry(output_frame, textvariable=self.output_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 파일 목록 프레임
        list_frame = ttk.LabelFrame(self.root, text="WebP 파일 목록", padding=10)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 스크롤바가 있는 리스트박스
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=8)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Button(button_frame, text="🔄 새로고침", command=self.refresh_file_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 선택 항목 제거", command=self.remove_selected_file).pack(side=tk.LEFT, padx=5)
        self.convert_btn = ttk.Button(button_frame, text="▶️ 변환 시작", command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=5)
        
        # 진행률 프레임
        progress_frame = ttk.LabelFrame(self.root, text="진행 상황", padding=10)
        progress_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="진행률: 0%")
        self.progress_label.pack(fill=tk.X, pady=5)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(progress_frame, text="로그", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="WebP 파일이 있는 폴더를 선택하세요")
        if folder_path:
            self.folder_path = folder_path
            self.folder_label.config(text=f"선택된 폴더: {folder_path}")
            self.refresh_file_list()
    
    def refresh_file_list(self):
        if not hasattr(self, 'folder_path'):
            messagebox.showwarning("경고", "먼저 폴더를 선택하세요")
            return
        
        self.file_listbox.delete(0, tk.END)
        self.webp_files = []
        
        try:
            for file in sorted(os.listdir(self.folder_path)):
                if file.lower().endswith('.webp'):
                    full_path = os.path.join(self.folder_path, file)
                    self.webp_files.append(full_path)
                    self.file_listbox.insert(tk.END, file)
            
            self.log(f"✓ {len(self.webp_files)}개의 WebP 파일을 찾았습니다")
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽을 수 없습니다: {str(e)}")
            self.log(f"✗ 오류: {str(e)}")
    
    def remove_selected_file(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            removed_file = self.webp_files.pop(index)
            self.file_listbox.delete(index)
            self.log(f"제거됨: {os.path.basename(removed_file)}")
    
    def log(self, message):
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_conversion(self):
        if not self.webp_files:
            messagebox.showwarning("경고", "변환할 WebP 파일이 없습니다")
            return
        
        if self.is_converting:
            messagebox.showwarning("경고", "이미 변환 중입니다")
            return
        
        output_filename = self.output_var.get()
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = os.path.join(self.folder_path, output_filename)
        
        # 변환 스레드 시작
        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.failed_files = []
        
        thread = threading.Thread(
            target=self.convert_webp_to_mp4,
            args=(self.webp_files, output_path, self.fps_var.get(), self.repeat_var.get())
        )
        thread.daemon = True
        thread.start()
    
    def extract_all_frames_from_webp(self, webp_file):
        """WebP 파일의 모든 프레임 추출 (Animated WebP 지원)"""
        frames = []
        img = None
        try:
            img = Image.open(webp_file)
            img.seek(0)  # 첫 프레임으로 이동
            
            width = img.width
            height = img.height
            frame_index = 0
            
            # Animated WebP인 경우 모든 프레임 추출
            while True:
                try:
                    # 현재 프레임을 RGB로 변환
                    frame = img.convert('RGB')
                    frame_np = np.array(frame)
                    frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                    frames.append(frame_bgr)
                    
                    # 다음 프레임으로 이동
                    frame_index += 1
                    img.seek(frame_index)
                except EOFError:
                    # 모든 프레임을 다 읽었을 때 발생
                    break
            
            # 프레임이 없으면 정적 이미지로 처리
            if not frames:
                img.seek(0)
                frame = img.convert('RGB')
                frame_np = np.array(frame)
                frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                frames.append(frame_bgr)
            
            return frames, width, height
        
        except Exception as e:
            raise Exception(f"프레임 추출 실패: {str(e)}")
        finally:
            # 파일 닫기 (중요!)
            if img is not None:
                img.close()
    
    def resize_frame_with_aspect_ratio(self, frame, target_width, target_height):
        """종횡비를 유지하면서 프레임 리사이징 (패딩 추가)"""
        current_height, current_width = frame.shape[:2]
        
        # 이미 목표 해상도와 같으면 그대로 반환
        if current_width == target_width and current_height == target_height:
            return frame
        
        # 종횡비 계산
        aspect_ratio = current_width / current_height
        target_aspect = target_width / target_height
        
        if aspect_ratio > target_aspect:
            # 원본이 더 넓은 경우 (가로가 더 길다)
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            # 원본이 더 좁은 경우 (세로가 더 길다)
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        
        # 리사이징
        resized = cv2.resize(frame, (new_width, new_height))
        
        # 패딩 추가 (검정색)
        pad_top = (target_height - new_height) // 2
        pad_bottom = target_height - new_height - pad_top
        pad_left = (target_width - new_width) // 2
        pad_right = target_width - new_width - pad_left
        
        padded = cv2.copyMakeBorder(
            resized,
            pad_top, pad_bottom, pad_left, pad_right,
            cv2.BORDER_CONSTANT,
            value=(0, 0, 0)  # 검정색 패딩
        )
        
        return padded
    
    def convert_webp_to_mp4(self, webp_files, output_path, fps, repeat_count):
        try:
            self.log("━" * 50)
            self.log(f"변환 시작 | 파일 수: {len(webp_files)} | FPS: {fps} | 반복: {repeat_count}x")
            self.log("━" * 50)
            
            # 첫 번째 패스: 기준 해상도 결정 (메모리 효율적 방식)
            target_width = None
            target_height = None
            file_info = []  # 파일 정보만 저장 (프레임은 보관 안 함)
            
            for idx, webp_file in enumerate(webp_files):
                try:
                    progress = (idx / len(webp_files)) * 30  # 0-30%
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"진행률: {progress:.1f}% ({idx + 1}/{len(webp_files)}) - 정보 수집 중")
                    
                    filename = os.path.basename(webp_file)
                    self.log(f"정보 수집... [{idx + 1}/{len(webp_files)}] {filename}")
                    
                    # 🔑 프레임을 추출하지 말고 해상도 정보만 가져오기
                    img = Image.open(webp_file)
                    width = img.width
                    height = img.height
                    
                    # 프레임 개수 세기 (프레임 데이터는 로드하지 않음)
                    frame_count = 0
                    frame_index = 0
                    while True:
                        try:
                            img.seek(frame_index)
                            frame_count += 1
                            frame_index += 1
                        except EOFError:
                            break
                    
                    if frame_count == 0:
                        frame_count = 1
                    
                    img.close()  # 즉시 닫기
                    
                    # 첫 파일의 해상도를 기준으로 설정
                    if target_width is None:
                        target_width = width
                        target_height = height
                    
                    file_info.append({
                        'path': webp_file,
                        'filename': filename,
                        'width': width,
                        'height': height,
                        'frame_count': frame_count
                    })
                    
                    self.log(f"✓ {filename} - {width}x{height} ({frame_count}개 프레임)")
                    
                except Exception as e:
                    self.failed_files.append((os.path.basename(webp_file), str(e)))
                    self.log(f"✗ 실패: {os.path.basename(webp_file)} - {str(e)}")
                    continue
            
            if not file_info:
                messagebox.showerror("오류", "변환할 수 있는 이미지가 없습니다")
                self.log("✗ 오류: 변환할 수 있는 이미지가 없습니다")
                return
            
            # MP4 저장
            self.log("━" * 50)
            self.log(f"MP4 저장 중... (모든 프레임을 {target_width}x{target_height}로 변환, 종횡비 유지)")
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
            
            if not out.isOpened():
                raise Exception("VideoWriter를 열 수 없습니다")
            
            # 총 프레임 개수 계산
            total_frames = sum(info['frame_count'] * repeat_count for info in file_info)
            written_frames = 0
            
            # 🔑 두 번째 패스: 파일별로 프레임을 실시간으로 처리
            for file_idx, info in enumerate(file_info):
                try:
                    # 프레임 추출 (이번에만 로드)
                    webp_frames, width, height, filename = self.extract_all_frames_from_webp(info['path']), info['width'], info['height'], info['filename']
                    
                    for frame in webp_frames:
                        # 종횡비를 유지하면서 리사이징 (패딩 추가)
                        if width != target_width or height != target_height:
                            frame = self.resize_frame_with_aspect_ratio(frame, target_width, target_height)
                        
                        # 반복 횟수만큼 쓰기
                        for _ in range(repeat_count):
                            success = out.write(frame)
                            if success:
                                written_frames += 1
                            
                            # 진행률 업데이트 (30-100%)
                            progress = 30 + (written_frames / total_frames) * 70
                            self.progress_var.set(min(progress, 100))
                            self.progress_label.config(text=f"진행률: {progress:.1f}% ({written_frames}/{total_frames})")
                            self.log_text.see(tk.END)
                            self.root.update()
                    
                    # 프레임 메모리 해제
                    webp_frames = None
                    gc.collect()  # 가비지 컬렉션 강제 실행
                    
                except Exception as e:
                    self.log(f"✗ 프레임 처리 실패: {info['filename']} - {str(e)}")
                    continue
            
            out.release()
            
            self.progress_var.set(100)
            self.progress_label.config(text="진행률: 100%")
            
            self.log("━" * 50)
            self.log(f"✓ 변환 완료!")
            self.log(f"📹 출력 파일: {output_path}")
            self.log(f"📊 총 프레임: {written_frames}")
            self.log(f"⏱️ 동영상 길이: {written_frames / fps:.2f}초")
            self.log(f"📐 해상도: {target_width}x{target_height}")
            self.log(f"⚡ FPS: {fps}")
            
            # 실패 파일 저장
            if self.failed_files:
                self.save_failed_files(output_path)
                self.log(f"⚠️ 실패한 파일: {len(self.failed_files)}개")
                self.log(f"📝 실패 목록: {os.path.basename(output_path).replace('.mp4', '_failed.txt')}")
            else:
                self.log("✓ 모든 파일 변환 성공!")
            
            self.log("━" * 50)
            messagebox.showinfo("완료", f"MP4 변환이 완료되었습니다!\n\n위치: {output_path}")
            
        except Exception as e:
            messagebox.showerror("오류", f"변환 중 오류가 발생했습니다: {str(e)}")
            self.log(f"✗ 오류: {str(e)}")
        finally:
            self.is_converting = False
            self.convert_btn.config(state=tk.NORMAL)
            gc.collect()  # 마지막 메모리 정리
    
    def save_failed_files(self, output_path):
        if not self.failed_files:
            return
        
        failed_file_path = output_path.replace('.mp4', '_failed.txt')
        
        try:
            with open(failed_file_path, 'w', encoding='utf-8') as f:
                f.write("WebP to MP4 변환 실패 파일 목록\n")
                f.write("=" * 50 + "\n")
                f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for filename, error in self.failed_files:
                    f.write(f"파일: {filename}\n")
                    f.write(f"오류: {error}\n")
                    f.write("-" * 50 + "\n")
                
                f.write(f"\n합계: {len(self.failed_files)}개 파일 실패\n")
            
            self.log(f"✓ 실패 목록 저장: {failed_file_path}")
        except Exception as e:
            self.log(f"✗ 실패 목록 저장 오류: {str(e)}")


def main():
    root = tk.Tk()
    app = WebPToMP4Converter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
