#!/usr/bin/env python3
"""
终端截图生成器
使用 Playwright 将 JSON 中的命令执行记录渲染成终端截图
"""

import html
import json
import sys
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from utils.logger import get_logger
from config import SCREENSHOT_MAX_LINE_LENGTH

logger = get_logger('utils.screenshot_generator')


def parse_ps1(ps1_template, env):
    """
    解析 PS1 提示符模板
    支持常见的 bash PS1 转义序列和条件表达式
    """
    import re
    
    prompt = ps1_template
    
    # 1. 移除非打印字符序列 \[...\]
    # 这些序列用于设置终端标题等，不应该显示在提示符中
    # 格式：\[\e]0;...\a\] 用于设置终端标题
    # 使用非贪婪匹配来匹配整个序列
    # 先处理特殊的终端标题序列 \[\e]0;...\a\]
    prompt = re.sub(r'\\\[\\e\]0;.*?\\a\\\]', '', prompt)
    # 然后处理其他非打印字符序列 \[...\]
    prompt = re.sub(r'\\\[.*?\\\]', '', prompt)
    
    # 2. 处理 bash 条件表达式 ${var:+value} 或 ${var:-value}
    # ${debian_chroot:+($debian_chroot)} - 如果 debian_chroot 存在，显示 ($debian_chroot)
    def replace_bash_conditional(match):
        expr = match.group(0)
        # 处理 ${var:+value} 格式（包括 ${var:+(value)} 和 ${var:+value}）
        if ':+' in expr:
            # 匹配 ${var:+(value)} 格式
            var_match = re.search(r'\$\{([^:]+):\+\(([^)]+)\)\}', expr)
            if var_match:
                var_name = var_match.group(1)
                value_expr = var_match.group(2)
                if env.get(var_name):
                    # 处理 value_expr 中的变量引用（如 $debian_chroot 或 debian_chroot）
                    # 如果 value_expr 是 $var_name 或 var_name，则使用变量的值
                    if value_expr == f'${var_name}' or value_expr == f'${{{var_name}}}' or value_expr == var_name:
                        return f'({env.get(var_name, "")})'
                    else:
                        # 尝试解析 value_expr 中的变量引用
                        # 如果 value_expr 包含 ${var} 或 $var，替换为变量值
                        resolved_value = value_expr
                        var_ref_match = re.search(r'\$\{?([^}]+)\}?', value_expr)
                        if var_ref_match:
                            ref_var_name = var_ref_match.group(1)
                            if ref_var_name in env:
                                resolved_value = env.get(ref_var_name, '')
                        return f'({resolved_value})'
                else:
                    return ''
            # 匹配 ${var:+value} 格式（无括号）
            var_match = re.search(r'\$\{([^:]+):\+([^}]+)\}', expr)
            if var_match:
                var_name = var_match.group(1)
                value = var_match.group(2)
                if env.get(var_name):
                    return value
                else:
                    return ''
        # 处理 ${var:-value} 格式
        elif ':-' in expr:
            var_match = re.search(r'\$\{([^:]+):-([^}]+)\}', expr)
            if var_match:
                var_name = var_match.group(1)
                default_value = var_match.group(2)
                return env.get(var_name, default_value)
        return ''
    
    prompt = re.sub(r'\$\{[^}]+\}', replace_bash_conditional, prompt)
    
    # 3. 替换转义序列
    # \u -> 用户名
    prompt = prompt.replace('\\u', env.get('USER', 'user'))
    
    # \h -> 主机名
    prompt = prompt.replace('\\h', env.get('HOSTNAME', 'localhost'))
    
    # \w -> 完整路径（支持 ~ 缩写）
    pwd = env.get('PWD', '/')
    home = env.get('HOME')
    # root 用户默认 HOME 为 /root
    if not home and env.get('USER') == 'root':
        home = '/root'
    if not home:
        home = '/'
    if pwd.startswith(home) and home != '/':
        pwd_display = '~' + pwd[len(home):]
    else:
        pwd_display = pwd
    prompt = prompt.replace('\\w', pwd_display)
    
    # \W -> 当前目录名（从完整路径提取）
    dirname = Path(pwd).name if pwd != '/' else '/'
    prompt = prompt.replace('\\W', dirname)
    
    # \$ -> $ 或 #（根据用户是否为 root）
    user = env.get('USER', '')
    dollar_sign = '#' if user == 'root' else '$'
    prompt = prompt.replace('\\$', dollar_sign)
    
    # \e -> ESC 字符（通常用于颜色代码，已移除）
    prompt = prompt.replace('\\e', '')
    
    # \a -> 响铃字符（BEL，不显示）
    prompt = prompt.replace('\\a', '')
    
    # 清理多余的空格
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    
    return prompt


