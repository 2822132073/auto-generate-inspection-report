import os
import requests
import json
import time
from pathlib import Path

def send_inspection_files_to_api(base_directory, api_url, api_token=None):
    """
    遍历指定目录，将所有JSON文件通过POST请求发送到指定API。

    Args:
        base_directory (str): 包含项目文件夹的根目录路径。
        api_url (str): API的完整URL，例如 'http://your-server.com/api/v1/inspections'。
        api_token (str, optional): 用于API认证的Bearer Token。
    """
    # 遍历 base_directory 下的所有子目录（即项目目录）
    for project_dir_path in Path(base_directory).iterdir():
        if project_dir_path.is_dir():
            print(f"\n正在处理项目目录: {project_dir_path.name}")
            
            # 遍历项目目录下的所有 .json 文件
            json_files = list(project_dir_path.glob("*.json"))
            total_files = len(json_files)
            print(f"  找到 {total_files} 个JSON文件。")

            for i, json_file_path in enumerate(json_files, start=1):
                print(f"    [{i}/{total_files}] 正在发送文件: {json_file_path.name}")

                try:
                    # 读取JSON文件内容
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        # 尝试解析为JSON对象，确保是有效JSON
                        json_data = json.loads(file_content)

                    # 准备请求头
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    # 如果提供了API Token，则添加到请求头
                    if api_token:
                        headers['Authorization'] = f'Bearer {api_token}'

                    # 发送POST请求
                    response = requests.post(
                        url=api_url,
                        headers=headers,
                        json=json_data # 使用 json 参数，requests 会自动序列化并设置正确的 Content-Type
                    )

                    # 检查响应状态码
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"      成功: {response.status_code} - {json_file_path.name}")
                    else:
                        print(f"      失败: {response.status_code} - {json_file_path.name}")
                        print(f"      响应内容: {response.text[:200]}...") # 打印部分响应内容以便调试

                except FileNotFoundError:
                    print(f"      错误: 文件未找到 - {json_file_path}")
                except json.JSONDecodeError as e:
                    print(f"      错误: JSON解析失败 - {json_file_path}, 错误: {e}")
                except requests.exceptions.RequestException as e:
                    print(f"      错误: 网络请求失败 - {json_file_path}, 错误: {e}")
                except Exception as e:
                    print(f"      错误: 发生未知错误 - {json_file_path}, 错误: {e}")

            print(f"  项目 {project_dir_path.name} 处理完成。\n")
            # 可选：在处理完一个项目后稍作停顿，避免过于频繁的请求
            # time.sleep(0.1)

if __name__ == "__main__":
    # --- 请在此处修改配置 ---
    # 1. 指定包含项目文件夹的根目录
    INSPECTION_DATA_DIR = "/tmp/inspection_data" # 请修改为您的实际目录路径

    # 2. 指定API的URL
    API_ENDPOINT = "http://localhost:8000/api/v1/inspections" # 请修改为您的实际API地址

    # 3. (可选) 如果API需要认证，请提供Bearer Token
    # AUTH_TOKEN = "your_api_token_here" 
    AUTH_TOKEN = None # 如果不需要认证，请保持为 None
    # --- 配置结束 ---

    print(f"开始将 {INSPECTION_DATA_DIR} 目录下的JSON文件发送到 {API_ENDPOINT}")
    if AUTH_TOKEN:
        print("使用了API Token进行认证。")
    else:
        print("未配置API Token，将进行无认证请求。")

    send_inspection_files_to_api(INSPECTION_DATA_DIR, API_ENDPOINT, AUTH_TOKEN)

    print("\n所有文件发送任务已完成。")
