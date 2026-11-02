// Settings.libsonnet
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
