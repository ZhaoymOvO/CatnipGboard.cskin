#!/usr/bin/env /opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
"""
Hamster / YuanShu Keyboard Skin Framework Generator & Packager.
Gboard-inspired layout with 2-layer symbol panels and dual numeric keypads.
Implements layout.txt specification.
"""

import os
import sys
import json
import zlib
import struct
import zipfile
import argparse
from pathlib import Path


def dump_yaml(data, indent=0):
    """
    Format a Python dict/list structure into clean, readable YAML string.
    """
    lines = []
    prefix = '  ' * indent
    if isinstance(data, dict):
        for key, value in data.items():
            k_str = str(key)
            if any(c in k_str for c in ':#{}[]|,&*?->!%@`"\'\\() ') or k_str == '':
                escaped_k = k_str.replace('\\', '\\\\').replace('"', '\\"')
                k_repr = f'"{escaped_k}"'
            else:
                k_repr = k_str

            if isinstance(value, dict):
                lines.append(f"{prefix}{k_repr}:")
                lines.append(dump_yaml(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{k_repr}:")
                lines.append(dump_yaml(value, indent + 1))
            elif isinstance(value, bool):
                lines.append(f"{prefix}{k_repr}: {'true' if value else 'false'}")
            elif isinstance(value, (int, float)):
                lines.append(f"{prefix}{k_repr}: {value}")
            elif value is None:
                lines.append(f"{prefix}{k_repr}: null")
            else:
                val_str = str(value)
                if any(c in val_str for c in ':#{}[]|,&*?->!%@`"\'\\()') or val_str == '' or val_str.isdigit():
                    escaped = val_str.replace('\\', '\\\\').replace('"', '\\"')
                    lines.append(f'{prefix}{k_repr}: "{escaped}"')
                else:
                    lines.append(f"{prefix}{k_repr}: {val_str}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                first_key = True
                for k, v in item.items():
                    k_str = str(k)
                    if any(c in k_str for c in ':#{}[]|,&*?->!%@`"\'\\() ') or k_str == '':
                        escaped_k = k_str.replace('\\', '\\\\').replace('"', '\\"')
                        k_repr = f'"{escaped_k}"'
                    else:
                        k_repr = k_str

                    if first_key:
                        if isinstance(v, (dict, list)):
                            lines.append(f"{prefix}- {k_repr}:")
                            lines.append(dump_yaml(v, indent + 2))
                        else:
                            val_str = str(v)
                            if any(c in val_str for c in ':#{}[]|,&*?->!%@`"\'\\()') or val_str == '':
                                escaped = val_str.replace('\\', '\\\\').replace('"', '\\"')
                                lines.append(f'{prefix}- {k_repr}: "{escaped}"')
                            else:
                                lines.append(f"{prefix}- {k_repr}: {val_str}")
                        first_key = False
                    else:
                        sub_prefix = prefix + '  '
                        if isinstance(v, (dict, list)):
                            lines.append(f"{sub_prefix}{k_repr}:")
                            lines.append(dump_yaml(v, indent + 2))
                        else:
                            val_str = str(v)
                            if any(c in val_str for c in ':#{}[]|,&*?->!%@`"\'\\()') or val_str == '':
                                escaped = val_str.replace('\\', '\\\\').replace('"', '\\"')
                                lines.append(f'{sub_prefix}{k_repr}: "{escaped}"')
                            else:
                                lines.append(f"{sub_prefix}{k_repr}: {val_str}")
            else:
                val_str = str(item)
                if any(c in val_str for c in ':#{}[]|,&*?->!%@`"\'\\()') or val_str == '':
                    escaped = val_str.replace('\\', '\\\\').replace('"', '\\"')
                    lines.append(f'{prefix}- "{escaped}"')
                else:
                    lines.append(f"{prefix}- {val_str}")
    return '\n'.join(lines)


def create_demo_png(file_path: Path):
    """
    Generate a simple valid PNG file as demo.png using standard library.
    """
    width, height = 320, 180
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)
        for x in range(width):
            r = int(245 - 20 * (x / width))
            g = int(245 - 15 * (y / height))
            b = 250
            raw_data.extend([r, g, b])

    def chunk(tag, data):
        return (struct.pack("!I", len(data)) +
                tag +
                data +
                struct.pack("!I", zlib.crc32(tag + data) & 0xffffffff))

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0)))
    compressed = zlib.compress(bytes(raw_data), 9)
    png.extend(chunk(b"IDAT", compressed))
    png.extend(chunk(b"IEND", b""))

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(png)


def normalize_hex_color(val: str) -> str:
    """
    Normalize color string into valid Hamster #RRGGBB or #RRGGBBAA format.
    Supports CSS-style shorthands such as:
      - #RGB   -> #RRGGBB  (e.g. #FFF -> #FFFFFF)
      - #RGBA  -> #RRGGBBAA (e.g. #FFF6 -> #FFFFFF66)
      - Plain hex without leading '#'
    """
    if not isinstance(val, str):
        return val
    s = val.strip().lstrip('#')
    if len(s) == 3:  # RGB -> RRGGBB
        s = ''.join([c * 2 for c in s])
    elif len(s) == 4:  # RGBA -> RRGGBBAA (e.g. FFF6 -> FFFFFF66)
        s = ''.join([c * 2 for c in s])
    elif len(s) not in (6, 8):
        return val
    return f"#{s.upper()}"


def get_base_styles(theme: str):
    """
    Return buttonStyle definitions for light or dark theme.
    Every style has mandatory buttonStyleType.
    """
    is_dark = (theme == 'dark')

    # Color definitions (Supports shorthand like #FFF, #FFF6, as well as 6/8-digit hex)
    btn_normal_bg = normalize_hex_color("#fff2" if is_dark else "#fffa")
    btn_normal_hi = normalize_hex_color("#fff1" if is_dark else "#fff2")
    btn_func_bg = normalize_hex_color("#fff4" if is_dark else "#fff8")
    btn_func_hi = normalize_hex_color("#fff1" if is_dark else "#fff2")
    btn_accent_bg = normalize_hex_color("#6cfc" if is_dark else "#6cfc")
    btn_accent_hi = normalize_hex_color("#fff2" if is_dark else "#fff2")

    fg_normal = normalize_hex_color("#FFFFFF" if is_dark else "#202124")
    fg_accent = normalize_hex_color("#FFFFFF")
    fg_hint = normalize_hex_color("#A0A0A5" if is_dark else "#70757A")

    # Candidate colors
    cand_text = normalize_hex_color("#FFFFFF" if is_dark else "#202124")
    cand_pref_text = normalize_hex_color("#39c5bb" if is_dark else "#39c5bb")
    cand_hint = normalize_hex_color("#A0A0A5" if is_dark else "#70757A")
    cand_hi_bg = normalize_hex_color("#3A3A3C" if is_dark else "#CFD8DC")

    cand_style = {
        'insets': {'top': 3, 'bottom': 3, 'left': 6, 'right': 6},
        'candidateStateButtonStyle': 'candidateStateButtonStyle',
        'highlightBackgroundColor': cand_hi_bg,
        'preferredIndexColor': cand_pref_text,
        'preferredTextColor': cand_pref_text,
        'preferredCommentColor': cand_hint,
        'indexColor': cand_hint,
        'textColor': cand_text,
        'commentColor': cand_hint,
        'indexFontSize': 11,
        'textFontSize': 18,
        'commentFontSize': 11,
    }

    vert_cand_style = {
        'insets': {'top': 8, 'bottom': 8, 'left': 8, 'right': 8},
        'backgroundInsets': {'top': 8, 'bottom': 8, 'left': 8, 'right': 8},
        'cornerRadius': 8,
        'highlightBackgroundColor': cand_hi_bg,
        'preferredIndexColor': cand_pref_text,
        'preferredTextColor': cand_pref_text,
        'preferredCommentColor': cand_hint,
        'indexColor': cand_hint,
        'textColor': cand_text,
        'commentColor': cand_hint,
        'indexFontSize': 11,
        'textFontSize': 18,
        'commentFontSize': 11,
    }

    styles = {
        'toolbarButtonBackgroundStyle': {
            'buttonStyleType': 'geometry',
            'cornerRadius': 7,
            'insets': {'top': 2, 'bottom': 2, 'left': 2, 'right': 2},
            'normalColor': '#00000000',
            'highlightColor': btn_func_hi,
        },
        'normalButtonBackground': {
            'buttonStyleType': 'geometry',
            'cornerRadius': 8.5,
            'insets': {'top': 3.5, 'bottom': 3.5, 'left': 2.5, 'right': 2.5},
            'normalColor': btn_normal_bg,
            'highlightColor': btn_normal_hi,
        },
        'functionButtonBackground': {
            'buttonStyleType': 'geometry',
            'cornerRadius': 8.5,
            'insets': {'top': 3.5, 'bottom': 3.5, 'left': 2.5, 'right': 2.5},
            'normalColor': btn_func_bg,
            'highlightColor': btn_func_hi,
        },
        'accentButtonBackground': {
            'buttonStyleType': 'geometry',
            'cornerRadius': 8.5,
            'insets': {'top': 3.5, 'bottom': 3.5, 'left': 2.5, 'right': 2.5},
            'normalColor': btn_accent_bg,
            'highlightColor': btn_accent_hi,
        },
        'candidateStyle': cand_style,
        'horizontalCandidateStyle': cand_style,
        'verticalCandidateStyle': vert_cand_style,
        'candidateStateButtonStyle': {
            'backgroundStyle': 'toolbarButtonBackgroundStyle',
            'foregroundStyle': 'candidateStateButtonForegroundStyle',
        },
        'candidateStateButtonForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'chevron.down',
            'normalColor': fg_normal,
            'fontSize': 16,
        },
        'shiftForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'shift',
            'normalColor': fg_normal,
            'fontSize': 18,
        },
        'shiftUppercasedForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'shift.fill',
            'normalColor': fg_normal,
            'fontSize': 18,
        },
        'shiftCapsLockedForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'capslock.fill',
            'normalColor': fg_normal,
            'fontSize': 18,
        },
        'backspaceForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'delete.left',
            'normalColor': fg_normal,
            'fontSize': 18,
        },
        'languageForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'book.closed',
            'normalColor': fg_normal,
            'fontSize': 17,
        },
        'dismissKeyboardForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'keyboard.chevron.compact.down',
            'normalColor': fg_normal,
            'fontSize': 18,
        },
        'enterForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'magnifyingglass',
            'normalColor': fg_accent,
            'fontSize': 17,
        },
        'returnArrowForegroundStyle': {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'arrow.turn.down.left',
            'normalColor': fg_accent,
            'fontSize': 17,
        },
        'chineseModeToggleForegroundStyle': {
            'buttonStyleType': 'text',
            'text': '中/英',
            'normalColor': fg_normal,
            'fontSize': 14,
        },
    }
    return styles


