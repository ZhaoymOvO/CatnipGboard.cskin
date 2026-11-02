// Components/Buttons.libsonnet
// Button helpers and common function buttons
{
  makeCharKey(char, theme, swipeUpChar=null):
    local keyName = 'key_' + char;
    local styleName = 'fg_' + char;
    {
      name: keyName,
      styleName: styleName,
      button: {
        action: { character: char },
        backgroundStyle: 'normalButtonBackground',
        foregroundStyle: [styleName],
      } + (if swipeUpChar != null then { swipeUpAction: { character: swipeUpChar } } else {}),
      style: {
        buttonStyleType: 'text',
        text: char,
        normalColor: if theme == 'dark' then '#FFFFFF' else '#000000',
        fontSize: 22,
      },
    },

  getCommonButtons(): {
    shiftButton: {
      size: { width: { percentage: 0.135 } },
      action: { action: 'shift' },
      uppercasedStateAction: { action: 'shift' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['shiftForegroundStyle'],
      uppercasedStateForegroundStyle: ['shiftUppercasedForegroundStyle'],
      capsLockedStateForegroundStyle: ['shiftCapsLockedForegroundStyle'],
    },
    backspaceButton: {
      size: { width: { percentage: 0.135 } },
      action: { action: 'backspace' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['backspaceForegroundStyle'],
    },
    switchNumericButton: {
      size: { width: { percentage: 0.135 } },
      action: { keyboardType: 'numeric' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['numericSwitchForegroundStyle'],
    },
    switchSymbolicButton: {
      size: { width: { percentage: 0.135 } },
      action: { keyboardType: 'symbolic' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['symbolicSwitchForegroundStyle'],
    },
    switchPinyinButton: {
      size: { width: { percentage: 0.12 } },
      action: { keyboardType: 'pinyin' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['pinyinSwitchForegroundStyle'],
    },
    switchAlphabeticButton: {
      size: { width: { percentage: 0.12 } },
      action: { keyboardType: 'alphabetic' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['alphabeticSwitchForegroundStyle'],
    },
    nextKeyboardButton: {
      size: { width: { percentage: 0.11 } },
      action: { action: 'nextKeyboard' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['nextKeyboardForegroundStyle'],
    },
    spaceButton: {
      action: { action: 'space' },
      backgroundStyle: 'normalButtonBackground',
      foregroundStyle: ['spaceForegroundStyle'],
    },
    spaceEnglishButton: {
      action: { action: 'space' },
      backgroundStyle: 'normalButtonBackground',
      foregroundStyle: ['spaceEnglishForegroundStyle'],
    },
    enterButton: {
      size: { width: { percentage: 0.22 } },
      action: { action: 'enter' },
      backgroundStyle: 'accentButtonBackground',
      foregroundStyle: ['enterForegroundStyle'],
    },
    enterEnglishButton: {
      size: { width: { percentage: 0.22 } },
      action: { action: 'enter' },
      backgroundStyle: 'accentButtonBackground',
      foregroundStyle: ['enterEnglishForegroundStyle'],
    },
    horizontalCandidatesCell: {
      type: 'horizontalCandidates',
      candidateStyle: 'candidateStyle',
    },
    switchModeButton: {
      action: { keyboardType: 'alphabetic' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['chineseModeToggleForegroundStyle'],
    },
    punctuationCommaButton: {
      action: { character: '，' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['commaForegroundStyle'],
    },
    punctuationPeriodButton: {
      action: { character: '。' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['periodForegroundStyle'],
    },
    punctuationQuestionButton: {
      action: { character: '？' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['questionForegroundStyle'],
    },
    dismissKeyboardButton: {
      action: { action: 'dismissKeyboard' },
      backgroundStyle: 'functionButtonBackground',
      foregroundStyle: ['dismissKeyboardForegroundStyle'],
    },
  },
}
