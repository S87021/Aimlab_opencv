import cv2
import numpy as np
import pygetwindow as gw
import time
import win32api
import win32con
import mss

# 定义目标颜色范围
# 定义颜色范围的下界和上界，用于后续的图像处理
#Red
lower_bound = np.array([130,0,0])
upper_bound = np.array([255, 40, 40])

def main():
    # 目标窗口的标题
    target_window_title = "aimlab_tb"  
    # 获取所有匹配目标标题的窗口
    windows = gw.getWindowsWithTitle(target_window_title)
    
    # 如果没有找到任何窗口，则输出信息并退出函数
    if not windows:
        print(f"未找到标题为 '{target_window_title}' 的窗口")
        return
    
    # 获取第一个匹配的窗口并激活它
    target_window = windows[0]
    target_window.activate()
    
    # 使用mss工具进行屏幕截图
    with mss.mss() as sct:
        while True:
            # 获取窗口的位置和大小
            left, top, width, height = target_window.left, target_window.top, target_window.width, target_window.height
            # 定义截图的区域
            monitors = {'left': left, 'top': top, 'width': width, 'height': height}
            # 捕获截图
            screenshot = sct.grab(monitors)           
            # 将截图转换为numpy数组
            frame = np.array(screenshot)         
            # 转换图像的颜色空间
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 根据颜色范围创建掩码
            mask = cv2.inRange(frame, lower_bound, upper_bound)
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 初始化最近的轮廓和最小的距离
            closest_contour = None
            min_distance = float('inf')
            # 获取当前鼠标位置
            current_x, current_y = win32api.GetCursorPos() 
            
            # 遍历所有轮廓
            for contour in contours:
                # 获取轮廓的边界框
                x, y, w, h = cv2.boundingRect(contour)
                # 在图像上绘制轮廓的边界框
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 计算轮廓中心点的屏幕位置
                center_x = x + w // 2
                center_y = y + h // 2
                screen_x = left + center_x
                screen_y = top + center_y
                # 计算轮廓中心点与鼠标位置的距离
                distance = np.sqrt((screen_x - current_x) ** 2 + (screen_y - current_y) ** 2)
                # 如果当前距离小于最小距离，则更新最小距离和最近的轮廓
                if distance < min_distance:
                    min_distance = distance
                    closest_contour = contour
            
            # 如果找到了最近的轮廓
            if closest_contour is not None:
                # 获取最近轮廓的边界框
                x, y, w, h = cv2.boundingRect(closest_contour)
                center_x = x + w // 2
                center_y = y + h // 2
                screen_x = left + center_x
                screen_y = top + center_y
                # 计算相对于鼠标位置的移动距离
                relative_x = screen_x - current_x
                relative_y = screen_y - current_y

                # 移动鼠标
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, relative_x, relative_y, 0, 0)
                # 如果鼠标在轮廓内部，则点击鼠标
                if x <= current_x - left <= x + w and y <= current_y - top <= y + h:           
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # 显示处理后的图像和掩码
            cv2.imshow('frame',frame)
            cv2.imshow('mask', mask)
            
            # 如果按下'Q'键，则退出循环
            if cv2.waitKey(1) & 0xFF == ord('Q'):
                break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
