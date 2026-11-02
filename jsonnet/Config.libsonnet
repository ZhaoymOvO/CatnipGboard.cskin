// Config.libsonnet
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
