from telebot import types

#                                     Profile MurkUp                                   #
#######################################################################################

profileMP = types.InlineKeyboardMarkup(row_width=1)
name_button = types.InlineKeyboardButton("Изменить имя", callback_data="pr_name")
tp_button = types.InlineKeyboardButton("Изменить телефон", callback_data="pr_tp")
address_button = types.InlineKeyboardButton("Изменить адрес", callback_data="pr_address")
email_button = types.InlineKeyboardButton("Изменить почту", callback_data="pr_email")
confirm_button = types.InlineKeyboardButton("Продолжить", callback_data="pr_confirm")
profileMP.add(name_button, tp_button, address_button, email_button, confirm_button)

##########################################################################################