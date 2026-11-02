// Components/Styles.libsonnet
// Generates background and foreground styles for a given theme
local settings = import '../Settings.libsonnet';

{
  getStyles(theme):
    local c = settings.colors[theme];
    {
      keyboardBackgroundStyle: {
        buttonStyleType: 'geometry',
        normalColor: c.keyboardBg,
      },
      toolbarBackgroundStyle: {
        buttonStyleType: 'geometry',
        normalColor: c.toolbarBg,
      },
      normalButtonBackground: {
        buttonStyleType: 'geometry',
        cornerRadius: 14,
        normalColor: c.buttonNormalBg,
        highlightColor: c.buttonNormalHighlight,
      },
      functionButtonBackground: {
        buttonStyleType: 'geometry',
        cornerRadius: 14,
        normalColor: c.buttonFuncBg,
        highlightColor: c.buttonFuncHighlight,
      },
      accentButtonBackground: {
        buttonStyleType: 'geometry',
        cornerRadius: 14,
        normalColor: c.buttonAccentBg,
        highlightColor: c.buttonAccentHighlight,
      },
      candidateStyle: {
        insets: { top: 4, bottom: 4, left: 8, right: 8 },
        normalColor: c.textNormal,
        highlightBackgroundColor: c.buttonNormalBg,
        fontSize: 18,
      },
      shiftForegroundStyle: {
        buttonStyleType: 'systemImage',
        systemImageName: 'shift',
        normalColor: c.textNormal,
        fontSize: 18,
      },
      shiftUppercasedForegroundStyle: {
        buttonStyleType: 'systemImage',
        systemImageName: 'shift.fill',
        normalColor: c.textNormal,
        fontSize: 18,
      },
      shiftCapsLockedForegroundStyle: {
        buttonStyleType: 'systemImage',
        systemImageName: 'capslock.fill',
        normalColor: c.textNormal,
        fontSize: 18,
      },
      backspaceForegroundStyle: {
        buttonStyleType: 'systemImage',
        systemImageName: 'delete.left',
        normalColor: c.textNormal,
        fontSize: 18,
      },
      nextKeyboardForegroundStyle: {
        buttonStyleType: 'systemImage',
        systemImageName: 'book.closed',
        normalColor: c.textNormal,
        fontSize: 17,
      },
      dismissKeyboardForegroundStyle: {
        buttonStyleType: 'systemImage',
        systemImageName: 'keyboard.chevron.compact.down',
        normalColor: c.textNormal,
        fontSize: 18,
      },
      spaceForegroundStyle: {
        buttonStyleType: 'text',
        text: '空白',
        normalColor: c.textNormal,
        fontSize: 15,
      },
      spaceEnglishForegroundStyle: {
        buttonStyleType: 'text',
        text: 'space',
        normalColor: c.textNormal,
        fontSize: 15,
      },
      enterForegroundStyle: {
        buttonStyleType: 'text',
        text: '換行',
        normalColor: c.textAccent,
        fontSize: 16,
      },
      enterEnglishForegroundStyle: {
        buttonStyleType: 'text',
        text: 'return',
        normalColor: c.textAccent,
        fontSize: 16,
      },
      numericSwitchForegroundStyle: {
        buttonStyleType: 'text',
        text: '123',
        normalColor: c.textNormal,
        fontSize: 16,
      },
      symbolicSwitchForegroundStyle: {
        buttonStyleType: 'text',
        text: '#+=',
        normalColor: c.textNormal,
        fontSize: 16,
      },
      pinyinSwitchForegroundStyle: {
        buttonStyleType: 'text',
        text: '拼音',
        normalColor: c.textNormal,
        fontSize: 15,
      },
      alphabeticSwitchForegroundStyle: {
        buttonStyleType: 'text',
        text: 'ABC',
        normalColor: c.textNormal,
        fontSize: 15,
      },
      chineseModeToggleForegroundStyle: {
        buttonStyleType: 'text',
        text: '中/英',
        normalColor: c.textNormal,
        fontSize: 14,
      },
      commaForegroundStyle: {
        buttonStyleType: 'text',
        text: '，',
        normalColor: c.textNormal,
        fontSize: 16,
      },
      periodForegroundStyle: {
        buttonStyleType: 'text',
        text: '。',
        normalColor: c.textNormal,
        fontSize: 16,
      },
      questionForegroundStyle: {
        buttonStyleType: 'text',
        text: '？',
        normalColor: c.textNormal,
        fontSize: 16,
      },
    },
}