def escape_html(text):
    """转义 HTML 特殊字符"""
    return html.escape(text, quote=True)


def wrap_text(text, max_length=SCREENSHOT_MAX_LINE_LENGTH):
    """
    将超长文本按指定字符数换行

    Args:
        text: 原始文本
        max_length: 每行最大字符数

    Returns:
        str: 处理后的文本，超长部分会换行
    """
    if not text:
        return text

    lines = []
    for line in text.split('\n'):
        while len(line) > max_length:
            lines.append(line[:max_length])
            line = line[max_length:]
        lines.append(line)

    return '\n'.join(lines)


def load_font_as_base64(font_path):
    """将字体文件转换为 base64 编码"""
    font_file = Path(font_path)
    if not font_file.exists():
        raise FileNotFoundError(f"字体文件不存在: {font_path}")
    
    with open(font_file, 'rb') as f:
        font_data = f.read()
        font_base64 = base64.b64encode(font_data).decode('utf-8')
        return font_base64


def get_css_styles(font_base64):
    """生成 CSS 样式"""
    css_parts = []
    
    # 添加字体定义
    if font_base64:
        css_parts.append(f'''
        @font-face {{
            font-family: 'OperatorMono';
            src: url('data:font/otf;base64,{font_base64}') format('opentype');
            font-weight: 500;
            font-style: normal;
            font-display: swap;
        }}
        ''')
    
    css_parts.append('''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        html, body {
            height: auto;
            min-height: 100%;
        }
        body {
            background-color: #000000;
            color: #ffffff;
            font-family: 'OperatorMono', 'Courier New', 'Monaco', 'Consolas', 'Menlo', monospace;
            font-size: 16px;
            line-height: 0.5;
            letter-spacing: 0;
            padding: 0;
            margin: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        .terminal {
            background-color: #000000;
            color: #ffffff;
            padding: 1px;
            white-space: pre;
            word-wrap: break-word;
            font-family: 'OperatorMono', 'Courier New', 'Monaco', 'Consolas', 'Menlo', monospace;
            line-height: 0.5;
            width: fit-content;
        }
        .prompt {
            color: #00ff00;
        }
        .command {
            color: #ffffff;
        }
        .output {
            color: #ffffff;
            white-space: pre;
        }
        .error {
            color: #ff0000;
        }
        .line {
            margin: 0;
            padding: 0;
            height: 1.0em;
            line-height: 1.0em;
            display: block;
        }
    ''')
    return '\n'.join(css_parts)


def generate_single_command_html(env, command, output, return_code, font_base64):
    """为单个命令生成 HTML 页面"""
    # 解析 PS1 提示符
    ps1 = env.get('PS1', '[\\u@\\h \\W]\\$ ')
    prompt = parse_ps1(ps1, env)
    
    # 构建 HTML
    html_parts = ['<!DOCTYPE html>']
    html_parts.append('<html lang="zh-CN">')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append('<title>Terminal Screenshot</title>')
    html_parts.append('<style>')
    html_parts.append(get_css_styles(font_base64))
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append('<div class="terminal">')
    
    # 提示符行（确保提示符和命令之间有一个空格）
    prompt_escaped = escape_html(prompt)
    full_prompt_line = f"{prompt} {command}"
    if len(full_prompt_line) > SCREENSHOT_MAX_LINE_LENGTH:
        # 命令行超长，需要换行
        wrapped_command = wrap_text(command, SCREENSHOT_MAX_LINE_LENGTH)
        cmd_lines = wrapped_command.split('\n')
        for i, cmd_line in enumerate(cmd_lines):
            if i == 0:
                html_parts.append(f'<div class="line"><span class="prompt">{prompt_escaped}</span> <span class="command">{escape_html(cmd_line)}</span></div>')
            else:
                html_parts.append(f'<div class="line"><span class="command">{escape_html(cmd_line)}</span></div>')
    else:
        html_parts.append(f'<div class="line"><span class="prompt">{prompt_escaped}</span> <span class="command">{escape_html(command)}</span></div>')
    
    # 输出行（return_code 为 1 时不显示输出）
    if output and return_code != 1:
        output_lines = output.split('\n')
        for line in output_lines:
            # 对每行输出进行长度限制
            wrapped_lines = wrap_text(line, SCREENSHOT_MAX_LINE_LENGTH).split('\n')
            for wrapped_line in wrapped_lines:
                html_parts.append(f'<div class="line"><span class="output">{escape_html(wrapped_line)}</span></div>')
    
    # 如果返回码非 0，显示错误信息（已禁用）
    # if return_code != 0:
    #     html_parts.append(f'<div class="line"><span class="error">[返回码: {return_code}]</span></div>')
    html_parts.append('</div>')
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    return '\n'.join(html_parts)


