// Panels/Symbolic.libsonnet
local settings = import '../Settings.libsonnet';
local stylesHelper = import '../Components/Styles.libsonnet';
local buttonsHelper = import '../Components/Buttons.libsonnet';

local charsR1 = ['[', ']', '{', '}', '#', '%', '^', '*', '+', '='];
local charsR2 = ['_', '\\', '|', '~', '<', '>', '€', '£', '¥', '•'];
local charsR3 = ['.', ',', '?', '!', "'"];

local buildPanel(orientation, theme) =
  local dims = settings.dimensions[orientation];
  local styles = stylesHelper.getStyles(theme);
  local commonButtons = buttonsHelper.getCommonButtons();

  local r1Keys = [buttonsHelper.makeCharKey(c, theme) for c in charsR1];
  local r2Keys = [buttonsHelper.makeCharKey(c, theme) for c in charsR2];
  local r3Keys = [buttonsHelper.makeCharKey(c, theme) for c in charsR3];

  local allCharButtons = { [k.name]: k.button for k in (r1Keys + r2Keys + r3Keys) };
  local allCharStyles = { [k.styleName]: k.style for k in (r1Keys + r2Keys + r3Keys) };

  {
    keyboardHeight: dims.keyboardHeight,
    toolbarHeight: dims.toolbarHeight,
    keyboardStyle: {
      insets: { top: 3, bottom: 3, left: 3, right: 3 },
      backgroundStyle: 'keyboardBackgroundStyle',
    },
    toolbarStyle: {
      insets: { top: 2, bottom: 2, left: 4, right: 4 },
      backgroundStyle: 'toolbarBackgroundStyle',
    },
    toolbarLayout: [
      {
        HStack: {
          subviews: [
            { Cell: 'switchPinyinButton' },
            { Cell: 'switchAlphabeticButton' },
            { Cell: 'switchNumericButton' },
            { Cell: 'switchSymbolicButton' },
            { Cell: 'dismissKeyboardButton' },
          ],
        },
      },
    ],
    keyboardLayout: [
      { HStack: { subviews: [{ Cell: k.name } for k in r1Keys] } },
      { HStack: { subviews: [{ Cell: k.name } for k in r2Keys] } },
      {
        HStack: {
          subviews: [{ Cell: 'switchNumericButton' }] +
                    [{ Cell: k.name } for k in r3Keys] +
                    [{ Cell: 'backspaceButton' }],
        },
      },
      {
        HStack: {
          subviews: [
            { Cell: 'switchAlphabeticButton' },
            { Cell: 'nextKeyboardButton' },
            { Cell: 'switchPinyinButton' },
            { Cell: 'spaceButton' },
            { Cell: 'enterButton' },
          ],
        },
      },
    ],
  } + commonButtons + styles + allCharButtons + allCharStyles;

{
  portrait(theme): buildPanel('portrait', theme),
  landscape(theme): buildPanel('landscape', theme),
}