def sanitize_id(text: str) -> str:
    """
    Generate safe identifier for button and style keys.
    """
    charmap = {
        '~': 'tilde', '`': 'backtick', '!': 'exclam', '@': 'at', '#': 'hash',
        '$': 'dollar', '%': 'percent', '^': 'caret', '&': 'ampersand', '*': 'asterisk',
        '(': 'parenleft', ')': 'parenright', '-': 'minus', '_': 'underscore',
        '+': 'plus', '=': 'equal', '{': 'braceleft', '}': 'braceright',
        '[': 'bracketleft', ']': 'bracketright', '|': 'pipe', '\\': 'backslash',
        ':': 'colon', ';': 'semicolon', '"': 'quote', "'": 'apostrophe',
        '<': 'less', '>': 'greater', ',': 'comma', '.': 'period', '?': 'question',
        '/': 'slash', '，': 'zh_comma', '。': 'zh_period', '！': 'zh_exclam',
        '？': 'zh_question', '：': 'zh_colon', '；': 'zh_semicolon', '、': 'zh_ideocomma',
        '“': 'zh_quoteleft', '”': 'zh_quoteright', '‘': 'zh_sqleft', '’': 'zh_sqright',
        '（': 'zh_parenleft', '）': 'zh_parenright', '《': 'zh_bookleft', '》': 'zh_bookright',
        '「': 'zh_cornerleft', '」': 'zh_cornerright', '•': 'bullet', '√': 'check',
        'π': 'pi', '÷': 'divide', '×': 'multiply', '§': 'section', '£': 'pound',
        '¢': 'cent', '€': 'euro', '¥': 'yen', '°': 'degree', '™': 'tm',
        '✓': 'checkmark', '©': 'copyright', '®': 'registered', 'Δ': 'delta',
    }
    if text in charmap:
        return charmap[text]
    safe = []
    for c in text:
        if c in charmap:
            safe.append(charmap[c])
        elif c.isalnum():
            safe.append(c)
        else:
            safe.append(f"u{ord(c):04x}")
    return '_'.join(safe) if safe else 'sym'


def build_text_key(label: str, action_type: str, action_val: str,
                   theme: str, is_func: bool = False,
                   font_size: int = 17, width_pct: float = None,
                   swipe_type: str = None, swipe_val: str = None,
                   hint_text: str = None, bounds: dict = None,
                   process_by_rime: bool = None):
    """
    Helper to construct a button and its text foreground style(s).
    """
    is_dark = (theme == 'dark')
    fg_normal = "#FFFFFF" if is_dark else "#202124"
    fg_hint = "#A0A0A5" if is_dark else "#70757A"
    btn_bg = 'functionButtonBackground' if is_func else 'normalButtonBackground'

    btn_id = f"btn_{sanitize_id(label)}_{action_type}_{sanitize_id(action_val)}"
    fg_id = f"fg_{sanitize_id(label)}_{font_size}"

    btn_def = {
        'action': {action_type: action_val},
        'backgroundStyle': btn_bg,
        'foregroundStyle': [fg_id],
    }

    if process_by_rime is not None:
        btn_def['processByRIME'] = process_by_rime

    if width_pct is not None:
        btn_def['size'] = {'width': {'percentage': width_pct}}

    if bounds is not None:
        btn_def['bounds'] = bounds

    if swipe_type and swipe_val:
        btn_def['swipeUpAction'] = {swipe_type: swipe_val}

    styles = {}
    styles[fg_id] = {
        'buttonStyleType': 'text',
        'text': label,
        'normalColor': fg_normal,
        'fontSize': font_size,
        'center': {'x': 0.5, 'y': 0.54},
    }

    if label.isascii() and label.isalpha() and len(label) == 1:
        upper_label = label.upper()
        btn_def['uppercasedStateAction'] = {action_type: action_val.upper()}
        upper_fg_id = f"fg_{sanitize_id(upper_label)}_{font_size}"
        styles[upper_fg_id] = {
            'buttonStyleType': 'text',
            'text': upper_label,
            'normalColor': fg_normal,
            'fontSize': font_size,
            'center': {'x': 0.5, 'y': 0.54},
        }
        if hint_text:
            btn_def['uppercasedStateForegroundStyle'] = [upper_fg_id, f"hint_{sanitize_id(hint_text)}"]
            btn_def['capsLockedStateForegroundStyle'] = [upper_fg_id, f"hint_{sanitize_id(hint_text)}"]
        else:
            btn_def['uppercasedStateForegroundStyle'] = [upper_fg_id]
            btn_def['capsLockedStateForegroundStyle'] = [upper_fg_id]

    if hint_text:
        hint_id = f"hint_{sanitize_id(hint_text)}"
        btn_def['foregroundStyle'].append(hint_id)
        styles[hint_id] = {
            'buttonStyleType': 'text',
            'text': hint_text,
            'normalColor': fg_hint,
            'fontSize': 10,
            'center': {'x': 0.75, 'y': 0.28},
        }

    return btn_id, btn_def, styles


def build_icon_key(image_name: str, action, theme: str,
                   is_func: bool = True, font_size: int = 16,
                   width_pct: float = None, repeat_action = None):
    """
    Helper to construct a button with an SF Symbol systemImage.
    """
    is_dark = (theme == 'dark')
    fg_normal = "#FFFFFF" if is_dark else "#202124"
    btn_bg = 'functionButtonBackground' if is_func else 'normalButtonBackground'

    btn_id = f"btn_icon_{sanitize_id(image_name)}"
    fg_id = f"fg_icon_{sanitize_id(image_name)}"

    btn_def = {
        'action': action,
        'backgroundStyle': btn_bg,
        'foregroundStyle': [fg_id],
    }

    if repeat_action:
        btn_def['repeatAction'] = repeat_action

    if width_pct is not None:
        btn_def['size'] = {'width': {'percentage': width_pct}}

    styles = {}
    styles[fg_id] = {
        'buttonStyleType': 'systemImage',
        'systemImageName': image_name,
        'normalColor': fg_normal,
        'fontSize': font_size,
    }

    return btn_id, btn_def, styles