def sanitize_filename(filename):
    """清理文件名，移除不安全的字符"""
    # 移除或替换不安全的字符
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ', '&', ';', '|', '(', ')', '[', ']', '{', '}']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    # 限制文件名长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def generate_screenshot_bytes(env, command, output, return_code, font_file='OperatorMono-Medium.otf', scale_factor=3):
    """
    生成终端截图并返回字节流
    
    Args:
        env: 环境变量字典
        command: 命令字符串
        output: 命令输出字符串
        return_code: 返回码
        font_file: 字体文件名，默认为 'OperatorMono-Medium.otf'
        scale_factor: 设备像素比，默认 3
    
    Returns:
        bytes: PNG 图片的字节流
    
    Raises:
        FileNotFoundError: 如果字体文件不存在
    """
    from io import BytesIO
    
    # 获取字体文件路径（相对于脚本目录）
    script_dir = Path(__file__).parent
    font_path = script_dir / font_file
    
    # 验证字体文件是否存在
    if not font_path.exists():
        raise FileNotFoundError(f"字体文件不存在: {font_file}")
    
    # 加载字体文件并转换为 base64
    font_base64 = load_font_as_base64(str(font_path))
    
    # 生成单个命令的 HTML
    html_content = generate_single_command_html(env, command, output, return_code, font_base64)
    
    # 使用 Playwright 渲染并截图
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        
        # 创建 context 并设置设备像素比
        context = browser.new_context(
            device_scale_factor=scale_factor,
            viewport={"width": 1600, "height": 100}
        )
        page = context.new_page()
        
        # 加载 HTML 内容
        page.set_content(html_content)
        
        # 等待内容渲染和字体加载
        page.wait_for_timeout(500)
        
        # 等待页面内容完全加载
        page.wait_for_load_state('networkidle')
        
        # 获取页面实际内容尺寸
        content_size = page.evaluate("""
            () => {
                const terminal = document.querySelector('.terminal');
                if (terminal) {
                    return {
                        width: terminal.scrollWidth,
                        height: terminal.scrollHeight
                    };
                }
                const body = document.body;
                const html = document.documentElement;
                return {
                    width: Math.max(
                        body.scrollWidth, body.offsetWidth,
                        html.clientWidth, html.scrollWidth, html.offsetWidth
                    ),
                    height: Math.max(
                        body.scrollHeight, body.offsetHeight,
                        html.clientHeight, html.scrollHeight, html.offsetHeight
                    )
                };
            }
        """)
        
        # 根据实际内容尺寸调整视口（添加2px边距用于padding）
        viewport_width = content_size['width'] + 2  # 1px padding * 2
        viewport_height = content_size['height'] + 2  # 1px padding * 2
        
        page.set_viewport_size({
            "width": viewport_width,
            "height": viewport_height
        })
        
        # 重新等待内容渲染
        page.wait_for_timeout(200)
        
        # 截图到内存（返回字节流）
        screenshot_bytes = page.screenshot(
            full_page=True,
            type='png'
        )
        
        # 关闭浏览器
        browser.close()
    
    return screenshot_bytes


