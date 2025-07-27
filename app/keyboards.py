from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

subject = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text='Matemātika', callback_data='math'),
        KeyboardButton(text='Fizika', callback_data='physics')
    ],
              [
                  KeyboardButton(text='Angļu valoda', callback_data='english'),
                  KeyboardButton(text='Vēsture', callback_data='history')
              ]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Izvēlies testa priekšmetu...')

testType = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text='1.'),
        KeyboardButton(text='2.'),
        KeyboardButton(text='3.')
    ]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Izvēlies testa veidu...')

difficulty = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text='Viegls'),
        KeyboardButton(text='Vidējais'),
        KeyboardButton(text='Grūtais')
    ]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Izvēlies testa sarežģītību...')

shopItems = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='1.', callback_data='firstItem'),
    InlineKeyboardButton(text='2.', callback_data='secondItem'),
    InlineKeyboardButton(text='3.', callback_data='thirdItem'),
    InlineKeyboardButton(text='4.', callback_data='fourthItem')
]])

reviewKeyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Iepriekšējais jautājums', callback_data='back'),
    InlineKeyboardButton(text='Nākamais jautājums', callback_data='forward')
]])

tryAgain = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Mēģināt vēlreiz', callback_data='tryTestAgain')
]])

historyButtons = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Atpakaļ', callback_data='goBack'),
    InlineKeyboardButton(text='Uz priekšu', callback_data='goForward')
], [InlineKeyboardButton(text='Dzēst vēsturi', callback_data='deleteHistory')]
                                                       ])