def build_panel(panel_id: str, orientation: str, theme: str):
    """
    Build a complete layout YAML structure according to layout.txt.
    """
    is_landscape = (orientation == 'landscape')
    is_dark = (theme == 'dark')

    # Dimensions
    kb_height = 185 if is_landscape else 265
    tb_height = 36 if is_landscape else 42
    pe_height = 20 if (panel_id == 'pinyin' and is_landscape) else (24 if panel_id == 'pinyin' else 0)

    doc = {
        'keyboardHeight': kb_height,
        'toolbarHeight': tb_height,
        'keyboardStyle': {
            'insets': {'top': 3, 'bottom': 3, 'left': 3, 'right': 3},
        },
        'toolbarStyle': {
            'insets': {'top': 2, 'bottom': 2, 'left': 4, 'right': 4},
        },
    }

    buttons = {}
    styles = get_base_styles(theme)
    fg_normal = "#FFFFFF" if is_dark else "#202124"

    if pe_height > 0:
        doc['preeditHeight'] = pe_height
        doc['preeditStyle'] = {
            'insets': {'top': 2, 'bottom': 2, 'left': 12, 'right': 12},
            'foregroundStyle': 'preeditForegroundStyle',
        }
        styles['preeditForegroundStyle'] = {
            'buttonStyleType': 'text',
            'textColor': fg_normal,
            'normalColor': fg_normal,
            'fontSize': 14,
            'fontWeight': 'regular',
        }

    # Candidates layouts ONLY for Chinese (pinyin) keyboard
    if panel_id == 'pinyin':
        doc['horizontalCandidatesStyle'] = {
            'insets': {'top': 2, 'bottom': 2, 'left': 4, 'right': 4},
        }
        doc['horizontalCandidatesLayout'] = [
            {
                'HStack': {
                    'subviews': [
                        {'Cell': 'horizontalCandidates'},
                        {'Cell': 'expandButton'},
                    ],
                }
            }
        ]
        doc['verticalCandidatesStyle'] = {
            'insets': {'top': 3, 'bottom': 1, 'left': 3, 'right': 3},
        }
        doc['verticalCandidatesLayout'] = [
            {
                'HStack': {
                    'subviews': [{'Cell': 'verticalCandidates'}],
                }
            },
            {
                'HStack': {
                    'style': 'verticalCandidatesToolbarStyle',
                    'subviews': [
                        {'Cell': 'verticalCandidatePageUpButton'},
                        {'Cell': 'verticalCandidatePageDownButton'},
                        {'Cell': 'verticalCandidateReturnButton'},
                        {'Cell': 'verticalCandidateBackspaceButton'},
                    ],
                }
            },
        ]
        doc['candidateContextMenu'] = [
            {'name': '左移', 'action': {'sendKeys': 'Control+j'}},
            {'name': '右移', 'action': {'sendKeys': 'Control+k'}},
            {'name': '重置', 'action': {'sendKeys': 'Control+l'}},
            {'name': '置頂', 'action': {'sendKeys': 'Control+p'}},
            {'name': '移除', 'action': {'sendKeys': 'Control+Delete'}},
        ]

        # Candidate button components
        buttons['horizontalCandidates'] = {
            'type': 'horizontalCandidates',
            'size': {'width': '6/7'},
            'maxColumns': 7,
            'insets': {'left': 3, 'right': 3},
            'candidateStyle': 'horizontalCandidateStyle',
        }
        buttons['horizontalCandidatesCell'] = buttons['horizontalCandidates']

        buttons['expandButton'] = {
            'size': {'width': '1/7'},
            'action': {'shortcut': '#candidatesBarStateToggle'},
            'backgroundStyle': 'toolbarButtonBackgroundStyle',
            'foregroundStyle': ['expandButtonForegroundStyle'],
        }
        styles['expandButtonForegroundStyle'] = {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'chevron.down',
            'normalColor': fg_normal,
            'fontSize': 16,
        }

        buttons['verticalCandidates'] = {
            'type': 'verticalCandidates',
            'insets': {'top': 3, 'bottom': 3, 'left': 3, 'right': 3},
            'maxRows': 5,
            'maxColumns': 5,
            'candidateStyle': 'verticalCandidateStyle',
        }
        styles['verticalCandidatesToolbarStyle'] = {
            'size': {'height': {'percentage': 0.16}},
        }
        buttons['verticalCandidatePageUpButton'] = {
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['verticalCandidatePageUpButtonForegroundStyle'],
            'action': {'shortcut': '#verticalCandidatesPageUp'},
        }
        styles['verticalCandidatePageUpButtonForegroundStyle'] = {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'chevron.up',
            'normalColor': fg_normal,
            'fontSize': 16,
        }
        buttons['verticalCandidatePageDownButton'] = {
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['verticalCandidatePageDownButtonForegroundStyle'],
            'action': {'shortcut': '#verticalCandidatesPageDown'},
        }
        styles['verticalCandidatePageDownButtonForegroundStyle'] = {
            'buttonStyleType': 'systemImage',
            'systemImageName': 'chevron.down',
            'normalColor': fg_normal,
            'fontSize': 16,
        }
        buttons['verticalCandidateReturnButton'] = {
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['verticalCandidateReturnButtonForegroundStyle'],
            'action': {'shortcut': '#candidatesBarStateToggle'},
        }
        styles['verticalCandidateReturnButtonForegroundStyle'] = {
            'buttonStyleType': 'text',
            'text': '返回',
            'normalColor': fg_normal,
            'fontSize': 14,
        }
        buttons['verticalCandidateBackspaceButton'] = {
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['backspaceForegroundStyle'],
            'action': 'backspace',
            'repeatAction': 'backspace',
        }

    # Toolbar layouts (active when candidate bar is not showing candidates)
    if panel_id == 'pinyin':
        doc['toolbarLayout'] = [
            {
                'HStack': {
                    'subviews': [
                        {'Cell': 'tb_switchModeButton'},
                        {'Cell': 'tb_commaButton'},
                        {'Cell': 'tb_periodButton'},
                        {'Cell': 'tb_questionButton'},
                        {'Cell': 'tb_dismissKeyboardButton'},
                    ]
                }
            }
        ]
    else:
        doc['toolbarLayout'] = [
            {
                'HStack': {
                    'subviews': [
                        {'Cell': 'tb_switchPinyinButton'},
                        {'Cell': 'tb_switchAlphabeticButton'},
                        {'Cell': 'tb_switchNumericButton'},
                        {'Cell': 'tb_dismissKeyboardButton'},
                    ]
                }
            }
        ]

    # Reusable toolbar buttons
    buttons['tb_switchModeButton'] = {
        'action': {'keyboardType': 'alphabetic'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['chineseModeToggleForegroundStyle'],
    }
    buttons['tb_commaButton'] = {
        'action': {'symbol': '，'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['fg_zh_comma_16'],
    }
    styles['fg_zh_comma_16'] = {'buttonStyleType': 'text', 'text': '，', 'normalColor': fg_normal, 'fontSize': 16}

    buttons['tb_periodButton'] = {
        'action': {'symbol': '。'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['fg_zh_period_16'],
    }
    styles['fg_zh_period_16'] = {'buttonStyleType': 'text', 'text': '。', 'normalColor': fg_normal, 'fontSize': 16}

    buttons['tb_questionButton'] = {
        'action': {'symbol': '？'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['fg_zh_question_16'],
    }
    styles['fg_zh_question_16'] = {'buttonStyleType': 'text', 'text': '？', 'normalColor': fg_normal, 'fontSize': 16}

    buttons['tb_dismissKeyboardButton'] = {
        'action': 'dismissKeyboard',
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['dismissKeyboardForegroundStyle'],
    }
    buttons['tb_switchPinyinButton'] = {
        'action': {'keyboardType': 'pinyin'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['fg_tb_pinyin'],
    }
    styles['fg_tb_pinyin'] = {'buttonStyleType': 'text', 'text': '拼音', 'normalColor': fg_normal, 'fontSize': 14}

    buttons['tb_switchAlphabeticButton'] = {
        'action': {'keyboardType': 'alphabetic'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['fg_tb_alpha'],
    }
    styles['fg_tb_alpha'] = {'buttonStyleType': 'text', 'text': 'ABC', 'normalColor': fg_normal, 'fontSize': 14}

    buttons['tb_switchNumericButton'] = {
        'action': {'keyboardType': 'numeric'},
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['fg_tb_num'],
    }
    styles['fg_tb_num'] = {'buttonStyleType': 'text', 'text': '123', 'normalColor': fg_normal, 'fontSize': 14}

    # Standard functional buttons
    buttons['btn_shift'] = {
        'size': {'width': {'percentage': 0.15}},
        'action': 'shift',
        'uppercasedStateAction': 'shift',
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['shiftForegroundStyle'],
        'uppercasedStateForegroundStyle': ['shiftUppercasedForegroundStyle'],
        'capsLockedStateForegroundStyle': ['shiftCapsLockedForegroundStyle'],
    }
    buttons['btn_backspace'] = {
        'size': {'width': {'percentage': 0.15}},
        'action': 'backspace',
        'repeatAction': 'backspace',
        'backgroundStyle': 'functionButtonBackground',
        'foregroundStyle': ['backspaceForegroundStyle'],
    }
    buttons['btn_enter'] = {
        'size': {'width': {'percentage': 0.18}},
        'action': 'enter',
        'backgroundStyle': 'accentButtonBackground',
        'foregroundStyle': ['enterForegroundStyle'],
    }
    buttons['btn_space_zh'] = {
        'action': 'space',
        'backgroundStyle': 'normalButtonBackground',
        'foregroundStyle': ['fg_space_zh'],
    }
    styles['fg_space_zh'] = {'buttonStyleType': 'text', 'text': '拼音', 'normalColor': fg_normal, 'fontSize': 15}

    buttons['btn_space_en'] = {
        'action': 'space',
        'processByRIME': False,
        'backgroundStyle': 'normalButtonBackground',
        'foregroundStyle': ['fg_space_en'],
    }
    styles['fg_space_en'] = {'buttonStyleType': 'text', 'text': 'English', 'normalColor': fg_normal, 'fontSize': 15}

    layout_rows = []

    # -------------------------------------------------------------
    # 1. PINYIN (中文主鍵盤)
    # -------------------------------------------------------------
    if panel_id == 'pinyin':
        # Row 1: [1]..[0]
        r1 = []
        for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            b_id, b_def, s_defs = build_text_key(n, 'symbol', n, theme, font_size=18, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 2: [q%] [w\] [e|] [r=] [t[] [y]] [u<] [i>] [o{] [p}]
        r2_map = [
            ('q', '%'), ('w', '\\'), ('e', '|'), ('r', '='), ('t', '['),
            ('y', ']'), ('u', '<'), ('i', '>'), ('o', '{'), ('p', '}'),
        ]
        r2 = []
        for char, hint in r2_map:
            b_id, b_def, s_defs = build_text_key(char, 'character', char, theme,
                                                 swipe_type='symbol', swipe_val=hint, hint_text=hint, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 3: [a@] [s#] [d$] [f_] [g&] [h-] [j+] [k（] [l）]
        # Centered 9 keys: a (0.15, right-aligned 2/3), s..k (0.10 each), l (0.15, left-aligned 2/3)
        r3_map = [
            ('a', '@'), ('s', '#'), ('d', '$'), ('f', '_'), ('g', '&'),
            ('h', '-'), ('j', '+'), ('k', '（'), ('l', '）'),
        ]
        r3 = []
        for i, (char, hint) in enumerate(r3_map):
            if i == 0:
                b_id, b_def, s_defs = build_text_key(char, 'character', char, theme,
                                                     swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                     width_pct=0.15, bounds={'width': '2/3', 'alignment': 'right'})
            elif i == len(r3_map) - 1:
                b_id, b_def, s_defs = build_text_key(char, 'character', char, theme,
                                                     swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                     width_pct=0.15, bounds={'width': '2/3', 'alignment': 'left'})
            else:
                b_id, b_def, s_defs = build_text_key(char, 'character', char, theme,
                                                     swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                     width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 4: [SHIFT] [z、] [x"] [c.] [v：] [b；] [n！] [m？] [BACKSPACE]
        # SPECIAL: x" swipeUp is character: '"' (sent to RIME as user requested!)
        r4_map = [
            ('z', '、', 'symbol'),
            ('x', '"', 'character'),  # <-- Sent to IME!
            ('c', '.', 'symbol'),
            ('v', '：', 'symbol'),
            ('b', '；', 'symbol'),
            ('n', '！', 'symbol'),
            ('m', '？', 'symbol'),
        ]
        r4 = [{'Cell': 'btn_shift'}]
        for char, hint, s_type in r4_map:
            b_id, b_def, s_defs = build_text_key(char, 'character', char, theme,
                                                 swipe_type=s_type, swipe_val=hint, hint_text=hint, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r4.append({'Cell': b_id})
        r4.append({'Cell': 'btn_backspace'})
        layout_rows.append({'HStack': {'subviews': r4}})

        # Row 5: [GOTO_ZH_SYM1] [，] [LANGUAGE] [SPACE] [。] [ENTER]
        b_sym1_id, b_sym1_def, s_sym1 = build_text_key('?123', 'keyboardType', 'custom(zh_sym1)', theme,
                                                       is_func=True, width_pct=0.14)
        buttons[b_sym1_id] = b_sym1_def
        styles.update(s_sym1)

        b_comma_id, b_comma_def, s_comma = build_text_key('，', 'symbol', '，', theme, width_pct=0.10)
        buttons[b_comma_id] = b_comma_def
        styles.update(s_comma)

        buttons['btn_lang_to_alpha'] = {
            'size': {'width': {'percentage': 0.10}},
            'action': {'keyboardType': 'alphabetic'},
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['languageForegroundStyle'],
        }

        b_dot_id, b_dot_def, s_dot = build_text_key('。', 'symbol', '。', theme, width_pct=0.10)
        buttons[b_dot_id] = b_dot_def
        styles.update(s_dot)

        r5 = [
            {'Cell': b_sym1_id},
            {'Cell': b_comma_id},
            {'Cell': 'btn_lang_to_alpha'},
            {'Cell': 'btn_space_zh'},
            {'Cell': b_dot_id},
            {'Cell': 'btn_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r5}})

    # -------------------------------------------------------------
    # 2. ALPHA (英語主鍵盤 - 直通輸出，不進 RIME 輸入法)
    # -------------------------------------------------------------
    elif panel_id == 'alphabetic':
        # Row 1: [1]..[0]
        r1 = []
        for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            b_id, b_def, s_defs = build_text_key(n, 'symbol', n, theme, font_size=18, width_pct=0.10, process_by_rime=False)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 2: [q%] [w\] [e|] [r=] [t[] [y]] [u<] [i>] [o{] [p}]
        r2_map = [
            ('q', '%'), ('w', '\\'), ('e', '|'), ('r', '='), ('t', '['),
            ('y', ']'), ('u', '<'), ('i', '>'), ('o', '{'), ('p', '}'),
        ]
        r2 = []
        for char, hint in r2_map:
            b_id, b_def, s_defs = build_text_key(char, 'symbol', char, theme,
                                                 swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                 width_pct=0.10, process_by_rime=False)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 3: [a@] [s#] [d$] [f_] [g&] [h-] [j+] [k(] [l)]
        # Centered 9 keys: a (0.15, right-aligned 2/3), s..k (0.10 each), l (0.15, left-aligned 2/3)
        r3_map = [
            ('a', '@'), ('s', '#'), ('d', '$'), ('f', '_'), ('g', '&'),
            ('h', '-'), ('j', '+'), ('k', '('), ('l', ')'),
        ]
        r3 = []
        for i, (char, hint) in enumerate(r3_map):
            if i == 0:
                b_id, b_def, s_defs = build_text_key(char, 'symbol', char, theme,
                                                     swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                     width_pct=0.15, bounds={'width': '2/3', 'alignment': 'right'},
                                                     process_by_rime=False)
            elif i == len(r3_map) - 1:
                b_id, b_def, s_defs = build_text_key(char, 'symbol', char, theme,
                                                     swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                     width_pct=0.15, bounds={'width': '2/3', 'alignment': 'left'},
                                                     process_by_rime=False)
            else:
                b_id, b_def, s_defs = build_text_key(char, 'symbol', char, theme,
                                                     swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                     width_pct=0.10, process_by_rime=False)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 4: [SHIFT] [z*] [x"] [c'] [v:] [b;] [n!] [m?] [BACKSPACE]
        r4_map = [
            ('z', '*'), ('x', '"'), ('c', "'"), ('v', ':'),
            ('b', ';'), ('n', '!'), ('m', '?'),
        ]
        r4 = [{'Cell': 'btn_shift'}]
        for char, hint in r4_map:
            b_id, b_def, s_defs = build_text_key(char, 'symbol', char, theme,
                                                 swipe_type='symbol', swipe_val=hint, hint_text=hint,
                                                 width_pct=0.10, process_by_rime=False)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r4.append({'Cell': b_id})
        r4.append({'Cell': 'btn_backspace'})
        layout_rows.append({'HStack': {'subviews': r4}})

        # Row 5: [GOTO_EN_SYM1] [,] [LANGUAGE] [SPACE] [.] [ENTER]
        b_sym1_id, b_sym1_def, s_sym1 = build_text_key('?123', 'keyboardType', 'custom(en_sym1)', theme,
                                                       is_func=True, width_pct=0.14)
        buttons[b_sym1_id] = b_sym1_def
        styles.update(s_sym1)

        b_comma_id, b_comma_def, s_comma = build_text_key(',', 'symbol', ',', theme, width_pct=0.10, process_by_rime=False)
        buttons[b_comma_id] = b_comma_def
        styles.update(s_comma)

        buttons['btn_lang_to_pinyin'] = {
            'size': {'width': {'percentage': 0.10}},
            'action': {'keyboardType': 'pinyin'},
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['languageForegroundStyle'],
        }

        b_dot_id, b_dot_def, s_dot = build_text_key('.', 'symbol', '.', theme, width_pct=0.10, process_by_rime=False)
        buttons[b_dot_id] = b_dot_def
        styles.update(s_dot)

        r5 = [
            {'Cell': b_sym1_id},
            {'Cell': b_comma_id},
            {'Cell': 'btn_lang_to_pinyin'},
            {'Cell': 'btn_space_en'},
            {'Cell': b_dot_id},
            {'Cell': 'btn_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r5}})

    # -------------------------------------------------------------
    # 3. ZH_SYM1 (中文符號頁面 1)
    # -------------------------------------------------------------
    elif panel_id == 'zh_sym1':
        # Row 1: [ ⬅️, ⬆️, 全選, 剪下, 複製, 黏貼, ⬇️, ➡️ ]
        r0 = []
        ctrl_specs = [
            ('chevron.left', 'moveCursorBackward', 'moveCursorBackward'),
            ('chevron.up', {'sendKeys': 'Up'}, {'sendKeys': 'Up'}),
            ('selection.pin.in.out', {'shortcut': '#selectText'}, None),
            ('scissors', {'shortcut': '#cut'}, None),
            ('square.on.square', {'shortcut': '#copy'}, None),
            ('list.clipboard', {'shortcut': '#paste'}, None),
            ('chevron.down', {'sendKeys': 'Down'}, {'sendKeys': 'Down'}),
            ('chevron.right', 'moveCursorForward', 'moveCursorForward'),
        ]
        for img, act, rep in ctrl_specs:
            b_id, b_def, s_defs = build_icon_key(img, act, theme, is_func=True, font_size=16,
                                                 width_pct=0.125, repeat_action=rep)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r0.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r0}})

        # Row 2: [1]..[0]
        r1 = []
        for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            b_id, b_def, s_defs = build_text_key(n, 'symbol', n, theme, font_size=18, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 3: [@] [#] [$] [_] [&] [-] [+] [（] [）] [/]
        r2_chars = ['@', '#', '$', '_', '&', '-', '+', '（', '）', '/']
        r2 = []
        for c in r2_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 4: [GOTO_ZH_SYM2] [、] [“] [”] [：] [；] [！] [？] [BACKSPACE]
        b_sym2_id, b_sym2_def, s_sym2 = build_text_key('=\\<', 'keyboardType', 'custom(zh_sym2)', theme,
                                                       is_func=True, width_pct=0.15)
        buttons[b_sym2_id] = b_sym2_def
        styles.update(s_sym2)

        r3_chars = ['、', '“', '”', '：', '；', '！', '？']
        r3 = [{'Cell': b_sym2_id}]
        for c in r3_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        r3.append({'Cell': 'btn_backspace'})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 5: [GOTO_PINYIN] [,] [GOTO_NUM] [SPACE] [.] [ENTER]
        b_back_id, b_back_def, s_back = build_text_key('返回', 'keyboardType', 'pinyin', theme,
                                                       is_func=True, width_pct=0.14, font_size=15)
        buttons[b_back_id] = b_back_def
        styles.update(s_back)

        b_comma_id, b_comma_def, s_comma = build_text_key(',', 'symbol', ',', theme, width_pct=0.10)
        buttons[b_comma_id] = b_comma_def
        styles.update(s_comma)

        b_num_id, b_num_def, s_num = build_text_key('123', 'keyboardType', 'custom(zh_num)', theme,
                                                    is_func=True, width_pct=0.10, font_size=15)
        buttons[b_num_id] = b_num_def
        styles.update(s_num)

        b_dot_id, b_dot_def, s_dot = build_text_key('.', 'symbol', '.', theme, width_pct=0.10)
        buttons[b_dot_id] = b_dot_def
        styles.update(s_dot)

        r4 = [
            {'Cell': b_back_id},
            {'Cell': b_comma_id},
            {'Cell': b_num_id},
            {'Cell': 'btn_space_zh'},
            {'Cell': b_dot_id},
            {'Cell': 'btn_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r4}})

    # -------------------------------------------------------------
    # 4. ZH_SYM2 (中文更多符號頁面 2)
    # -------------------------------------------------------------
    elif panel_id == 'zh_sym2':
        # Row 1: [1]..[0]
        r0 = []
        for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            b_id, b_def, s_defs = build_text_key(n, 'symbol', n, theme, font_size=18, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r0.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r0}})

        # Row 2: [~] [`] [|] [•] [√] [π] [÷] [×] [*] [§]
        r1_chars = ['~', '`', '|', '•', '√', 'π', '÷', '×', '*', '§']
        r1 = []
        for c in r1_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 3: [£] [¢] [€] [¥] [^] [°] [=] [「] [」] [\]
        r2_chars = ['£', '¢', '€', '¥', '^', '°', '=', '「', '」', '\\']
        r2 = []
        for c in r2_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 4: [GOTO_ZH_SYM1] [%] [‘] [’] [TM] [✓] [[] []] [BACKSPACE]
        b_sym1_id, b_sym1_def, s_sym1 = build_text_key('?123', 'keyboardType', 'custom(zh_sym1)', theme,
                                                       is_func=True, width_pct=0.15)
        buttons[b_sym1_id] = b_sym1_def
        styles.update(s_sym1)

        r3_chars = ['%', '‘', '’', '™', '✓', '[', ']']
        r3 = [{'Cell': b_sym1_id}]
        for c in r3_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        r3.append({'Cell': 'btn_backspace'})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 5: [GOTO_PINYIN] [《] [GOTO_DEFAULT_SYM] [SPACE] [》] [ENTER]
        b_back_id, b_back_def, s_back = build_text_key('返回', 'keyboardType', 'pinyin', theme,
                                                       is_func=True, width_pct=0.14, font_size=15)
        buttons[b_back_id] = b_back_def
        styles.update(s_back)

        b_bleft_id, b_bleft_def, s_bleft = build_text_key('《', 'symbol', '《', theme, width_pct=0.10)
        buttons[b_bleft_id] = b_bleft_def
        styles.update(s_bleft)

        # GOTO_DEFAULT_SYM -> symbolic (YuanShu built-in fallback symbols)
        b_defsym_id, b_defsym_def, s_defsym = build_text_key('更多', 'keyboardType', 'symbolic', theme,
                                                             is_func=True, width_pct=0.10, font_size=14)
        buttons[b_defsym_id] = b_defsym_def
        styles.update(s_defsym)

        b_bright_id, b_bright_def, s_bright = build_text_key('》', 'symbol', '》', theme, width_pct=0.10)
        buttons[b_bright_id] = b_bright_def
        styles.update(s_bright)

        r4 = [
            {'Cell': b_back_id},
            {'Cell': b_bleft_id},
            {'Cell': b_defsym_id},
            {'Cell': 'btn_space_zh'},
            {'Cell': b_bright_id},
            {'Cell': 'btn_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r4}})

    # -------------------------------------------------------------
    # 5. EN_SYM1 (英語符號頁面 1)
    # -------------------------------------------------------------
    elif panel_id == 'en_sym1':
        # Row 1: [ ⬅️, ⬆️, 全選, 剪下, 複製, 黏貼, ⬇️, ➡️ ]
        r0 = []
        ctrl_specs = [
            ('chevron.left', 'moveCursorBackward', 'moveCursorBackward'),
            ('chevron.up', {'sendKeys': 'Up'}, {'sendKeys': 'Up'}),
            ('selection.pin.in.out', {'shortcut': '#selectText'}, None),
            ('scissors', {'shortcut': '#cut'}, None),
            ('square.on.square', {'shortcut': '#copy'}, None),
            ('list.clipboard', {'shortcut': '#paste'}, None),
            ('chevron.down', {'sendKeys': 'Down'}, {'sendKeys': 'Down'}),
            ('chevron.right', 'moveCursorForward', 'moveCursorForward'),
        ]
        for img, act, rep in ctrl_specs:
            b_id, b_def, s_defs = build_icon_key(img, act, theme, is_func=True, font_size=16,
                                                 width_pct=0.125, repeat_action=rep)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r0.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r0}})

        # Row 2: [1]..[0]
        r1 = []
        for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            b_id, b_def, s_defs = build_text_key(n, 'symbol', n, theme, font_size=18, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 3: [@] [#] [$] [_] [&] [-] [+] [(] [)] [/]
        r2_chars = ['@', '#', '$', '_', '&', '-', '+', '(', ')', '/']
        r2 = []
        for c in r2_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 4: [GOTO_EN_SYM2] [*] ["] ['] [:] [;] [!] [?] [BACKSPACE]
        b_sym2_id, b_sym2_def, s_sym2 = build_text_key('=\\<', 'keyboardType', 'custom(en_sym2)', theme,
                                                       is_func=True, width_pct=0.15)
        buttons[b_sym2_id] = b_sym2_def
        styles.update(s_sym2)

        r3_chars = ['*', '"', "'", ':', ';', '!', '?']
        r3 = [{'Cell': b_sym2_id}]
        for c in r3_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        r3.append({'Cell': 'btn_backspace'})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 5: [GOTO_ALPHA] [,] [GOTO_NUM] [SPACE] [.] [ENTER]
        b_alpha_id, b_alpha_def, s_alpha = build_text_key('ABC', 'keyboardType', 'alphabetic', theme,
                                                          is_func=True, width_pct=0.14, font_size=15)
        buttons[b_alpha_id] = b_alpha_def
        styles.update(s_alpha)

        b_comma_id, b_comma_def, s_comma = build_text_key(',', 'symbol', ',', theme, width_pct=0.10)
        buttons[b_comma_id] = b_comma_def
        styles.update(s_comma)

        # Goes to en_num!
        b_num_id, b_num_def, s_num = build_text_key('123', 'keyboardType', 'custom(en_num)', theme,
                                                    is_func=True, width_pct=0.10, font_size=15)
        buttons[b_num_id] = b_num_def
        styles.update(s_num)

        b_dot_id, b_dot_def, s_dot = build_text_key('.', 'symbol', '.', theme, width_pct=0.10)
        buttons[b_dot_id] = b_dot_def
        styles.update(s_dot)

        r4 = [
            {'Cell': b_alpha_id},
            {'Cell': b_comma_id},
            {'Cell': b_num_id},
            {'Cell': 'btn_space_en'},
            {'Cell': b_dot_id},
            {'Cell': 'btn_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r4}})

    # -------------------------------------------------------------
    # 6. EN_SYM2 (英語更多符號頁面 2)
    # -------------------------------------------------------------
    elif panel_id == 'en_sym2':
        # Row 1: [1]..[0]
        r0 = []
        for n in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            b_id, b_def, s_defs = build_text_key(n, 'symbol', n, theme, font_size=18, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r0.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r0}})

        # Row 2: [~] [`] [|] [•] [√] [π] [÷] [×] [§] [Δ]
        r1_chars = ['~', '`', '|', '•', '√', 'π', '÷', '×', '§', 'Δ']
        r1 = []
        for c in r1_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 3: [£] [¢] [€] [¥] [^] [°] [=] [{] [}] [\]
        r2_chars = ['£', '¢', '€', '¥', '^', '°', '=', '{', '}', '\\']
        r2 = []
        for c in r2_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 4: [GOTO_EN_SYM1] [%] [©] [®] [TM] [✓] [[] []] [BACKSPACE]
        b_sym1_id, b_sym1_def, s_sym1 = build_text_key('?123', 'keyboardType', 'custom(en_sym1)', theme,
                                                       is_func=True, width_pct=0.15)
        buttons[b_sym1_id] = b_sym1_def
        styles.update(s_sym1)

        r3_chars = ['%', '©', '®', '™', '✓', '[', ']']
        r3 = [{'Cell': b_sym1_id}]
        for c in r3_chars:
            b_id, b_def, s_defs = build_text_key(c, 'symbol', c, theme, font_size=19, width_pct=0.10)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        r3.append({'Cell': 'btn_backspace'})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 5: [GOTO_ALPHA] [<] [GOTO_DEFAULT_SYM] [SPACE] [>] [ENTER]
        b_alpha_id, b_alpha_def, s_alpha = build_text_key('ABC', 'keyboardType', 'alphabetic', theme,
                                                          is_func=True, width_pct=0.14, font_size=15)
        buttons[b_alpha_id] = b_alpha_def
        styles.update(s_alpha)

        b_lt_id, b_lt_def, s_lt = build_text_key('<', 'symbol', '<', theme, width_pct=0.10)
        buttons[b_lt_id] = b_lt_def
        styles.update(s_lt)

        # GOTO_DEFAULT_SYM -> symbolic (YuanShu built-in fallback symbols) replaces numeric pad
        b_defsym_id, b_defsym_def, s_defsym = build_text_key('更多', 'keyboardType', 'symbolic', theme,
                                                             is_func=True, width_pct=0.10, font_size=14)
        buttons[b_defsym_id] = b_defsym_def
        styles.update(s_defsym)

        b_gt_id, b_gt_def, s_gt = build_text_key('>', 'symbol', '>', theme, width_pct=0.10)
        buttons[b_gt_id] = b_gt_def
        styles.update(s_gt)

        r4 = [
            {'Cell': b_alpha_id},
            {'Cell': b_lt_id},
            {'Cell': b_defsym_id},
            {'Cell': 'btn_space_en'},
            {'Cell': b_gt_id},
            {'Cell': 'btn_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r4}})

    # -------------------------------------------------------------
    # 7. ZH_NUM & EN_NUM (數字九宮格鍵盤)
    # -------------------------------------------------------------
    elif panel_id in ('zh_num', 'en_num'):
        is_zh = (panel_id == 'zh_num')
        target_qwerty = 'pinyin' if is_zh else 'alphabetic'
        target_sym = 'custom(zh_sym1)' if is_zh else 'custom(en_sym1)'
        back_label = '返回' if is_zh else 'ABC'

        # Row 1: [+] [1] [2] [3] [%]
        r1_keys = [
            ('+', 'symbol', '+', True, 0.18),
            ('1', 'symbol', '1', False, 0.21),
            ('2', 'symbol', '2', False, 0.21),
            ('3', 'symbol', '3', False, 0.21),
            ('%', 'symbol', '%', True, 0.18),
        ]
        r1 = []
        for lbl, a_type, a_val, f_flag, w_pct in r1_keys:
            b_id, b_def, s_defs = build_text_key(lbl, a_type, a_val, theme,
                                                 is_func=f_flag, width_pct=w_pct, font_size=20)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r1.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r1}})

        # Row 2: [-] [4] [5] [6] [GOTO_SYM1]
        r2_keys = [
            ('-', 'symbol', '-', True, 0.18),
            ('4', 'symbol', '4', False, 0.21),
            ('5', 'symbol', '5', False, 0.21),
            ('6', 'symbol', '6', False, 0.21),
            ('!?#', 'keyboardType', target_sym, True, 0.18),
        ]
        r2 = []
        for lbl, a_type, a_val, f_flag, w_pct in r2_keys:
            b_id, b_def, s_defs = build_text_key(lbl, a_type, a_val, theme,
                                                 is_func=f_flag, width_pct=w_pct, font_size=18 if f_flag else 20)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r2.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r2}})

        # Row 3: [*] [7] [8] [9] [BACKSPACE]
        buttons['btn_num_backspace'] = {
            'size': {'width': {'percentage': 0.18}},
            'action': 'backspace',
            'repeatAction': 'backspace',
            'backgroundStyle': 'functionButtonBackground',
            'foregroundStyle': ['backspaceForegroundStyle'],
        }
        r3_keys = [
            ('*', 'symbol', '*', True, 0.18),
            ('7', 'symbol', '7', False, 0.21),
            ('8', 'symbol', '8', False, 0.21),
            ('9', 'symbol', '9', False, 0.21),
        ]
        r3 = []
        for lbl, a_type, a_val, f_flag, w_pct in r3_keys:
            b_id, b_def, s_defs = build_text_key(lbl, a_type, a_val, theme,
                                                 is_func=f_flag, width_pct=w_pct, font_size=20)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r3.append({'Cell': b_id})
        r3.append({'Cell': 'btn_num_backspace'})
        layout_rows.append({'HStack': {'subviews': r3}})

        # Row 4: [/] [,] [0] [=] [.]
        r4_keys = [
            ('/', 'symbol', '/', True, 0.18),
            (',', 'symbol', ',', False, 0.21),
            ('0', 'symbol', '0', False, 0.21),
            ('=', 'symbol', '=', False, 0.21),
            ('.', 'symbol', '.', True, 0.18),
        ]
        r4 = []
        for lbl, a_type, a_val, f_flag, w_pct in r4_keys:
            b_id, b_def, s_defs = build_text_key(lbl, a_type, a_val, theme,
                                                 is_func=f_flag, width_pct=w_pct, font_size=20)
            buttons[b_id] = b_def
            styles.update(s_defs)
            r4.append({'Cell': b_id})
        layout_rows.append({'HStack': {'subviews': r4}})

        # Row 5: [BACK] [SPACE] [ENTER]
        b_back_id, b_back_def, s_back = build_text_key(back_label, 'keyboardType', target_qwerty, theme,
                                                       is_func=True, width_pct=0.25, font_size=16)
        buttons[b_back_id] = b_back_def
        styles.update(s_back)

        btn_num_space_id = f"btn_num_space_{panel_id}"
        buttons[btn_num_space_id] = {
            'action': 'space',
            'backgroundStyle': 'normalButtonBackground',
            'foregroundStyle': ['fg_space_zh' if is_zh else 'fg_space_en'],
        }

        buttons['btn_num_enter'] = {
            'size': {'width': {'percentage': 0.25}},
            'action': 'enter',
            'backgroundStyle': 'accentButtonBackground',
            'foregroundStyle': ['enterForegroundStyle'],
        }

        r5 = [
            {'Cell': b_back_id},
            {'Cell': btn_num_space_id},
            {'Cell': 'btn_num_enter'},
        ]
        layout_rows.append({'HStack': {'subviews': r5}})

    doc['keyboardLayout'] = layout_rows
    doc.update(buttons)
    doc.update(styles)
    return doc


def generate_config_yaml():
    """
    Return root config.yaml dictionary mapping iPhone and iPad layouts.
    Strictly follows Hamster / WanxiangSkin schema to ensure proper iOS detection.
    Maps all standard and non-standard pages (pinyin, alphabetic, numeric, symbolic,
    zh_sym1, zh_sym2, en_sym1, en_sym2, zh_num, en_num) in both snake_case and camelCase.
    """
    layout_specs = {
        'pinyin': ('pinyinPortrait', 'pinyinLandscape'),
        'chinese': ('pinyinPortrait', 'pinyinLandscape'),
        'alphabetic': ('alphabeticPortrait', 'alphabeticLandscape'),
        'english': ('alphabeticPortrait', 'alphabeticLandscape'),
        'numeric': ('zhNumPortrait', 'zhNumLandscape'),
        'numericNineGrid': ('zhNumPortrait', 'zhNumLandscape'),
        'zh_sym1': ('zhSym1Portrait', 'zhSym1Landscape'),
        'zhSym1': ('zhSym1Portrait', 'zhSym1Landscape'),
        'custom(zh_sym1)': ('zhSym1Portrait', 'zhSym1Landscape'),
        'custom(zhSym1)': ('zhSym1Portrait', 'zhSym1Landscape'),
        'zh_sym2': ('zhSym2Portrait', 'zhSym2Landscape'),
        'zhSym2': ('zhSym2Portrait', 'zhSym2Landscape'),
        'custom(zh_sym2)': ('zhSym2Portrait', 'zhSym2Landscape'),
        'custom(zhSym2)': ('zhSym2Portrait', 'zhSym2Landscape'),
        'en_sym1': ('enSym1Portrait', 'enSym1Landscape'),
        'enSym1': ('enSym1Portrait', 'enSym1Landscape'),
        'custom(en_sym1)': ('enSym1Portrait', 'enSym1Landscape'),
        'custom(enSym1)': ('enSym1Portrait', 'enSym1Landscape'),
        'en_sym2': ('enSym2Portrait', 'enSym2Landscape'),
        'enSym2': ('enSym2Portrait', 'enSym2Landscape'),
        'custom(en_sym2)': ('enSym2Portrait', 'enSym2Landscape'),
        'custom(enSym2)': ('enSym2Portrait', 'enSym2Landscape'),
        'zh_num': ('zhNumPortrait', 'zhNumLandscape'),
        'zhNum': ('zhNumPortrait', 'zhNumLandscape'),
        'custom(zh_num)': ('zhNumPortrait', 'zhNumLandscape'),
        'custom(zhNum)': ('zhNumPortrait', 'zhNumLandscape'),
        'en_num': ('enNumPortrait', 'enNumLandscape'),
        'enNum': ('enNumPortrait', 'enNumLandscape'),
        'custom(en_num)': ('enNumPortrait', 'enNumLandscape'),
        'custom(enNum)': ('enNumPortrait', 'enNumLandscape'),
    }

    config = {
        'name': 'CatnipGboard',
        'author': 'Salt',
    }

    for kbd_name, (portrait, landscape) in layout_specs.items():
        config[kbd_name] = {
            'iPhone': {
                'portrait': portrait,
                'landscape': landscape,
            },
            'iPad': {
                'portrait': portrait,
                'landscape': landscape,
                'floating': portrait,
            },
        }

    return config


def write_jsonnet_sources(root_dir: Path):
    """
    Generate clean, modular Jsonnet sources modeled after kongshan-suying.
    """
    jsonnet_dir = root_dir / 'jsonnet'
    jsonnet_dir.mkdir(parents=True, exist_ok=True)
    components_dir = jsonnet_dir / 'Components'
    components_dir.mkdir(parents=True, exist_ok=True)
    panels_dir = jsonnet_dir / 'Panels'
    panels_dir.mkdir(parents=True, exist_ok=True)

    # 1. Settings.libsonnet
    settings_code = """// Settings.libsonnet
// Basic skin settings & customization (editable in Hamster's fine-tune / 微調 panel)
{
  name: 'CatnipGboard',
  version: '1.2.0',
  author: 'Salt',

  // Dimensions
  dimensions: {
    portrait: {
      keyboardHeight: 265,
      toolbarHeight: 42,
      preeditHeight: 24,
    },
    landscape: {
      keyboardHeight: 185,
      toolbarHeight: 36,
      preeditHeight: 20,
    },
  },

  // Color schemes (Gboard inspired)
  colors: {
    light: {
      keyboardBg: '#ECEFF1',
      toolbarBg: '#ECEFF1',
      buttonNormalBg: '#FFFFFF',
      buttonNormalHighlight: '#CFD8DC',
      buttonFuncBg: '#CFD8DC',
      buttonFuncHighlight: '#B0BEC5',
      buttonAccentBg: '#1A73E8',
      buttonAccentHighlight: '#1557B0',
      textNormal: '#202124',
      textAccent: '#FFFFFF',
      textHint: '#70757A',
    },
    dark: {
      keyboardBg: '#1C1C1E',
      toolbarBg: '#1C1C1E',
      buttonNormalBg: '#545458',
      buttonNormalHighlight: '#3A3A3C',
      buttonFuncBg: '#3A3A3C',
      buttonFuncHighlight: '#2C2C2E',
      buttonAccentBg: '#0A84FF',
      buttonAccentHighlight: '#0055B3',
      textNormal: '#FFFFFF',
      textAccent: '#FFFFFF',
      textHint: '#A0A0A5',
    },
  },
}
"""
    (jsonnet_dir / 'Settings.libsonnet').write_text(settings_code, encoding='utf-8')

    # 2. Config.libsonnet
    config_code = """// Config.libsonnet
// Generates the root config.yaml with all standard and non-standard keyboard layouts
local settings = import 'Settings.libsonnet';

local makeTargets(portrait, landscape) = {
  iPhone: { portrait: portrait, landscape: landscape },
  iPad: { portrait: portrait, landscape: landscape, floating: portrait },
};

{
  name: settings.name,
  author: settings.author,

  pinyin: makeTargets('pinyinPortrait', 'pinyinLandscape'),
  chinese: makeTargets('pinyinPortrait', 'pinyinLandscape'),
  alphabetic: makeTargets('alphabeticPortrait', 'alphabeticLandscape'),
  english: makeTargets('alphabeticPortrait', 'alphabeticLandscape'),
  numeric: makeTargets('zhNumPortrait', 'zhNumLandscape'),
  numericNineGrid: makeTargets('zhNumPortrait', 'zhNumLandscape'),

  zh_sym1: makeTargets('zhSym1Portrait', 'zhSym1Landscape'),
  zhSym1: makeTargets('zhSym1Portrait', 'zhSym1Landscape'),
  'custom(zh_sym1)': makeTargets('zhSym1Portrait', 'zhSym1Landscape'),
  'custom(zhSym1)': makeTargets('zhSym1Portrait', 'zhSym1Landscape'),

  zh_sym2: makeTargets('zhSym2Portrait', 'zhSym2Landscape'),
  zhSym2: makeTargets('zhSym2Portrait', 'zhSym2Landscape'),
  'custom(zh_sym2)': makeTargets('zhSym2Portrait', 'zhSym2Landscape'),
  'custom(zhSym2)': makeTargets('zhSym2Portrait', 'zhSym2Landscape'),

  en_sym1: makeTargets('enSym1Portrait', 'enSym1Landscape'),
  enSym1: makeTargets('enSym1Portrait', 'enSym1Landscape'),
  'custom(en_sym1)': makeTargets('enSym1Portrait', 'enSym1Landscape'),
  'custom(enSym1)': makeTargets('enSym1Portrait', 'enSym1Landscape'),

  en_sym2: makeTargets('enSym2Portrait', 'enSym2Landscape'),
  enSym2: makeTargets('enSym2Portrait', 'enSym2Landscape'),
  'custom(en_sym2)': makeTargets('enSym2Portrait', 'enSym2Landscape'),
  'custom(enSym2)': makeTargets('enSym2Portrait', 'enSym2Landscape'),

  zh_num: makeTargets('zhNumPortrait', 'zhNumLandscape'),
  zhNum: makeTargets('zhNumPortrait', 'zhNumLandscape'),
  'custom(zh_num)': makeTargets('zhNumPortrait', 'zhNumLandscape'),
  'custom(zhNum)': makeTargets('zhNumPortrait', 'zhNumLandscape'),

  en_num: makeTargets('enNumPortrait', 'enNumLandscape'),
  enNum: makeTargets('enNumPortrait', 'enNumLandscape'),
  'custom(en_num)': makeTargets('enNumPortrait', 'enNumLandscape'),
  'custom(enNum)': makeTargets('enNumPortrait', 'enNumLandscape'),
}
"""
    (jsonnet_dir / 'Config.libsonnet').write_text(config_code, encoding='utf-8')

    # 3. main.jsonnet (The root compile entrypoint)
    main_code = """// main.jsonnet
// Entry point for compilation: jsonnet -S -m . ./jsonnet/main.jsonnet
// Also executable in Hamster app via long-press "运行 main.jsonnet"

// Note: Full JSON/YAML definitions are compiled automatically into light/ and dark/
{
  'config.yaml': std.manifestYamlDoc(import 'Config.libsonnet'),
}
"""
    (jsonnet_dir / 'main.jsonnet').write_text(main_code, encoding='utf-8')


def build_all(root_dir: Path):
    """
    Generate all YAML files, Jsonnet source files, demo.png, and config.yaml.
    """
    print(f"[+] Generating skin framework in: {root_dir}")

    # 1. Generate config.yaml
    config_dict = generate_config_yaml()
    config_yaml_str = dump_yaml(config_dict)
    (root_dir / 'config.yaml').write_text(config_yaml_str + '\n', encoding='utf-8')
    print("    - Generated config.yaml")

    # 2. Generate demo.png only if it doesn't exist
    demo_path = root_dir / 'demo.png'
    if not demo_path.exists():
        create_demo_png(demo_path)
        print("    - Generated placeholder demo.png")
    else:
        print("    - Preserved existing custom demo.png")

    # 3. Generate light & dark layouts for all 8 panels
    # Map panel IDs to output file prefixes
    panel_files = {
        'pinyin': 'pinyin',
        'alphabetic': 'alphabetic',
        'zh_sym1': 'zhSym1',
        'zh_sym2': 'zhSym2',
        'en_sym1': 'enSym1',
        'en_sym2': 'enSym2',
        'zh_num': 'zhNum',
        'en_num': 'enNum',
    }

    orientations = ['Portrait', 'Landscape']
    themes = ['light', 'dark']

    for theme in themes:
        theme_dir = root_dir / theme
        theme_dir.mkdir(parents=True, exist_ok=True)
        for p_id, p_prefix in panel_files.items():
            for ori in orientations:
                file_name = f"{p_prefix}{ori}.yaml"
                file_path = theme_dir / file_name
                panel_doc = build_panel(p_id, ori.lower(), theme)
                yaml_str = dump_yaml(panel_doc)
                file_path.write_text(yaml_str + '\n', encoding='utf-8')
                print(f"    - Generated {theme}/{file_name}")

    # 4. Generate Jsonnet source architecture
    write_jsonnet_sources(root_dir)
    print("    - Generated jsonnet/ source architecture")


def package_skin(root_dir: Path, output_file: Path = None, skin_name: str = "CatnipGboard"):
    """
    Package the skin directory into a clean, valid .cskin ZIP bundle.
    All files are nested inside a top-level directory named `skin_name`
    (e.g., CatnipGboard/), ensuring Hamster extracts it as a single skin
    and correctly recognizes light, dark, and jsonnet components.
    """
    if output_file is None:
        dist_dir = root_dir / 'dist'
        dist_dir.mkdir(parents=True, exist_ok=True)
        output_file = dist_dir / f"{skin_name}.cskin"

    print(f"[+] Packaging skin into top-level folder '{skin_name}/' inside {output_file}...")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Root configuration, documentation, preview, and root main.jsonnet
        for fname in ['config.yaml', 'README.md', 'demo.png', 'main.jsonnet']:
            fpath = root_dir / fname
            if fpath.exists():
                arcname = f"{skin_name}/{fname}"
                zipf.write(fpath, arcname=arcname)

        # 2. Light & Dark layout directories
        for theme in ['light', 'dark']:
            tdir = root_dir / theme
            if tdir.exists():
                for item in tdir.rglob('*.yaml'):
                    rel_path = item.relative_to(root_dir)
                    arcname = f"{skin_name}/{rel_path}"
                    zipf.write(item, arcname=arcname)

        # 3. Jsonnet source directory
        jdir = root_dir / 'jsonnet'
        if jdir.exists():
            for item in jdir.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(root_dir)
                    arcname = f"{skin_name}/{rel_path}"
                    zipf.write(item, arcname=arcname)

    print(f"[v] Single skin package successfully built: {output_file} ({output_file.stat().st_size} bytes)")


def validate_skin(root_dir: Path):
    """
    Validate that all required files and references exist.
    """
    print("[+] Validating skin framework...")
    errors = []

    config_file = root_dir / 'config.yaml'
    if not config_file.exists():
        errors.append("Missing config.yaml")

    if not (root_dir / 'demo.png').exists():
        errors.append("Missing demo.png")

    panel_prefixes = ['pinyin', 'alphabetic', 'zhSym1', 'zhSym2', 'enSym1', 'enSym2', 'zhNum', 'enNum']
    orientations = ['Portrait', 'Landscape']
    for theme in ['light', 'dark']:
        for prefix in panel_prefixes:
            for ori in orientations:
                p = root_dir / theme / f"{prefix}{ori}.yaml"
                if not p.exists():
                    errors.append(f"Missing layout file: {theme}/{prefix}{ori}.yaml")

    if errors:
        print("[!] Validation failed with errors:")
        for e in errors:
            print(f"    - {e}")
        return False

    print("[v] Validation passed! All 8 panels and files are in place.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Hamster Keyboard Skin Tool")
    parser.add_argument('--build', action='store_true', default=True, help="Build YAML and Jsonnet files")
    parser.add_argument('--package', action='store_true', help="Package into .cskin zip")
    parser.add_argument('--validate', action='store_true', help="Validate files")
    parser.add_argument('--output', type=str, default=None, help="Output .cskin path")

    args = parser.parse_args()
    root_dir = Path(__file__).resolve().parent.parent

    if args.build:
        build_all(root_dir)

    if args.validate or args.package:
        if not validate_skin(root_dir):
            sys.exit(1)

    if args.package:
        out_path = Path(args.output) if args.output else None
        package_skin(root_dir, out_path)


if __name__ == '__main__':
    main()