def generate_screenshot(json_file='test.json', output_dir='output', font_file='OperatorMono-Medium.otf'):
    """为每个命令生成终端截图"""
    # 读取 JSON 文件
    json_path = Path(json_file)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON 文件不存在: {json_file}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    env = data.get('data', {}).get('env', {})
    commands = data.get('data', {}).get('commands', {})
    
    # 获取字体文件路径（相对于脚本目录）
    script_dir = Path(__file__).parent
    font_path = script_dir / font_file
    
    # 加载字体文件并转换为 base64
    font_base64 = None
    try:
        font_base64 = load_font_as_base64(str(font_path))
    except FileNotFoundError:
        logger.warning(f"字体文件 {font_path} 不存在，使用默认字体")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 使用 Playwright 渲染并截图
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        
        # 创建 context 并设置设备像素比（提高分辨率）
        # device_scale_factor=2 表示 2x 分辨率（Retina 显示效果）
        context = browser.new_context(
            device_scale_factor=3,  # 2倍分辨率，可根据需要调整为 3 或更高
            viewport={"width": 1600, "height": 100}
        )
        page = context.new_page()
        
        # 为每个命令生成截图
        command_index = 1
        for cmd_key, cmd_data in commands.items():
            command = cmd_data.get('command', '')
            output = cmd_data.get('output', '')
            return_code = cmd_data.get('return_code', 0)
            
            # 生成单个命令的 HTML
            html_content = generate_single_command_html(env, command, output, return_code, font_base64)
            
            # 生成文件名（使用索引和清理后的命令名）
            safe_command = sanitize_filename(command)
            if not safe_command:
                safe_command = f"command_{command_index}"
            output_filename = f"{command_index:02d}_{safe_command}.png"
            output_file = output_path / output_filename
            
            # 加载 HTML 内容
            page.set_content(html_content)
            
            # 等待内容渲染和字体加载
            page.wait_for_timeout(500)
            
            # 等待页面内容完全加载
            page.wait_for_load_state('networkidle')
            
            # 获取页面实际内容尺寸
            content_size = page.evaluate("""
                () => {
                    const terminal = document.querySelector('.terminal');
                    if (terminal) {
                        return {
                            width: terminal.scrollWidth,
                            height: terminal.scrollHeight
                        };
                    }
                    const body = document.body;
                    const html = document.documentElement;
                    return {
                        width: Math.max(
                            body.scrollWidth, body.offsetWidth,
                            html.clientWidth, html.scrollWidth, html.offsetWidth
                        ),
                        height: Math.max(
                            body.scrollHeight, body.offsetHeight,
                            html.clientHeight, html.scrollHeight, html.offsetHeight
                        )
                    };
                }
            """)
            
            # 根据实际内容尺寸调整视口（添加2px边距用于padding）
            # 注意：由于 device_scale_factor=2，实际截图分辨率会是视口尺寸的 2 倍
            viewport_width = content_size['width'] + 2  # 1px padding * 2
            viewport_height = content_size['height'] + 2  # 1px padding * 2
            
            page.set_viewport_size({
                "width": viewport_width,
                "height": viewport_height
            })
            
            # 重新等待内容渲染
            page.wait_for_timeout(200)
            
            # 截图（使用 full_page=True 自动截取整个页面内容）
            page.screenshot(
                path=str(output_file),
                full_page=True,
                # type="jpeg",
                # quality=100
            )
            
            # 获取实际截图尺寸（由于 device_scale_factor=2，实际尺寸是视口的 2 倍）
            actual_width = viewport_width * 2
            actual_height = viewport_height * 2
            logger.debug(f"终端截图已保存到: {output_file} (视口: {viewport_width}x{viewport_height}, 实际分辨率: {actual_width}x{actual_height})")
            command_index += 1

        # 关闭浏览器
        browser.close()

    logger.info(f"所有截图已生成，共 {command_index - 1} 个文件，保存在目录: {output_dir}")


if __name__ == '__main__':
    # 支持命令行参数
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'test.json'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    font_file = sys.argv[3] if len(sys.argv) > 3 else 'OperatorMono-Medium.otf'
    
    try:
        generate_screenshot(json_file, output_dir, font_file)
    except Exception as e:
        logger.error(f"截图生成失败: {e}")
        sys.exit(1)

