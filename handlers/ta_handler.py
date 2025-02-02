import re
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.binance_service import get_ta_data

TA_DATA_CACHE = {}

router = Router()

def escape_md(text: str) -> str:

    return re.sub(r'([_*[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def calculate_composite_signal(ta_data):

    score_buy = 0
    score_sell = 0
    details = []

    rsi = ta_data.get("RSI")
    if rsi is None:
        details.append("*RSI:* Нет данных\\.")
    else:
        rsi_str = escape_md(f"{rsi:.2f}")
        if rsi > 70:
            score_sell += 1
            details.append(
                f"*RSI:* {rsi_str} 🔴 — значение выше 70 \\(перекупленность, сигнал *SELL*\\)\\."
            )
        elif rsi < 30:
            score_buy += 1
            details.append(
                f"*RSI:* {rsi_str} 🟢 — значение ниже 30 \\(перепроданность, сигнал *BUY*\\)\\."
            )
        else:
            details.append(f"*RSI:* {rsi_str} ⚪ — нейтральное состояние\\.")


    adx = ta_data.get("ADX")
    if adx is not None:
        adx_str = escape_md(f"{adx:.2f}")
        if adx >= 25:
            details.append(f"*ADX:* {adx_str} 💪 — сильный тренд\\.")
            last_close = ta_data.get("last_close")
            sma50 = ta_data.get("SMA_50")
            ema20 = ta_data.get("EMA_20")
            if last_close is not None and sma50 is not None and ema20 is not None:
                last_close_str = escape_md(f"{last_close:.2f}")
                sma50_str = escape_md(f"{sma50:.2f}")
                ema20_str = escape_md(f"{ema20:.2f}")
                if last_close > sma50 and last_close > ema20:
                    score_buy += 1
                    details.append(
                        f"*Цена:* {last_close_str} > *SMA 50:* {sma50_str} и *EMA 20:* {ema20_str} 📈 — сигнал *BUY*\\."
                    )
                elif last_close < sma50 and last_close < ema20:
                    score_sell += 1
                    details.append(
                        f"*Цена:* {last_close_str} < *SMA 50:* {sma50_str} и *EMA 20:* {ema20_str} 📉 — сигнал *SELL*\\."
                    )
                else:
                    details.append(
                        f"*Цена:* {last_close_str} находится между *SMA 50* и *EMA 20* — сигнал нейтральный\\."
                    )
        else:
            details.append(f"*ADX:* {adx_str} 🤷 — слабый или неустойчивый тренд\\.")
    else:
        details.append("*ADX:* Нет данных\\.")


    macd = ta_data.get("MACD")
    macd_signal = ta_data.get("MACD_signal")
    if macd is not None and macd_signal is not None:
        macd_str = escape_md(f"{macd:.2f}")
        macd_signal_str = escape_md(f"{macd_signal:.2f}")
        if macd > macd_signal:
            score_buy += 1
            details.append(
                f"*MACD:* {macd_str} > *Signal:* {macd_signal_str} 🔼 — сигнал *BUY*\\."
            )
        elif macd < macd_signal:
            score_sell += 1
            details.append(
                f"*MACD:* {macd_str} < *Signal:* {macd_signal_str} 🔽 — сигнал *SELL*\\."
            )
        else:
            details.append("*MACD:* Сигнальная линия совпадает — нейтрально\\.")
    else:
        details.append("*MACD:* Нет данных\\.")


    bb_upper = ta_data.get("BB_upper")
    bb_lower = ta_data.get("BB_lower")
    last_close = ta_data.get("last_close")
    if bb_upper is not None and bb_lower is not None and last_close is not None:
        bb_upper_str = escape_md(f"{bb_upper:.2f}")
        bb_lower_str = escape_md(f"{bb_lower:.2f}")
        last_close_str = escape_md(f"{last_close:.2f}")
        if last_close >= bb_upper:
            score_sell += 1
            details.append(
                f"*Bollinger Bands:* Цена {last_close_str} ≥ Верхней {bb_upper_str} ⬆️ — сигнал *SELL*\\."
            )
        elif last_close <= bb_lower:
            score_buy += 1
            details.append(
                f"*Bollinger Bands:* Цена {last_close_str} ≤ Нижней {bb_lower_str} ⬇️ — сигнал *BUY*\\."
            )
        else:
            details.append(
                f"*Bollinger Bands:* Цена {last_close_str} находится внутри диапазона\\."
            )
    else:
        details.append("*Bollinger Bands:* Нет данных\\.")


    obv = ta_data.get("OBV")
    if obv is not None:
        obv_str = escape_md(f"{obv:.2f}")
        details.append(
            f"*OBV:* {obv_str} 💰 — требуется динамический анализ для оценки тренда\\."
        )
    else:
        details.append("*OBV:* Нет данных\\.")


    atr = ta_data.get("ATR")
    if atr is not None:
        atr_str = escape_md(f"{atr:.2f}")
        details.append(f"*ATR:* {atr_str} 📊 — показывает уровень волатильности\\.")
    else:
        details.append("*ATR:* Нет данных\\.")


    if score_buy > score_sell:
        overall_signal = "BUY"
        overall_emoji = "🟢"
    elif score_sell > score_buy:
        overall_signal = "SELL"
        overall_emoji = "🔴"
    else:
        overall_signal = "NEUTRAL"
        overall_emoji = "⚪"

    report = f"*Общий сигнал: {overall_signal} {overall_emoji}*\n\n" + "\n".join(details)
    return overall_signal, report


@router.message(Command("ta"))
async def ta_command_handler(message: types.Message) -> None:

    parts = message.text.split()
    if len(parts) != 3:
        await message.reply("Используйте формат: /ta <валютная пара> <интервал>\nНапример: /ta BTCUSDT 1h")
        return

    _, pair, interval = parts
    user_id = message.from_user.id

    ta_data = get_ta_data(user_id, pair, interval)
    if "error" in ta_data:
        await message.reply(f"Ошибка: {ta_data['error']}")
        return

    TA_DATA_CACHE[user_id] = ta_data


    last_close_val = ta_data.get("last_close")
    last_close_str = escape_md(str(last_close_val)) if last_close_val is not None else "Нет данных"

    rsi_val = ta_data.get("RSI")
    rsi_str = escape_md(f"{rsi_val:.2f}") if rsi_val is not None else "Нет данных"

    adx_val = ta_data.get("ADX")
    adx_str = escape_md(f"{adx_val:.2f}") if adx_val is not None else "Нет данных"

    macd_val = ta_data.get("MACD")
    macd_str = escape_md(f"{macd_val:.2f}") if macd_val is not None else "Нет данных"

    bb_upper_val = ta_data.get("BB_upper")
    bb_upper_str = escape_md(f"{bb_upper_val:.2f}") if bb_upper_val is not None else "Нет данных"

    bb_lower_val = ta_data.get("BB_lower")
    bb_lower_str = escape_md(f"{bb_lower_val:.2f}") if bb_lower_val is not None else "Нет данных"

    summary = (
        f"*Результаты технического анализа для {escape_md(pair)} на интервале {escape_md(interval)}:*\n"
        f"*Цена закрытия:* {last_close_str}\n"
        f"*RSI:* {rsi_str}\n"
        f"*ADX:* {adx_str}\n"
        f"*MACD:* {macd_str}\n"
        f"*Bollinger Bands:* Верх {bb_upper_str}, Ниж {bb_lower_str}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать сигнал", callback_data="calc_signal")]
    ])

    await message.reply(summary, reply_markup=keyboard, parse_mode="MarkdownV2")

@router.callback_query(F.data == "calc_signal")
async def calc_signal_callback_handler(callback_query: types.CallbackQuery) -> None:

    user_id = callback_query.from_user.id
    ta_data = TA_DATA_CACHE.get(user_id)
    if not ta_data:
        await callback_query.answer("Нет данных для расчёта сигнала. Повторите запрос командой /ta")
        return

    overall_signal, report = calculate_composite_signal(ta_data)

    del TA_DATA_CACHE[user_id]

    await callback_query.message.answer(report, parse_mode="MarkdownV2")
    await callback_query.answer()
