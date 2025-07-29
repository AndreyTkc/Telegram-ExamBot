import asyncio, time, random
from datetime import datetime, timedelta
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.subjects.math import *
from app.subjects.physics import *
from app.subjects.english import *
from app.subjects.history import *
from db.database import SessionLocal, UserStats, UserHistory
import json

router = Router()

keys = [
    "date_time", "subject", "difficulty", "test_mode",
    "correct_answers_in_test", "wrong_answers_in_test", "percentages",
    "test_time", "obtained_points"
]

selectedSubject = ''
subjectValue = ''
selectedTestType = ''
testType = ''
selectedDifficulty = ''
difficulty = ''
selectedAnswer = ''
currentQuestion = ''
shopText = ''
currentQuestionOrder = 0
correctAnswersInTest = 0
wrongAnswersInTest = 0
spentTimeInTest = None
reviewMode = False
randomQuestions = None
randomOptions = None
answerList = []
lives = 3
passed = asyncio.Event()
stopPage = asyncio.Event()
dailyTaskActive = False
randomQuestion = dict
currentBatch = 0
totalBatches = 0
historyList = []
historyPage = ''
defaultText = True


def resetHistory():
    global currentBatch, totalBatches, historyList, historyPage, defaultText
    currentBatch = 0
    totalBatches = 0
    historyList.clear()
    historyPage = ''
    defaultText = True


def resetValues():
    global selectedSubject, subjectValue, selectedTestType, testType, selectedDifficulty, difficulty, selectedAnswer, currentQuestion, currentQuestionOrder, correctAnswersInTest, wrongAnswersInTest, spentTimeInTest, reviewMode, randomQuestions, randomOptions, answerList, lives, passed, dailyTaskActive, randomQuestion
    selectedSubject = ''
    subjectValue = ''
    selectedTestType = ''
    testType = ''
    selectedDifficulty = ''
    difficulty = ''
    selectedAnswer = ''
    currentQuestion = ''
    currentQuestionOrder = 0
    correctAnswersInTest = 0
    wrongAnswersInTest = 0
    spentTimeInTest = None
    reviewMode = False
    randomQuestions = None
    randomOptions = None
    answerList.clear()
    passed = asyncio.Event()
    dailyTaskActive = False
    randomQuestion = dict
    CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly = False


def tryTestAgainResetValues():
    global selectedAnswer, currentQuestion, currentQuestionOrder, correctAnswersInTest, wrongAnswersInTest, spentTimeInTest, reviewMode, randomQuestions, randomOptions, answerList, lives, passed, randomQuestion
    selectedAnswer = ''
    currentQuestion = ''
    currentQuestionOrder = 0
    correctAnswersInTest = 0
    wrongAnswersInTest = 0
    spentTimeInTest = None
    reviewMode = False
    randomQuestions = None
    randomOptions = None
    answerList.clear()
    passed = asyncio.Event()
    randomQuestion = dict
    CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly = False
    CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly = False


class Prepare(StatesGroup):
    selectSubject = State()
    selectTestType = State()
    selectDifficulty = State()
    startTest = State()
    testEnd = State()
    review = State()
    history = State()
    shop = State()


class MathTest(StatesGroup):
    mathTestSelect = State()
    firstQ = State()
    secondQ = State()
    thirdQ = State()
    fourthQ = State()
    fifthQ = State()
    sixthQ = State()
    seventhQ = State()
    eighthQ = State()
    ninthQ = State()
    tenthQ = State()


class PhysicsTest(StatesGroup):
    physicsTestSelect = State()
    firstQ = State()
    secondQ = State()
    thirdQ = State()
    fourthQ = State()
    fifthQ = State()
    sixthQ = State()
    seventhQ = State()
    eighthQ = State()
    ninthQ = State()
    tenthQ = State()


class EnglishTest(StatesGroup):
    englishTestSelect = State()
    firstQ = State()
    secondQ = State()
    thirdQ = State()
    fourthQ = State()
    fifthQ = State()
    sixthQ = State()
    seventhQ = State()
    eighthQ = State()
    ninthQ = State()
    tenthQ = State()


class HistoryTest(StatesGroup):
    historyTestSelect = State()
    firstQ = State()
    secondQ = State()
    thirdQ = State()
    fourthQ = State()
    fifthQ = State()
    sixthQ = State()
    seventhQ = State()
    eighthQ = State()
    ninthQ = State()
    tenthQ = State()


class CorrectlyAnsweredTenQuestions():
    is1QuestionAnsweredCorrectly = False
    is2QuestionAnsweredCorrectly = False
    is3QuestionAnsweredCorrectly = False
    is4QuestionAnsweredCorrectly = False
    is5QuestionAnsweredCorrectly = False
    is6QuestionAnsweredCorrectly = False
    is7QuestionAnsweredCorrectly = False
    is8QuestionAnsweredCorrectly = False
    is9QuestionAnsweredCorrectly = False
    is10QuestionAnsweredCorrectly = False


def createInlineKeyboard(firstOption, secondOption, thirdOption, fourthOption):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=firstOption, callback_data='a')],
            [InlineKeyboardButton(text=secondOption, callback_data='b')],
            [InlineKeyboardButton(text=thirdOption, callback_data='c')],
            [InlineKeyboardButton(text=fourthOption, callback_data='d')]
        ],
        one_time_keyboard=True,
    )
    return keyboard


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    resetValues()
    await message.answer(
        'Sveiks! Es esmu <i>“Eksāmena Bots”</i> un es palīdzēšu tev sagatavoties eksāmenam dažādos priekšmetos. '
        'Tu vari izvēlēties vajadzīgo priekšmetu no piedāvātā saraksta, testa veidu un sarežģītību.\nIevadi komandu '
        '/help, lai iepazītos ar visām bota komandām un sāktu gatavoties eksāmenam!',
        reply_markup=types.ReplyKeyboardRemove())


@router.message(Command('help', ignore_case=True))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    resetValues()
    await message.answer(
        'Eksāmena bota komandas:\n/help - tiek atvērta bāzes izvēlne ar visām bota komandām.\n/faq - tiek atvērta '
        'izvēlne ar bieži uzdotiem jautājumiem.\n/test - tiek atvērta starta izvēlne ar testa, priekšmeta un sarežģītības '
        'izvēli.\n/daily - lietotājam tiek uzdots viens nejaušs ikdienas jautājums nejaušā sarežģītības līmenī, nejaušā '
        'priekšmetā.\n/stats - tiek atvērta lietotāja statistika.\n/history - tiek atvērta lietotāja vēstures izvēlne '
        'ar iepriekšējām testa vērtējumiem.\n/shop - tiek atvērta veikala izvēlne, kur saņemtos punktus var apmainīt '
        'pret bonusiem.',
        reply_markup=types.ReplyKeyboardRemove())


@router.message(Command('stats', ignore_case=True))
async def cmd_stats(message: Message, state: FSMContext):
    db = SessionLocal()
    await state.clear()
    resetValues()
    activeBonusList = ''
    correctAnswers = db.query(UserStats).filter_by(id=1).first().correct_answers
    wrongAnswers = db.query(UserStats).filter_by(id=1).first().wrong_answers
    questionValue = correctAnswers + wrongAnswers
    if questionValue != 0:
        knowledgeKoeficient = round((correctAnswers / questionValue) * 100, 1)
    else:
        knowledgeKoeficient = 0
    userPoints = db.query(UserStats).filter_by(id=1).first().points
    if db.query(UserStats).filter_by(id=1).first().third_test_lives_amount > 3:
        activeBonusList += f'{db["third_test_lives_amount"]} dzīvības trešā veida testā.\n'
    if db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated:
        activeBonusList += '+1 mēģinājums ikdienas jautājumam.\n'
    if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
        activeBonusList += 'Rādīt uzdevuma risinājumu, ja lietotājs nav pareizi atbildējis uz jautājumu.\n'
    if db.query(UserStats).filter_by(id=1).first().point_multiplier > 1:
        activeBonusList += 'Visu punktu reizinātājs 2x.\n'
    if activeBonusList == '':
        activeBonusList = 'Nav aktīvo bonusu.'
    await message.answer(
        f"Tava statistika:\nPareizas atbildes: <b>{correctAnswers}</b>\nNepareizas atbildes: <b>{wrongAnswers}</b>"
        f"\nAtbildēto jautājumu skaits: <b>{questionValue}</b>\nZināšanu procents: <b>{knowledgeKoeficient}%</b>\nPunktu "
        f"skaits: <b>{userPoints}</b>\n\nAktīvie bonusi:\n{activeBonusList}",
        reply_markup=types.ReplyKeyboardRemove())
    db.close()


@router.message(Command('history', ignore_case=True))
async def cmd_history(message: Message, state: FSMContext):
    db = SessionLocal()
    await state.clear()
    resetValues()
    global historyList
    global stopPage
    resetHistory()
    stopPage.set()
    await state.set_state(Prepare.history)
    listLength = len(db.query(UserHistory).all())
    if listLength == 0:
        await message.answer('Nav testu vēstures.')
    elif listLength > 0:
        for i in range(listLength - 1, -1, -1):
            historyElement = (
                f"Datums un laiks: <b>{db.query(UserHistory).all()[i].date_time}</b>\n"
                f"Priekšmets: <b>{db.query(UserHistory).all()[i].subject}</b>\n"
                f"Sarežģītības līmenis: <b>{db.query(UserHistory).all()[i].difficulty}</b>\n"
                f"Testa veids: <b>{db.query(UserHistory).all()[i].test_mode}</b>\n"
                f"Pareizas atbildes testā: <b>{db.query(UserHistory).all()[i].correct_answers_in_test}</b>\n"
                f"Nepareizas atbildes testā: <b>{db.query(UserHistory).all()[i].wrong_answers_in_test}</b>\n"
                f"Procentu izpilde: <b>{db.query(UserHistory).all()[i].percentages}%</b>\n"
                f"Testa izpildes laiks: <b>{db.query(UserHistory).all()[i].test_time}</b>\n"
                f"Saņemtie punkti: <b>{db.query(UserHistory).all()[i].obtained_points}</b>")
            historyList.append(historyElement)
        await showBatches(message, state)
    db.close()


async def showBatches(message: Message, state: FSMContext):
    global currentBatch
    global totalBatches
    global stopPage
    global historyPage
    global defaultText
    insertHistory = ''
    batchSize = 3
    totalBatches = (len(historyList) + batchSize - 1) // batchSize
    while currentBatch < totalBatches and stopPage.is_set():
        start_index = currentBatch * 3
        end_index = min(start_index + 3, len(historyList))
        for i in range(start_index, end_index):
            insertHistory += historyList[i]
            insertHistory += "\n\n"
        if defaultText:
            historyPage = await message.answer(insertHistory,
                                               reply_markup=kb.historyButtons)
            defaultText = False
        elif not defaultText:
            historyPage = await historyPage.edit_text(
                insertHistory, reply_markup=kb.historyButtons)
        stopPage.clear()


@router.message(Command('faq', ignore_case=True))
async def cmd_faq(message: Message, state: FSMContext):
    await state.clear()
    resetValues()
    await message.answer(
        'Bieži uzdotie jautājumi:\n1. Kas ir eksāmenu bots?\n— Eksāmenu bots ir bots Telegram vietnē, kas palīdzēs'
        ' Jums sagatavoties eksāmenam jebkurā no 4 pieejamajiem priekšmetiem, atbildot uz dažādu sarežģījumu testa'
        ' jautājumiem.\n\n2. Kādi priekšmeti pieejami botā?\n— Matemātika, fizika, angļu valoda un vēsture.\n\n'
        '3. Kādi režīmi pieejami botā?\n— “10 jautājumu” režīms, ātrais režīms “1 jautājums”, sarežģītais režīms'
        ' “10 jautājumi ar "3 dzīvībām"” un ikdienas nejaušais jautājums.\n\n4. Vai botā ir pieejami dažādi'
        ' sarežģītības līmeņi?\n— Jā, botā ir pieejami: viegls, vidējs un sarežģīts režīms.\n\n5. Vai varu noskatīties'
        ' pareizo atbildi un risinājumu jautājumām?\n— Jā, lai to izdarītu, vajag pareizi atbildet uz jautājumu vai'
        ' nopirkt bonusu veikalā.\n\n6. Vai es varu atkārtoti atbildēt ikdienas jautājumu vienā dienā?\n— Nē, ikdienas'
        ' jautājumam ir pieejams tikai 1 mēģinājums katru dienu. Ar bonusa palīdzību var atbildēt uz 2 ikdienas'
        ' jautājumiem dienā.\n\n7. Vai es varu iztērēt saņemtos punktus?\n— Jā, jūs varat iegādāties bonusus veikalā'
        ' par saņemtajiem punktiem ar komandas /shop palidzību.\n\n8. Vai jautājumi mainās testos?\n— Jā, jautājumi'
        ' tiek nejauši atlasīti no jautājumu datubāzes. Tāpat mainās atbilžu kārtība.\n\n9. Kā es varu atgriezties'
        ' sakumā no jebkuras vietas?\n— Ievadiet komandu /help, lai atgrieztos sākuma izvēlnē.',
        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Prepare.selectSubject)


@router.message(Command('shop', ignore_case=True))
async def cmd_shop(message: Message, state: FSMContext):
    db = SessionLocal()
    global shopText
    await state.clear()
    resetValues()
    shopText = await message.answer(
        f'Veikals:\n1. +1 "dzīvība" pie testa - 10 jautājumu tests ar 3 “dzīvībām” (limits 5 dzīvības) — '
        f'<b>100 punkti</b>.\n2. +1 mēģinājums ikdienas jautājumam (vienreizējs pirkums) — <b>200 punkti</b>.\n'
        f'3. Rādīt uzdevuma risinājumu, ja lietotājs nav pareizi atbildējis uz jautājumu (vienreizējs pirkums) — '
        f'<b>300 punkti</b>.\n4. Visu punktu reizinātājs 2x (vienreizējs pirkums) — <b>300 punkti</b>.\n\nTavs punktu '
        f'atlikums: <b>{db.query(UserStats).filter_by(id=1).first().points}</b>\n\n[!] Bonusi tiek pirkti uz visiem laikiem.\n\nJa vēlies iegādāties vajadzīgo '
        f'preci, nospied pogu ar atbilstošu preces numuru.',
        reply_markup=kb.shopItems)
    await state.set_state(Prepare.shop)
    db.close()

async def shop_text(message: Message, state: FSMContext):
    db = SessionLocal()
    global shopText
    shopText = await message.edit_text(
        f'Veikals:\n1. +1 "dzīvība" pie testa - 10 jautājumu tests ar 3 “dzīvībām” (limits 5 dzīvības) — <b>100 '
        f'punkti</b>.\n2. +1 mēģinājums ikdienas jautājumam (vienreizējs pirkums) — <b>200 punkti</b>.\n3. Rādīt '
        f'uzdevuma risinājumu, ja lietotājs nav pareizi atbildējis uz jautājumu (vienreizējs pirkums) — <b>300 '
        f'punkti</b>.\n4. Visu punktu reizinātājs 2x (vienreizējs pirkums) — <b>300 punkti</b>.\n\nTavs punktu '
        f'atlikums: <b>{db.query(UserStats).filter_by(id=1).first().points}</b>\n\n[!] Bonusi tiek pirkti uz visiem laikiem.\n\nJa vēlies iegādāties '
        f'vajadzīgo preci, nospied pogu ar atbilstošu preces numuru.',
        reply_markup=kb.shopItems)
    db.close()


@router.callback_query(F.data == 'firstItem', Prepare.shop)
async def shopFirst(callback: CallbackQuery, state: FSMContext):
    db = SessionLocal()
    if db.query(UserStats).filter_by(id=1).first().third_test_lives_amount >= 5:
        await callback.answer('Tu jau esi nopircis maksimālo bonusu skaitu!')
    else:
        if db.query(UserStats).filter_by(id=1).first().points >= 100:
            db.query(UserStats).filter_by(id=1).first().points -= 100
            db.query(UserStats).filter_by(id=1).first().third_test_lives_amount += 1
            await callback.answer(
                "Apsveicu, tu nopirki bonusu “+1 'dzīvība' pie testa - 10 jautājumu tests ar 3 “dzīvībām”“ par 100 punktiem!",
                show_alert=True)
            await shop_text(callback.message, state)
        elif db.query(UserStats).filter_by(id=1).first().points < 100:
            await callback.answer(
                'Tev nepietiek punktu, lai iegādātos šo preci!')
        else:
            await callback.answer('Radās kļūda, mēģiniet vēlreiz vēlāk!')
    db.close()


@router.callback_query(F.data == 'secondItem', Prepare.shop)
async def shopSecond(callback: CallbackQuery, state: FSMContext):
    db = SessionLocal()
    if db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated:
        await callback.answer('Tu jau esi nopircis šo bonusu!')
    else:
        if db.query(UserStats).filter_by(id=1).first().points >= 200:
            db.query(UserStats).filter_by(id=1).first().points -= 200
            db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated = True
            await callback.answer(
                'Apsveicu, tu nopirki bonusu “+1 mēģinājums ikdienas jautājumam“ par 200 punktiem!',
                show_alert=True)
            await shop_text(callback.message, state)
        elif db.query(UserStats).filter_by(id=1).first().points < 200:
            await callback.answer(
                'Tev nepietiek punktu, lai iegādātos šo preci!')
        else:
            await callback.answer('Radās kļūda, mēģiniet vēlreiz vēlāk!')
    db.close()


@router.callback_query(F.data == 'thirdItem', Prepare.shop)
async def shopThird(callback: CallbackQuery, state: FSMContext):
    db = SessionLocal()
    if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
        await callback.answer('Tu jau esi nopircis šo bonusu!')
    else:
        if db.query(UserStats).filter_by(id=1).first().points >= 300:
            db.query(UserStats).filter_by(id=1).first().points -= 300
            db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated = True
            await callback.answer(
                'Apsveicu, tu nopirki bonusu “Rādīt uzdevuma risinājumu, ja lietotājs nav pareizi atbildējis uz '
                'jautājumu“ par 300 punktiem!',
                show_alert=True)
            await shop_text(callback.message, state)
        elif db.query(UserStats).filter_by(id=1).first().points < 300:
            await callback.answer(
                'Tev nepietiek punktu, lai iegādātos šo preci!')
        else:
            await callback.answer('Radās kļūda, mēģiniet vēlreiz vēlāk!')
    db.close()


@router.callback_query(F.data == 'fourthItem', Prepare.shop)
async def shopFourth(callback: CallbackQuery, state: FSMContext):
    db = SessionLocal()
    if db.query(UserStats).filter_by(id=1).first().point_multiplier >= 2:
        await callback.answer('Tu jau esi nopircis šo bonusu!')
    else:
        if db.query(UserStats).filter_by(id=1).first().points >= 300:
            db.query(UserStats).filter_by(id=1).first().points -= 300
            db.query(UserStats).filter_by(id=1).first().point_multiplier = 2
            await callback.answer(
                'Apsveicu, tu nopirki bonusu “Visu punktu reizinātājs 2x“ par 300 punktiem!',
                show_alert=True)
            await shop_text(callback.message, state)
        elif db.query(UserStats).filter_by(id=1).first().points < 300:
            await callback.answer(
                'Tev nepietiek punktu, lai iegādātos šo preci!')
        else:
            await callback.answer('Radās kļūda, mēģiniet vēlreiz vēlāk!')
    db.close()


@router.message(Command('test', ignore_case=True))
async def cmd_start_test(message: Message, state: FSMContext):
    db = SessionLocal()
    await state.clear()
    resetValues()
    global lives
    lives = db.query(UserStats).filter_by(id=1).first().third_test_lives_amount
    await message.answer('Izvēlies sarakstā vajadzīgo priekšmetu.',
                         reply_markup=kb.subject)
    await state.set_state(Prepare.selectSubject)
    db.close()


@router.message(Prepare.selectSubject)
async def selectSubject(message: Message, state: FSMContext):
    db = SessionLocal()
    global selectedSubject
    global subjectValue
    bonusText = ''
    selectedSubject = message.text
    await message.answer(f"Izvēlētais priekšmets: {selectedSubject}",
                         reply_markup=types.ReplyKeyboardRemove())
    match selectedSubject:
        case 'Matemātika':
            subjectValue = 'math'
        case 'Fizika':
            subjectValue = 'physics'
        case 'Angļu valoda':
            subjectValue = 'english'
        case 'Vēsture':
            subjectValue = 'history'
        case _:
            await message.answer(
                f"Tāda priekšmeta man nav: {selectedSubject}\nIzvēlēts noklusējuma priekšmets: Matemātika"
            )
            subjectValue = 'math'
            selectedSubject = 'Matemātika'
    await state.set_state(Prepare.selectTestType)
    if db.query(UserStats).filter_by(id=1).first().third_test_lives_amount > 3:
        bonusAttempts = db.query(UserStats).filter_by(id=1).first().third_test_lives_amount
        bonusText = f" (Ar bonusu: {bonusAttempts} dzīvības)"
    await message.answer(
        f"Izvēlies testa veidu:\n1. 10 jautājumu tests. Beigās redzamas atbildes un risinājumi uz pareizi "
        f"atbildētiem jautājumiem.\n2. 1 jautājumu ātrs tests. Beigās redzamas atbilde un risinājums uz pareizi atbildētu "
        f"jautājumu.\n3. 10 jautājumu tests ar 3 “dzīvībām”{bonusText}. Par nepareizu atbildi -1 dzīve, kad paliek 0 dzīvības, "
        f"tests beidzas un nav redzamas atbildes un risinājumi. Vairāk punktu par pareizajām atbildēm pēc veiksmīgas "
        f"testa kārtošanas!",
        reply_markup=kb.testType)
    db.close()


@router.message(Prepare.selectTestType)
async def selectSubject(message: Message, state: FSMContext):
    global selectedTestType
    global testType
    selectedTestType = message.text
    await message.answer(f"Izvēlētais testa veids: {selectedTestType}",
                         reply_markup=types.ReplyKeyboardRemove())
    match message.text:
        case '1.':
            testType = 'firstTest'
            selectedTestType = '10 jautājumu tests'
        case '2.':
            testType = 'secondTest'
            selectedTestType = '1 jautājumu ātrs tests'
        case '3.':
            testType = 'thirdTest'
            selectedTestType = '10 jautājumu tests ar 3 “dzīvībām”'
        case _:
            await message.answer(
                f"Tāda testa veida man nav: {message.text}\nIzvēlēts noklusējuma testa veids: 1. 10 jautājumu tests. "
                f"Beigās redzamas atbildes un risinājumi uz pareizi atbildētiem jautājumiem."
            )
            testType = 'firstTest'
            selectedTestType = '1. 10 jautājumu tests. Beigās redzamas atbildes un pareizi risinājumi.'
    await message.answer(
        'Izvēlies testa sarežģītības līmeni:\n1. Viegls: vieglas pakāpes uzdevumi.\n2. Vidējais: vidējās pakāpes '
        'uzdevumi.\n3. Grūts: grūtās pakāpes uzdevumi.\n\nJo grūtāka sarežģītība, jo vairāk punktu par pareizām atbildēm!',
        reply_markup=kb.difficulty)
    await state.set_state(Prepare.selectDifficulty)


@router.message(Prepare.selectDifficulty)
async def selectSubject(message: Message, state: FSMContext):
    global selectedDifficulty
    global difficulty
    selectedDifficulty = message.text
    await message.answer(
        f"Izvēlētais sarežģītības līmenis: {selectedDifficulty}",
        reply_markup=types.ReplyKeyboardRemove())
    match message.text:
        case 'Viegls':
            difficulty = 'easy'
            selectedDifficulty = 'Viegls'
        case 'Vidējais':
            difficulty = 'normal'
            selectedDifficulty = 'Vidējais'
        case 'Grūtais':
            difficulty = 'hard'
            selectedDifficulty = 'Grūtais'
        case _:
            await message.answer(
                f"Tāda sarežģītības līmeni man nav: {message.text}\nIzvēlēts noklusējuma sarežģītības līmenis: Viegls."
            )
            difficulty = 'easy'
            selectedDifficulty = 'Viegls'
    await message.answer(
        f"Sāksim testu?\nIzvēlētais priekšmets: <b>{selectedSubject}</b>\nIzvēlētais testa veids: <b>{selectedTestType}"
        f"</b>\nIzvēlēta sarežģītība: <b>{selectedDifficulty}</b>\nIevadi komandu <b>/starttest</b>, lai sāktu testu!"
    )
    await state.set_state(Prepare.startTest)


@router.message(Command('starttest', ignore_case=True), Prepare.startTest)
async def defineSubject(message: Message, state: FSMContext):
    await state.clear()
    match subjectValue:
        case 'math':
            await state.set_state(MathTest.mathTestSelect)
            await startMathTest(message, state)
        case 'physics':
            await state.set_state(PhysicsTest.physicsTestSelect)
            await startPhysicsTest(message, state)
        case 'english':
            await state.set_state(EnglishTest.englishTestSelect)
            await startEnglishTest(message, state)
        case 'history':
            await state.set_state(HistoryTest.historyTestSelect)
            await startHistoryTest(message, state)
        case _:
            await message.answer("Radās kļūda. Mēģiniet vēlreiz <b>/test</b>.")


@router.message(MathTest.mathTestSelect)
async def startMathTest(message: Message, state: FSMContext):
    global randomQuestions
    global randomOptions
    await message.answer(
        'Pirms testa veikšanas iesakām atvērt lapu ar formulām.\nSaite: https://www.visc.gov.lv/lv/media/19301/download?attachment'
    )
    randomQuestions = random.sample(range(1, 21), 10)
    randomOptions = random.sample(range(0, 4), 4)
    await asyncio.sleep(2)
    if testType == 'firstTest' or testType == 'thirdTest':
        await m1Question(message, state)
    elif testType == 'secondTest':
        await mRandQuestion(message, state)


async def mRandQuestion(message: Message, state: FSMContext):
    db = SessionLocal()
    global spentTimeInTest
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[0])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[0])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(MathTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>Jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: "
                    f"{answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}"
                )
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>Jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: "
                    f"{answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}"
                )
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt "
                        f"pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini uzdevumu "
                        f"atrisināt pareizi vēlreiz."
                    )
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
    db.close()


async def m1Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    global spentTimeInTest
    global currentQuestionOrder
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[0])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[0])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(MathTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>1. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 1
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>1. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza"
                    f"</ins>: {answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>1. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza"
                    f"</ins>: {answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza"
                        f"</ins>: {answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini uzdevumu "
                        f"atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
    db.close()


async def m2Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[1])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[1])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[1])
    if not reviewMode:
        await state.set_state(MathTest.secondQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>2. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 2
        if CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>2. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: "
                f"{answerList[1]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                    f"{answerList[1]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu "
                    f"vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                    f"{answerList[1]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def m3Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[2])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[2])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[2])
    if not reviewMode:
        await state.set_state(MathTest.thirdQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>3. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 3
        if CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>3. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: "
                f"{answerList[2]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                    f"{answerList[2]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu "
                    f"vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                    f"{answerList[2]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def m4Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[3])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[3])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[3])
    if not reviewMode:
        await state.set_state(MathTest.fourthQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>4. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 4
        if CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>4. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins><ins>pareiza</ins>"
                f"</ins>: {answerList[3]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                    f"{answerList[3]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu "
                    f"vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                    f"{answerList[3]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def m5Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[4])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[4])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[4])
    if not reviewMode:
        await state.set_state(MathTest.fifthQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>5. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 5
        if CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>5. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def m6Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[5])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[5])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[5])
    if not reviewMode:
        await state.set_state(MathTest.sixthQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>6. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 6
        if CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>6. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def m7Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[6])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[6])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[6])
    if not reviewMode:
        await state.set_state(MathTest.seventhQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>7. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 7
        if CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>7. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def m8Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[7])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[7])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[7])
    if not reviewMode:
        await state.set_state(MathTest.eighthQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>8. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 8
        if CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>8. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def m9Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[8])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[8])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[8])
    if not reviewMode:
        await state.set_state(MathTest.ninthQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>9. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 9
        if CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>9. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def m10Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    mathQuestions = dict
    match difficulty:
        case 'easy':
            mathQuestions = next(q for q in mathEasyQuestions
                                 if q['id'] == randomQuestions[9])
        case 'normal':
            mathQuestions = next(q for q in mathMediumQuestions
                                 if q['id'] == randomQuestions[9])
        case 'hard':
            mathQuestions = next(q for q in mathHardQuestions
                                 if q['id'] == randomQuestions[9])
    if not reviewMode:
        await state.set_state(MathTest.tenthQ)
        keyboard = createInlineKeyboard(
            mathQuestions['options'][randomOptions[0]],
            mathQuestions['options'][randomOptions[1]],
            mathQuestions['options'][randomOptions[2]],
            mathQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>10. jautājums:</b>\n{mathQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 10
        if CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>10. jautājums:</b>\n{mathQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {mathQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {mathQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>\n{mathQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


@router.message(PhysicsTest.physicsTestSelect)
async def startPhysicsTest(message: Message, state: FSMContext):
    global randomQuestions
    global randomOptions
    await message.answer(
        'Pirms testa veikšanas iesakām atvērt lapu ar formulām.\nSaite: https://www.visc.gov.lv/lv/media/487/download?attachment'
    )
    randomQuestions = random.sample(range(1, 21), 10)
    randomOptions = random.sample(range(0, 4), 4)
    await asyncio.sleep(2)
    if testType == 'firstTest' or testType == 'thirdTest':
        await p1Question(message, state)
    elif testType == 'secondTest':
        await pRandQuestion(message, state)


async def pRandQuestion(message: Message, state: FSMContext):
    db = SessionLocal()
    global spentTimeInTest
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[0])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[0])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(PhysicsTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>Jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>Jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
    db.close()


async def p1Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    global spentTimeInTest
    global currentQuestionOrder
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[0])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[0])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(PhysicsTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>1. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 1
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>1. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>1. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
    db.close()

async def p2Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[1])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[1])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[1])
    if not reviewMode:
        await state.set_state(PhysicsTest.secondQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>2. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 2
        if CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>2. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[1]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[1]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[1]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def p3Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[2])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[2])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[2])
    if not reviewMode:
        await state.set_state(PhysicsTest.thirdQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>3. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 3
        if CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>3. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[2]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[2]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[2]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def p4Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[3])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[3])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[3])
    if not reviewMode:
        await state.set_state(PhysicsTest.fourthQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>4. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 4
        if CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>4. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins><ins>pareiza</ins></ins>: {answerList[3]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[3]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[3]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def p5Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[4])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[4])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[4])
    if not reviewMode:
        await state.set_state(PhysicsTest.fifthQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>5. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 5
        if CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>5. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>5. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>5. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def p6Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[5])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[5])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[5])
    if not reviewMode:
        await state.set_state(PhysicsTest.sixthQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>6. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 6
        if CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>6. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def p7Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[6])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[6])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[6])
    if not reviewMode:
        await state.set_state(PhysicsTest.seventhQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>7. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 7
        if CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>7. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def p8Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[7])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[7])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[7])
    if not reviewMode:
        await state.set_state(PhysicsTest.eighthQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>8. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 8
        if CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>8. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def p9Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[8])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[8])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[8])
    if not reviewMode:
        await state.set_state(PhysicsTest.ninthQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>9. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 9
        if CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>9. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def p10Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    physicsQuestions = dict
    match difficulty:
        case 'easy':
            physicsQuestions = next(q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[9])
        case 'normal':
            physicsQuestions = next(q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[9])
        case 'hard':
            physicsQuestions = next(q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[9])
    if not reviewMode:
        await state.set_state(PhysicsTest.tenthQ)
        keyboard = createInlineKeyboard(
            physicsQuestions['options'][randomOptions[0]],
            physicsQuestions['options'][randomOptions[1]],
            physicsQuestions['options'][randomOptions[2]],
            physicsQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>10. jautājums:</b>\n{physicsQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 10
        if CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>10. jautājums:</b>\n{physicsQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {physicsQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>n{physicsQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


@router.message(EnglishTest.englishTestSelect)
async def startEnglishTest(message: Message, state: FSMContext):
    global randomQuestions
    global randomOptions
    randomQuestions = random.sample(range(1, 21), 10)
    randomOptions = random.sample(range(0, 4), 4)
    if testType == 'firstTest' or testType == 'thirdTest':
        await e1Question(message, state)
    elif testType == 'secondTest':
        await eRandQuestion(message, state)


async def eRandQuestion(message: Message, state: FSMContext):
    db = SessionLocal()
    global spentTimeInTest
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[0])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[0])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(EnglishTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>Jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}"
                )
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>Jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}"
                )
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
    db.close()


async def e1Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    global spentTimeInTest
    global currentQuestionOrder
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[0])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[0])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(EnglishTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>1. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 1
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>1. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>1. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
    db.close()


async def e2Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[1])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[1])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[1])
    if not reviewMode:
        await state.set_state(EnglishTest.secondQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>2. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 2
        if CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>2. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[1]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[1]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[1]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e3Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[2])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[2])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[2])
    if not reviewMode:
        await state.set_state(EnglishTest.thirdQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>3. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 3
        if CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>3. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[2]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[2]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[2]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e4Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[3])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[3])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[3])
    if not reviewMode:
        await state.set_state(EnglishTest.fourthQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>4. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 4
        if CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>4. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins><ins>pareiza</ins></ins>: {answerList[3]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[3]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[3]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e5Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[4])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[4])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[4])
    if not reviewMode:
        await state.set_state(EnglishTest.fifthQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>5. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 5
        if CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>5. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>5. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>5. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e6Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[5])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[5])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[5])
    if not reviewMode:
        await state.set_state(EnglishTest.sixthQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>6. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 6
        if CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>6. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e7Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[6])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[6])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[6])
    if not reviewMode:
        await state.set_state(EnglishTest.seventhQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>7. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 7
        if CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>7. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e8Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[7])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[7])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[7])
    if not reviewMode:
        await state.set_state(EnglishTest.eighthQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>8. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 8
        if CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>8. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def e9Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[8])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[8])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[8])
    if not reviewMode:
        await state.set_state(EnglishTest.ninthQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>9. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 9
        if CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>9. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()

async def e10Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    englishQuestions = dict
    match difficulty:
        case 'easy':
            englishQuestions = next(q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[9])
        case 'normal':
            englishQuestions = next(q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[9])
        case 'hard':
            englishQuestions = next(q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[9])
    if not reviewMode:
        await state.set_state(EnglishTest.tenthQ)
        keyboard = createInlineKeyboard(
            englishQuestions['options'][randomOptions[0]],
            englishQuestions['options'][randomOptions[1]],
            englishQuestions['options'][randomOptions[2]],
            englishQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>10. jautājums:</b>\n{englishQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 10
        if CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>10. jautājums:</b>\n{englishQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {englishQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {englishQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>n{englishQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


@router.message(HistoryTest.historyTestSelect)
async def startHistoryTest(message: Message, state: FSMContext):
    global randomQuestions
    global randomOptions
    randomQuestions = random.sample(range(1, 21), 10)
    randomOptions = random.sample(range(0, 4), 4)
    if testType == 'firstTest' or testType == 'thirdTest':
        await h1Question(message, state)
    elif testType == 'secondTest':
        await hRandQuestion(message, state)


async def hRandQuestion(message: Message, state: FSMContext):
    db = SessionLocal()
    global spentTimeInTest
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[0])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[0])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(HistoryTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>Jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}"
                )
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>Jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}"
                )
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz."
                    )
    db.close()


async def h1Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    global spentTimeInTest
    global currentQuestionOrder
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[0])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[0])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[0])
    if not reviewMode:
        await state.set_state(HistoryTest.firstQ)
        spentTimeInTest = time.time()
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await message.answer(
            f"<b>1. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 1
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>1. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>1. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                    reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>1. Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>1. Jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[0]}.\n\nPamēģini uzdevumu atrisināt pareizi vēlreiz.",
                        reply_markup=kb.reviewKeyboard)
    db.close()


async def h2Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[1])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[1])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[1])
    if not reviewMode:
        await state.set_state(HistoryTest.secondQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>2. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 2
        if CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>2. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[1]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is2QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[1]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>2. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[1]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h3Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[2])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[2])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[2])
    if not reviewMode:
        await state.set_state(HistoryTest.thirdQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>3. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 3
        if CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>3. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[2]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is3QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[2]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>3. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[2]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h4Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[3])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[3])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[3])
    if not reviewMode:
        await state.set_state(HistoryTest.fourthQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>4. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 4
        if CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>4. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins><ins>pareiza</ins></ins>: {answerList[3]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is4QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[3]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>4. jautājums:</b>\n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[3]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h5Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[4])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[4])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[4])
    if not reviewMode:
        await state.set_state(HistoryTest.fifthQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>5. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 5
        if CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>5. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is5QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>5. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>5. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[4]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h6Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[5])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[5])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[5])
    if not reviewMode:
        await state.set_state(HistoryTest.sixthQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>6. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 6
        if CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>6. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is6QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>6. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[5]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h7Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[6])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[6])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[6])
    if not reviewMode:
        await state.set_state(HistoryTest.seventhQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>7. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 7
        if CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>7. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is7QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>7. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[6]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h8Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[7])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[7])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[7])
    if not reviewMode:
        await state.set_state(HistoryTest.eighthQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>8. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 8
        if CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>8. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is8QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>8. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[7]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h9Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[8])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[8])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[8])
    if not reviewMode:
        await state.set_state(HistoryTest.ninthQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>9. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 9
        if CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>9. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is9QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>9. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[8]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def h10Question(message: Message, state: FSMContext):
    db = SessionLocal()
    global currentQuestion
    historyQuestions = dict
    match difficulty:
        case 'easy':
            historyQuestions = next(q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[9])
        case 'normal':
            historyQuestions = next(q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[9])
        case 'hard':
            historyQuestions = next(q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[9])
    if not reviewMode:
        await state.set_state(HistoryTest.tenthQ)
        keyboard = createInlineKeyboard(
            historyQuestions['options'][randomOptions[0]],
            historyQuestions['options'][randomOptions[1]],
            historyQuestions['options'][randomOptions[2]],
            historyQuestions['options'][randomOptions[3]])
        currentQuestion = await currentQuestion.edit_text(
            f"<b>10. jautājums:</b>\n{historyQuestions['question']}",
            reply_markup=keyboard)
    elif reviewMode:
        global currentQuestionOrder
        currentQuestionOrder = 10
        if CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            currentQuestion = await currentQuestion.edit_text(
                f"<b>10. jautājums:</b>\n{historyQuestions['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {historyQuestions['explanation']}",
                reply_markup=kb.reviewKeyboard)
        elif not CorrectlyAnsweredTenQuestions.is10QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPaskaidrojums: {historyQuestions['explanation']}\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>10. jautājums:</b>n{historyQuestions['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: {answerList[9]}.\n\nPamēģini atrisināt uzdevumu vēlreiz pareizi!",
                    reply_markup=kb.reviewKeyboard)
    db.close()


async def TestEnd(message: Message, state: FSMContext):
    db = SessionLocal()
    await state.set_state(Prepare.testEnd)
    global spentTimeInTest
    global currentQuestion
    pointMultiplier = db.query(UserStats).filter_by(id=1).first().point_multiplier
    timeSpent = ''
    points = 0
    currentDateTime = datetime.now()
    adjustedTime = currentDateTime + timedelta(hours=3)
    fixedCurrentDateTime = adjustedTime.strftime('%Y-%m-%d %H:%M:%S')
    if difficulty == 'easy':
        points = round((correctAnswersInTest / 2) * pointMultiplier, 1)
    elif difficulty == 'normal':
        points = round(correctAnswersInTest * pointMultiplier, 1)
    elif difficulty == 'hard':
        points = round((correctAnswersInTest * 2) * pointMultiplier, 1)
    if testType == 'firstTest' or testType == 'secondTest' or (
            testType == 'thirdTest' and lives > 0):
        if spentTimeInTest is not None:
            end_time = time.time()
            elapsed_time = end_time - spentTimeInTest
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        percentages = round(
            (correctAnswersInTest /
             (correctAnswersInTest + wrongAnswersInTest)) * 100)
        timeSpent = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        if testType == 'thirdTest':
            points *= 2
        db.query(UserStats).filter_by(id=1).first().correct_answers += correctAnswersInTest
        db.query(UserStats).filter_by(id=1).first().wrong_answers += wrongAnswersInTest
        db.query(UserStats).filter_by(id=1).first().points += points
        date_time_list = json.loads(db.query(UserStats).filter_by(id=1).first().date_time)
        date_time_list.append(str(fixedCurrentDateTime))
        db.query(UserStats).filter_by(id=1).first().date_time = json.dumps(date_time_list)
        user_history = db.query(UserHistory).filter_by(user_id=1).first()
        subject_list = json.loads(user_history.subject)
        difficulty_list = json.loads(user_history.difficulty)
        subject_list.append(selectedSubject)
        difficulty_list.append(selectedDifficulty)
        user_history.subject = json.dumps(subject_list)
        user_history.difficulty = json.dumps(difficulty_list)
        if selectedTestType != '':
            db["test_mode"].append(selectedTestType)
        elif selectedTestType == '':
            db["test_mode"].append("Ikdienas jautājums")
        db["correct_answers_in_test"].append(correctAnswersInTest)
        db["wrong_answers_in_test"].append(wrongAnswersInTest)
        db["percentages"].append(percentages)
        db["test_time"].append(timeSpent)
        db["obtained_points"].append(points)
        await currentQuestion.edit_text(
            f"Apsveicu, tu pabeidzi testu!\nPareizās atbildes: <b>{correctAnswersInTest}</b>\nNepareizas atbildes: <b>{wrongAnswersInTest}</b>\nProcentu izpilde: <b>{percentages}%</b>\nLaiks: <b>{timeSpent}</b>\nPar testa kārtošanu tu saņēmi <b>{points}</b> punktus!\n\nIevadi <b>/review</b>, lai apskatītu uzdevumus un risinājumus.",
            reply_markup=kb.tryAgain)
        currentQuestion = ''
    elif testType == 'thirdTest' and lives <= 0:
        points = 0
        if spentTimeInTest is not None:
            end_time = time.time()
            elapsed_time = end_time - spentTimeInTest
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        percentages = round((correctAnswersInTest / 10) * 100)
        timeSpent = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        db.query(UserStats).filter_by(id=1).first().correct_answers += correctAnswersInTest
        db.query(UserStats).filter_by(id=1).first().wrong_answers += wrongAnswersInTest
        date_time_list = json.loads(db.query(UserStats).filter_by(id=1).first().date_time)
        date_time_list.append(str(fixedCurrentDateTime))
        db.query(UserStats).filter_by(id=1).first().date_time = json.dumps(date_time_list)
        db["subject"].append(selectedSubject)
        db["difficulty"].append(selectedDifficulty)
        user_history = db.query(UserHistory).filter_by(user_id=1).first()
        if selectedTestType != '':
            user_history.test_mode = json.dumps(json.loads(user_history.test_mode) + [selectedTestType])
        else:
            user_history.test_mode = json.dumps(json.loads(user_history.test_mode) + ["Ikdienas jautājums"])
            user_history.correct_answers_in_test = json.dumps(json.loads(user_history.correct_answers_in_test) + [correctAnswersInTest])
            user_history.wrong_answers_in_test = json.dumps(json.loads(user_history.wrong_answers_in_test) + [wrongAnswersInTest])
            user_history.percentages = json.dumps(json.loads(user_history.percentages) + [percentages])
            user_history.test_time = json.dumps(json.loads(user_history.test_time) + [timeSpent])
            user_history.obtained_points = json.dumps(json.loads(user_history.obtained_points) + [points])
        wrongQuestionNumber = db.query(UserStats).filter_by(id=1).first().third_test_lives_amount
        await currentQuestion.edit_text(
            f"Diemžēl tu nepareizi atbildēji uz {wrongQuestionNumber} jautājumiem, un esi izkritis no testa. Pamēģini vēlreiz!\nPareizās atbildes: <b>{correctAnswersInTest}</b>\nNepareizas atbildes: <b>{wrongAnswersInTest}</b>\nProcentu izpilde: <b>{percentages}%</b>\nLaiks: <b>{timeSpent}</b>",
            reply_markup=kb.tryAgain)
        currentQuestion = ''
    elif dailyTaskActive:
        if spentTimeInTest is not None:
            end_time = time.time()
            elapsed_time = end_time - spentTimeInTest
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        percentages = round(correctAnswersInTest * 100)
        timeSpent = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        points *= 5
        db.query(UserStats).filter_by(id=1).first().correct_answers += correctAnswersInTest
        db.query(UserStats).filter_by(id=1).first().wrong_answers += wrongAnswersInTest
        db.query(UserStats).filter_by(id=1).first().points += points
        date_time_list = json.loads(db.query(UserHistory).filter_by(id=1).first().date_time)
        date_time_list.append(str(fixedCurrentDateTime))
        db.query(UserHistory).filter_by(id=1).first().date_time = json.dumps(date_time_list)
        user_history = db.query(UserHistory).filter_by(user_id=1).first()
        user_history.subject = json.dumps(json.loads(user_history.subject) + [selectedSubject])
        user_history.difficulty = json.dumps(json.loads(user_history.difficulty) + [selectedDifficulty])
        if selectedTestType != '':
            user_history.test_mode = json.dumps(json.loads(user_history.test_mode) + [selectedTestType])
        else:
            user_history.test_mode = json.dumps(json.loads(user_history.test_mode) + ["Ikdienas jautājums"])
        user_history.correct_answers_in_test = json.dumps(json.loads(user_history.correct_answers_in_test) + [correctAnswersInTest])
        user_history.wrong_answers_in_test = json.dumps(json.loads(user_history.wrong_answers_in_test) + [wrongAnswersInTest])
        user_history.percentages = json.dumps(json.loads(user_history.percentages) + [percentages])
        user_history.test_time = json.dumps(json.loads(user_history.test_time) + [timeSpent])
        user_history.obtained_points = json.dumps(json.loads(user_history.obtained_points) + [points])
        if not db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated:
            db.query(UserStats).filter_by(id=1).first().completed += 1
            await currentQuestion.edit_text(
                f"Apsveicu, tu atbildēji uz ikdienas jautājumu!\nPareizās atbildes: <b>{correctAnswersInTest}</b>\nNepareizas atbildes: <b>{wrongAnswersInTest}</b>\nProcentu izpilde: <b>{percentages}%</b>\nLaiks: <b>{timeSpent}</b>\nPar testa kārtošanu tu saņēmi <b>{points}</b> punktus!\n\nIevadi <b>/review</b>, lai apskatītu uzdevumu un risinājumu."
            )
        elif db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated:
            db.query(UserStats).filter_by(id=1).first().completed += 1
            await currentQuestion.edit_text(
                f"Apsveicu, tu atbildēji uz ikdienas jautājumu!\nPareizās atbildes: <b>{correctAnswersInTest}</b>\nNepareizas atbildes: <b>{wrongAnswersInTest}</b>\nProcentu izpilde: <b>{percentages}%</b>\nLaiks: <b>{timeSpent}</b>\nPar testa kārtošanu tu saņēmi <b>{points}</b> punktus!\n\nIevadi <b>/review</b>, lai apskatītu uzdevumu un risinājumu.",
                reply_markup=kb.tryAgain)
        currentQuestion = ''
    list_length = len(json.loads(db.query(UserHistory).filter_by(user_id=1).first().date_time))
    if list_length > 20:
        user_history = db.query(UserHistory).filter_by(user_id=1).first()
        user_history.date_time = json.dumps(json.loads(user_history.date_time)[-20:])
        user_history.subject = json.dumps(json.loads(user_history.subject)[-20:])
        user_history.difficulty = json.dumps(json.loads(user_history.difficulty)[-20:])
        user_history.test_mode = json.dumps(json.loads(user_history.test_mode)[-20:])
        user_history.correct_answers_in_test = json.dumps(json.loads(user_history.correct_answers_in_test)[-20:])
        user_history.wrong_answers_in_test = json.dumps(json.loads(user_history.wrong_answers_in_test)[-20:])
        user_history.percentages = json.dumps(json.loads(user_history.percentages)[-20:])
        user_history.test_time = json.dumps(json.loads(user_history.test_time)[-20:])
        user_history.obtained_points = json.dumps(json.loads(user_history.obtained_points)[-20:])
        db.commit()
    db.close()


@router.message(Command('daily', ignore_case=True))
async def dailyTask(message: Message, state: FSMContext):
    db = SessionLocal()
    global randomQuestion
    global spentTimeInTest
    global currentQuestion
    global dailyTaskActive
    global randomQuestions
    global randomOptions
    global difficulty
    global selectedSubject
    global selectedDifficulty
    global selectedTestType
    if not reviewMode:
        await state.clear()
        resetValues()
        if db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated:
            if db.query(UserStats).filter_by(id=1).first().completed < 2:
                await message.answer(
                    "Tev ir iespēja atbildēt uz nejaušu ikdienas jautājumu, lai saņemtu punktus!"
                )
                await asyncio.sleep(2)
                dailyTaskActive = True
                randomQuestions = random.sample(range(1, 21), 1)
                randomOptions = random.sample(range(0, 4), 4)
                subjectList = ['math', 'physics', 'english', 'history']
                difficultyList = ['easy', 'normal', 'hard']
                randomSubject = random.choice(subjectList)
                randomDifficulty = random.choice(difficultyList)
                match randomSubject:
                    case 'math':
                        await state.set_state(MathTest.firstQ)
                        selectedSubject = 'Matemātika'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in mathEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in mathMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in mathHardQuestions
                                    if q['id'] == randomQuestions[0])
                    case 'physics':
                        await state.set_state(PhysicsTest.firstQ)
                        selectedSubject = 'Fizika'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[0])
                    case 'english':
                        await state.set_state(EnglishTest.firstQ)
                        selectedSubject = 'Angļu valoda'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[0])
                    case 'history':
                        await state.set_state(HistoryTest.firstQ)
                        selectedSubject = 'Vēsture'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[0])
                spentTimeInTest = time.time()
                keyboard = createInlineKeyboard(
                    randomQuestion['options'][randomOptions[0]],
                    randomQuestion['options'][randomOptions[1]],
                    randomQuestion['options'][randomOptions[2]],
                    randomQuestion['options'][randomOptions[3]])
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{randomQuestion['question']}",
                    reply_markup=keyboard)
            else:
                dailyTaskActive = False
                await message.answer(
                    "Šodien tu jau atbildēji uz ikdienas jautājumu. Nāc rīt, mēs tev sagatavosim jaunu jautājumu!"
                )
        elif not db.query(UserStats).filter_by(id=1).first().second_attempt_daily_activated:
            if db.query(UserStats).filter_by(id=1).first().completed < 1:
                await message.answer(
                    "Tev ir iespēja atbildēt uz nejaušu ikdienas jautājumu, lai saņemtu punktus!"
                )
                await asyncio.sleep(2)
                dailyTaskActive = True
                randomQuestions = random.sample(range(1, 21), 1)
                randomOptions = random.sample(range(0, 4), 4)
                subjectList = ['math', 'physics', 'english', 'history']
                difficultyList = ['easy', 'normal', 'hard']
                randomSubject = random.choice(subjectList)
                randomDifficulty = random.choice(difficultyList)
                match randomSubject:
                    case 'math':
                        await state.set_state(MathTest.firstQ)
                        selectedSubject = 'Matemātika'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in mathEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in mathMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in mathHardQuestions
                                    if q['id'] == randomQuestions[0])
                    case 'physics':
                        await state.set_state(PhysicsTest.firstQ)
                        selectedSubject = 'Fizika'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in physicsEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in physicsMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in physicsHardQuestions
                                    if q['id'] == randomQuestions[0])
                    case 'english':
                        await state.set_state(EnglishTest.firstQ)
                        selectedSubject = 'Angļu valoda'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in englishEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in englishMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in englishHardQuestions
                                    if q['id'] == randomQuestions[0])
                    case 'history':
                        await state.set_state(HistoryTest.firstQ)
                        selectedSubject = 'Vēsture'
                        match randomDifficulty:
                            case 'easy':
                                difficulty = 'easy'
                                selectedDifficulty = 'Viegls'
                                randomQuestion = next(
                                    q for q in historyEasyQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'normal':
                                difficulty = 'normal'
                                selectedDifficulty = 'Vidējais'
                                randomQuestion = next(
                                    q for q in historyMediumQuestions
                                    if q['id'] == randomQuestions[0])
                            case 'hard':
                                difficulty = 'hard'
                                selectedDifficulty = 'Grūtais'
                                randomQuestion = next(
                                    q for q in historyHardQuestions
                                    if q['id'] == randomQuestions[0])
                spentTimeInTest = time.time()
                keyboard = createInlineKeyboard(
                    randomQuestion['options'][randomOptions[0]],
                    randomQuestion['options'][randomOptions[1]],
                    randomQuestion['options'][randomOptions[2]],
                    randomQuestion['options'][randomOptions[3]])
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{randomQuestion['question']}",
                    reply_markup=keyboard)
            else:
                dailyTaskActive = False
                await message.answer(
                    "Šodien tu jau atbildēji uz ikdienas jautājumu. Nāc rīt, mēs tev sagatavosim jaunu jautājumu!"
                )
    elif reviewMode:
        if CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if currentQuestion == '':
                currentQuestion = await message.answer(
                    f"<b>Jautājums:</b>\n{randomQuestion['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: "
                    f"{answerList[0]}.\n\nPaskaidrojums: {randomQuestion['explanation']}"
                )
            elif currentQuestion != '':
                currentQuestion = await currentQuestion.edit_text(
                    f"<b>Jautājums:</b>\n{randomQuestion['question']}\n\nMalacis, tava atbilde ir <ins>pareiza</ins>: "
                    f"{answerList[0]}.\n\nPaskaidrojums: {randomQuestion['explanation']}"
                )
        elif not CorrectlyAnsweredTenQuestions.is1QuestionAnsweredCorrectly:
            if db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{randomQuestion['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPaskaidrojums: {randomQuestion['explanation']}"
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{randomQuestion['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}.\n\nPaskaidrojums: {randomQuestion['explanation']}"
                    )
            elif not db.query(UserStats).filter_by(id=1).first().explanation_for_wrong_answers_activated:
                if currentQuestion == '':
                    currentQuestion = await message.answer(
                        f"<b>Jautājums:</b>\n{randomQuestion['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}."
                    )
                elif currentQuestion != '':
                    currentQuestion = await currentQuestion.edit_text(
                        f"<b>Jautājums:</b>\n{randomQuestion['question']}\n\nTava atbilde ir <ins>nepareiza</ins>: "
                        f"{answerList[0]}."
                    )
        tryTestAgainResetValues()
    db.close()


@router.message(Command('review', ignore_case=True), Prepare.testEnd)
async def reviewQuestions(message: Message, state: FSMContext):
    await state.set_state(Prepare.review)
    global reviewMode
    reviewMode = True
    match subjectValue:
        case 'math':
            if testType == 'firstTest':
                await m1Question(message, state)
            elif testType == 'secondTest':
                await mRandQuestion(message, state)
            elif testType == 'thirdTest' and lives > 0:
                await m1Question(message, state)
        case 'physics':
            if testType == 'firstTest':
                await p1Question(message, state)
            elif testType == 'secondTest':
                await pRandQuestion(message, state)
            elif testType == 'thirdTest' and lives > 0:
                await p1Question(message, state)
        case 'english':
            if testType == 'firstTest':
                await e1Question(message, state)
            elif testType == 'secondTest':
                await eRandQuestion(message, state)
            elif testType == 'thirdTest' and lives > 0:
                await e1Question(message, state)
        case 'history':
            if testType == 'firstTest':
                await h1Question(message, state)
            elif testType == 'secondTest':
                await hRandQuestion(message, state)
            elif testType == 'thirdTest' and lives > 0:
                await h1Question(message, state)
    if dailyTaskActive:
        await dailyTask(message, state)


@router.callback_query(F.data == 'goBack', Prepare.history)
async def back(callback: CallbackQuery, state: FSMContext):
    global stopPage
    global currentBatch
    if currentBatch > 0:
        currentBatch -= 1
        stopPage.set()
        await showBatches(callback.message, state)
    elif currentBatch <= 0:
        await callback.answer('Tu jau tā esi pirmajā lappusē.')


@router.callback_query(F.data == 'goForward', Prepare.history)
async def forward(callback: CallbackQuery, state: FSMContext):
    global stopPage
    global currentBatch
    if currentBatch < (totalBatches - 1):
        currentBatch += 1
        stopPage.set()
        await showBatches(callback.message, state)
    elif currentBatch >= (totalBatches - 1):
        await callback.answer('Tu jau tā esi pēdējā lappusē.')


@router.callback_query(F.data == 'deleteHistory', Prepare.history)
async def deleteHistory(callback: CallbackQuery, state: FSMContext):
    global historyPage
    db = SessionLocal()
    user_history = db.query(UserHistory).filter_by(user_id=1).first()
    if user_history:
        user_history.date_time = "[]"
        user_history.subject = "[]"
        user_history.difficulty = "[]"
        user_history.test_mode = "[]"
        user_history.correct_answers_in_test = "[]"
        user_history.wrong_answers_in_test = "[]"
        user_history.percentages = "[]"
        user_history.test_time = "[]"
        user_history.obtained_points = "[]"
        db.commit()
    db.close()
    await historyPage.edit_text('Vēsture ir dzēsta.')


@router.callback_query(F.data == 'back', Prepare.review)
async def goBack(callback: CallbackQuery, state: FSMContext):
    if currentQuestionOrder > 1:
        callFunction = currentQuestionOrder - 1
        subLetter = ''
        match subjectValue:
            case 'math':
                subLetter = 'm'
            case 'physics':
                subLetter = 'p'
            case 'english':
                subLetter = 'e'
            case 'history':
                subLetter = 'h'
        function_name = f"{subLetter}{callFunction}Question"
        question_function = globals()[function_name]
        await question_function(callback.message, state)
    elif currentQuestionOrder <= 1:
        await callback.answer('Tu jau tā esi pirmajā jautājumā.')


@router.callback_query(F.data == 'forward', Prepare.review)
async def goForward(callback: CallbackQuery, state: FSMContext):
    if currentQuestionOrder < 10:
        callFunction = currentQuestionOrder + 1
        subLetter = ''
        match subjectValue:
            case 'math':
                subLetter = 'm'
            case 'physics':
                subLetter = 'p'
            case 'english':
                subLetter = 'e'
            case 'history':
                subLetter = 'h'
        function_name = f"{subLetter}{callFunction}Question"
        question_function = globals()[function_name]
        await question_function(callback.message, state)
    elif currentQuestionOrder >= 10:
        await callback.answer('Tu jau tā esi pēdējā jautājumā.')


@router.callback_query(F.data == 'tryTestAgain', Prepare.testEnd)
@router.callback_query(F.data == 'tryTestAgain', Prepare.review)
async def tryTest(callback: CallbackQuery, state: FSMContext):
    db = SessionLocal()
    global lives
    lives = db.query(UserStats).filter_by(id=1).first().third_test_lives_amount
    if dailyTaskActive:
        await dailyTask(callback.message, state)
        return
    tryTestAgainResetValues()
    await state.clear()
    match subjectValue:
        case 'math':
            await startMathTest(callback.message, state)
        case 'physics':
            await startPhysicsTest(callback.message, state)
        case 'english':
            await startEnglishTest(callback.message, state)
        case 'history':
            await startHistoryTest(callback.message, state)
    db.close()


@router.callback_query(F.data == 'a')
async def answerA(message: Message, state: FSMContext):
    global selectedAnswer
    selectedAnswer = 'a'
    current_state = await state.get_state()
    match current_state:
        case MathTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                if passed.is_set():
                    await m2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                await TestEnd(message, state)
        case MathTest.secondQ:
            await answerHandler('math', randomQuestions[1], randomOptions[0],
                                2, message, state)
            if passed.is_set():
                await m3Question(message, state)
        case MathTest.thirdQ:
            await answerHandler('math', randomQuestions[2], randomOptions[0],
                                3, message, state)
            if passed.is_set():
                await m4Question(message, state)
        case MathTest.fourthQ:
            await answerHandler('math', randomQuestions[3], randomOptions[0],
                                4, message, state)
            if passed.is_set():
                await m5Question(message, state)
        case MathTest.fifthQ:
            await answerHandler('math', randomQuestions[4], randomOptions[0],
                                5, message, state)
            if passed.is_set():
                await m6Question(message, state)
        case MathTest.sixthQ:
            await answerHandler('math', randomQuestions[5], randomOptions[0],
                                6, message, state)
            if passed.is_set():
                await m7Question(message, state)
        case MathTest.seventhQ:
            await answerHandler('math', randomQuestions[6], randomOptions[0],
                                7, message, state)
            if passed.is_set():
                await m8Question(message, state)
        case MathTest.eighthQ:
            await answerHandler('math', randomQuestions[7], randomOptions[0],
                                8, message, state)
            if passed.is_set():
                await m9Question(message, state)
        case MathTest.ninthQ:
            await answerHandler('math', randomQuestions[8], randomOptions[0],
                                9, message, state)
            if passed.is_set():
                await m10Question(message, state)
        case MathTest.tenthQ:
            await answerHandler('math', randomQuestions[9], randomOptions[0],
                                10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case PhysicsTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                if passed.is_set():
                    await p2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                await TestEnd(message, state)
        case PhysicsTest.secondQ:
            await answerHandler('physics', randomQuestions[1],
                                randomOptions[0], 2, message, state)
            if passed.is_set():
                await p3Question(message, state)
        case PhysicsTest.thirdQ:
            await answerHandler('physics', randomQuestions[2],
                                randomOptions[0], 3, message, state)
            if passed.is_set():
                await p4Question(message, state)
        case PhysicsTest.fourthQ:
            await answerHandler('physics', randomQuestions[3],
                                randomOptions[0], 4, message, state)
            if passed.is_set():
                await p5Question(message, state)
        case PhysicsTest.fifthQ:
            await answerHandler('physics', randomQuestions[4],
                                randomOptions[0], 5, message, state)
            if passed.is_set():
                await p6Question(message, state)
        case PhysicsTest.sixthQ:
            await answerHandler('physics', randomQuestions[5],
                                randomOptions[0], 6, message, state)
            if passed.is_set():
                await p7Question(message, state)
        case PhysicsTest.seventhQ:
            await answerHandler('physics', randomQuestions[6],
                                randomOptions[0], 7, message, state)
            if passed.is_set():
                await p8Question(message, state)
        case PhysicsTest.eighthQ:
            await answerHandler('physics', randomQuestions[7],
                                randomOptions[0], 8, message, state)
            if passed.is_set():
                await p9Question(message, state)
        case PhysicsTest.ninthQ:
            await answerHandler('physics', randomQuestions[8],
                                randomOptions[0], 9, message, state)
            if passed.is_set():
                await p10Question(message, state)
        case PhysicsTest.tenthQ:
            await answerHandler('physics', randomQuestions[9],
                                randomOptions[0], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case EnglishTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                if passed.is_set():
                    await e2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                await TestEnd(message, state)
        case EnglishTest.secondQ:
            await answerHandler('english', randomQuestions[1],
                                randomOptions[0], 2, message, state)
            if passed.is_set():
                await e3Question(message, state)
        case EnglishTest.thirdQ:
            await answerHandler('english', randomQuestions[2],
                                randomOptions[0], 3, message, state)
            if passed.is_set():
                await e4Question(message, state)
        case EnglishTest.fourthQ:
            await answerHandler('english', randomQuestions[3],
                                randomOptions[0], 4, message, state)
            if passed.is_set():
                await e5Question(message, state)
        case EnglishTest.fifthQ:
            await answerHandler('english', randomQuestions[4],
                                randomOptions[0], 5, message, state)
            if passed.is_set():
                await e6Question(message, state)
        case EnglishTest.sixthQ:
            await answerHandler('english', randomQuestions[5],
                                randomOptions[0], 6, message, state)
            if passed.is_set():
                await e7Question(message, state)
        case EnglishTest.seventhQ:
            await answerHandler('english', randomQuestions[6],
                                randomOptions[0], 7, message, state)
            if passed.is_set():
                await e8Question(message, state)
        case EnglishTest.eighthQ:
            await answerHandler('english', randomQuestions[7],
                                randomOptions[0], 8, message, state)
            if passed.is_set():
                await e9Question(message, state)
        case EnglishTest.ninthQ:
            await answerHandler('english', randomQuestions[8],
                                randomOptions[0], 9, message, state)
            if passed.is_set():
                await e10Question(message, state)
        case EnglishTest.tenthQ:
            await answerHandler('english', randomQuestions[9],
                                randomOptions[0], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case HistoryTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                if passed.is_set():
                    await h2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[0], 1, message, state)
                await TestEnd(message, state)
        case HistoryTest.secondQ:
            await answerHandler('history', randomQuestions[1],
                                randomOptions[0], 2, message, state)
            if passed.is_set():
                await h3Question(message, state)
        case HistoryTest.thirdQ:
            await answerHandler('history', randomQuestions[2],
                                randomOptions[0], 3, message, state)
            if passed.is_set():
                await h4Question(message, state)
        case HistoryTest.fourthQ:
            await answerHandler('history', randomQuestions[3],
                                randomOptions[0], 4, message, state)
            if passed.is_set():
                await h5Question(message, state)
        case HistoryTest.fifthQ:
            await answerHandler('history', randomQuestions[4],
                                randomOptions[0], 5, message, state)
            if passed.is_set():
                await h6Question(message, state)
        case HistoryTest.sixthQ:
            await answerHandler('history', randomQuestions[5],
                                randomOptions[0], 6, message, state)
            if passed.is_set():
                await h7Question(message, state)
        case HistoryTest.seventhQ:
            await answerHandler('history', randomQuestions[6],
                                randomOptions[0], 7, message, state)
            if passed.is_set():
                await h8Question(message, state)
        case HistoryTest.eighthQ:
            await answerHandler('history', randomQuestions[7],
                                randomOptions[0], 8, message, state)
            if passed.is_set():
                await h9Question(message, state)
        case HistoryTest.ninthQ:
            await answerHandler('history', randomQuestions[8],
                                randomOptions[0], 9, message, state)
            if passed.is_set():
                await h10Question(message, state)
        case HistoryTest.tenthQ:
            await answerHandler('history', randomQuestions[9],
                                randomOptions[0], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)


@router.callback_query(F.data == 'b')
async def answerB(message: Message, state: FSMContext):
    global selectedAnswer
    selectedAnswer = 'b'
    current_state = await state.get_state()
    match current_state:
        case MathTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                if passed.is_set():
                    await m2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                await TestEnd(message, state)
        case MathTest.secondQ:
            await answerHandler('math', randomQuestions[1], randomOptions[1],
                                2, message, state)
            if passed.is_set():
                await m3Question(message, state)
        case MathTest.thirdQ:
            await answerHandler('math', randomQuestions[2], randomOptions[1],
                                3, message, state)
            if passed.is_set():
                await m4Question(message, state)
        case MathTest.fourthQ:
            await answerHandler('math', randomQuestions[3], randomOptions[1],
                                4, message, state)
            if passed.is_set():
                await m5Question(message, state)
        case MathTest.fifthQ:
            await answerHandler('math', randomQuestions[4], randomOptions[1],
                                5, message, state)
            if passed.is_set():
                await m6Question(message, state)
        case MathTest.sixthQ:
            await answerHandler('math', randomQuestions[5], randomOptions[1],
                                6, message, state)
            if passed.is_set():
                await m7Question(message, state)
        case MathTest.seventhQ:
            await answerHandler('math', randomQuestions[6], randomOptions[1],
                                7, message, state)
            if passed.is_set():
                await m8Question(message, state)
        case MathTest.eighthQ:
            await answerHandler('math', randomQuestions[7], randomOptions[1],
                                8, message, state)
            if passed.is_set():
                await m9Question(message, state)
        case MathTest.ninthQ:
            await answerHandler('math', randomQuestions[8], randomOptions[1],
                                9, message, state)
            if passed.is_set():
                await m10Question(message, state)
        case MathTest.tenthQ:
            await answerHandler('math', randomQuestions[9], randomOptions[1],
                                10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case PhysicsTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                if passed.is_set():
                    await p2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                await TestEnd(message, state)
        case PhysicsTest.secondQ:
            await answerHandler('physics', randomQuestions[1],
                                randomOptions[1], 2, message, state)
            if passed.is_set():
                await p3Question(message, state)
        case PhysicsTest.thirdQ:
            await answerHandler('physics', randomQuestions[2],
                                randomOptions[1], 3, message, state)
            if passed.is_set():
                await p4Question(message, state)
        case PhysicsTest.fourthQ:
            await answerHandler('physics', randomQuestions[3],
                                randomOptions[1], 4, message, state)
            if passed.is_set():
                await p5Question(message, state)
        case PhysicsTest.fifthQ:
            await answerHandler('physics', randomQuestions[4],
                                randomOptions[1], 5, message, state)
            if passed.is_set():
                await p6Question(message, state)
        case PhysicsTest.sixthQ:
            await answerHandler('physics', randomQuestions[5],
                                randomOptions[1], 6, message, state)
            if passed.is_set():
                await p7Question(message, state)
        case PhysicsTest.seventhQ:
            await answerHandler('physics', randomQuestions[6],
                                randomOptions[1], 7, message, state)
            if passed.is_set():
                await p8Question(message, state)
        case PhysicsTest.eighthQ:
            await answerHandler('physics', randomQuestions[7],
                                randomOptions[1], 8, message, state)
            if passed.is_set():
                await p9Question(message, state)
        case PhysicsTest.ninthQ:
            await answerHandler('physics', randomQuestions[8],
                                randomOptions[1], 9, message, state)
            if passed.is_set():
                await p10Question(message, state)
        case PhysicsTest.tenthQ:
            await answerHandler('physics', randomQuestions[9],
                                randomOptions[1], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case EnglishTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                if passed.is_set():
                    await e2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                await TestEnd(message, state)
        case EnglishTest.secondQ:
            await answerHandler('english', randomQuestions[1],
                                randomOptions[1], 2, message, state)
            if passed.is_set():
                await e3Question(message, state)
        case EnglishTest.thirdQ:
            await answerHandler('english', randomQuestions[2],
                                randomOptions[1], 3, message, state)
            if passed.is_set():
                await e4Question(message, state)
        case EnglishTest.fourthQ:
            await answerHandler('english', randomQuestions[3],
                                randomOptions[1], 4, message, state)
            if passed.is_set():
                await e5Question(message, state)
        case EnglishTest.fifthQ:
            await answerHandler('english', randomQuestions[4],
                                randomOptions[1], 5, message, state)
            if passed.is_set():
                await e6Question(message, state)
        case EnglishTest.sixthQ:
            await answerHandler('english', randomQuestions[5],
                                randomOptions[1], 6, message, state)
            if passed.is_set():
                await e7Question(message, state)
        case EnglishTest.seventhQ:
            await answerHandler('english', randomQuestions[6],
                                randomOptions[1], 7, message, state)
            if passed.is_set():
                await e8Question(message, state)
        case EnglishTest.eighthQ:
            await answerHandler('english', randomQuestions[7],
                                randomOptions[1], 8, message, state)
            if passed.is_set():
                await e9Question(message, state)
        case EnglishTest.ninthQ:
            await answerHandler('english', randomQuestions[8],
                                randomOptions[1], 9, message, state)
            if passed.is_set():
                await e10Question(message, state)
        case EnglishTest.tenthQ:
            await answerHandler('english', randomQuestions[9],
                                randomOptions[1], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case HistoryTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                if passed.is_set():
                    await h2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[1], 1, message, state)
                await TestEnd(message, state)
        case HistoryTest.secondQ:
            await answerHandler('history', randomQuestions[1],
                                randomOptions[1], 2, message, state)
            if passed.is_set():
                await h3Question(message, state)
        case HistoryTest.thirdQ:
            await answerHandler('history', randomQuestions[2],
                                randomOptions[1], 3, message, state)
            if passed.is_set():
                await h4Question(message, state)
        case HistoryTest.fourthQ:
            await answerHandler('history', randomQuestions[3],
                                randomOptions[1], 4, message, state)
            if passed.is_set():
                await h5Question(message, state)
        case HistoryTest.fifthQ:
            await answerHandler('history', randomQuestions[4],
                                randomOptions[1], 5, message, state)
            if passed.is_set():
                await h6Question(message, state)
        case HistoryTest.sixthQ:
            await answerHandler('history', randomQuestions[5],
                                randomOptions[1], 6, message, state)
            if passed.is_set():
                await h7Question(message, state)
        case HistoryTest.seventhQ:
            await answerHandler('history', randomQuestions[6],
                                randomOptions[1], 7, message, state)
            if passed.is_set():
                await h8Question(message, state)
        case HistoryTest.eighthQ:
            await answerHandler('history', randomQuestions[7],
                                randomOptions[1], 8, message, state)
            if passed.is_set():
                await h9Question(message, state)
        case HistoryTest.ninthQ:
            await answerHandler('history', randomQuestions[8],
                                randomOptions[1], 9, message, state)
            if passed.is_set():
                await h10Question(message, state)
        case HistoryTest.tenthQ:
            await answerHandler('history', randomQuestions[9],
                                randomOptions[1], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)


@router.callback_query(F.data == 'c')
async def answerC(message: Message, state: FSMContext):
    global selectedAnswer
    selectedAnswer = 'c'
    current_state = await state.get_state()
    match current_state:
        case MathTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                if passed.is_set():
                    await m2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                await TestEnd(message, state)
        case MathTest.secondQ:
            await answerHandler('math', randomQuestions[1], randomOptions[2],
                                2, message, state)
            if passed.is_set():
                await m3Question(message, state)
        case MathTest.thirdQ:
            await answerHandler('math', randomQuestions[2], randomOptions[2],
                                3, message, state)
            if passed.is_set():
                await m4Question(message, state)
        case MathTest.fourthQ:
            await answerHandler('math', randomQuestions[3], randomOptions[2],
                                4, message, state)
            if passed.is_set():
                await m5Question(message, state)
        case MathTest.fifthQ:
            await answerHandler('math', randomQuestions[4], randomOptions[2],
                                5, message, state)
            if passed.is_set():
                await m6Question(message, state)
        case MathTest.sixthQ:
            await answerHandler('math', randomQuestions[5], randomOptions[2],
                                6, message, state)
            if passed.is_set():
                await m7Question(message, state)
        case MathTest.seventhQ:
            await answerHandler('math', randomQuestions[6], randomOptions[2],
                                7, message, state)
            if passed.is_set():
                await m8Question(message, state)
        case MathTest.eighthQ:
            await answerHandler('math', randomQuestions[7], randomOptions[2],
                                8, message, state)
            if passed.is_set():
                await m9Question(message, state)
        case MathTest.ninthQ:
            await answerHandler('math', randomQuestions[8], randomOptions[2],
                                9, message, state)
            if passed.is_set():
                await m10Question(message, state)
        case MathTest.tenthQ:
            await answerHandler('math', randomQuestions[9], randomOptions[2],
                                10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case PhysicsTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                if passed.is_set():
                    await p2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                await TestEnd(message, state)
        case PhysicsTest.secondQ:
            await answerHandler('physics', randomQuestions[1],
                                randomOptions[2], 2, message, state)
            if passed.is_set():
                await p3Question(message, state)
        case PhysicsTest.thirdQ:
            await answerHandler('physics', randomQuestions[2],
                                randomOptions[2], 3, message, state)
            if passed.is_set():
                await p4Question(message, state)
        case PhysicsTest.fourthQ:
            await answerHandler('physics', randomQuestions[3],
                                randomOptions[2], 4, message, state)
            if passed.is_set():
                await p5Question(message, state)
        case PhysicsTest.fifthQ:
            await answerHandler('physics', randomQuestions[4],
                                randomOptions[2], 5, message, state)
            if passed.is_set():
                await p6Question(message, state)
        case PhysicsTest.sixthQ:
            await answerHandler('physics', randomQuestions[5],
                                randomOptions[2], 6, message, state)
            if passed.is_set():
                await p7Question(message, state)
        case PhysicsTest.seventhQ:
            await answerHandler('physics', randomQuestions[6],
                                randomOptions[2], 7, message, state)
            if passed.is_set():
                await p8Question(message, state)
        case PhysicsTest.eighthQ:
            await answerHandler('physics', randomQuestions[7],
                                randomOptions[2], 8, message, state)
            if passed.is_set():
                await p9Question(message, state)
        case PhysicsTest.ninthQ:
            await answerHandler('physics', randomQuestions[8],
                                randomOptions[2], 9, message, state)
            if passed.is_set():
                await p10Question(message, state)
        case PhysicsTest.tenthQ:
            await answerHandler('physics', randomQuestions[9],
                                randomOptions[2], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case EnglishTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                if passed.is_set():
                    await e2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                await TestEnd(message, state)
        case EnglishTest.secondQ:
            await answerHandler('english', randomQuestions[1],
                                randomOptions[2], 2, message, state)
            if passed.is_set():
                await e3Question(message, state)
        case EnglishTest.thirdQ:
            await answerHandler('english', randomQuestions[2],
                                randomOptions[2], 3, message, state)
            if passed.is_set():
                await e4Question(message, state)
        case EnglishTest.fourthQ:
            await answerHandler('english', randomQuestions[3],
                                randomOptions[2], 4, message, state)
            if passed.is_set():
                await e5Question(message, state)
        case EnglishTest.fifthQ:
            await answerHandler('english', randomQuestions[4],
                                randomOptions[2], 5, message, state)
            if passed.is_set():
                await e6Question(message, state)
        case EnglishTest.sixthQ:
            await answerHandler('english', randomQuestions[5],
                                randomOptions[2], 6, message, state)
            if passed.is_set():
                await e7Question(message, state)
        case EnglishTest.seventhQ:
            await answerHandler('english', randomQuestions[6],
                                randomOptions[2], 7, message, state)
            if passed.is_set():
                await e8Question(message, state)
        case EnglishTest.eighthQ:
            await answerHandler('english', randomQuestions[7],
                                randomOptions[2], 8, message, state)
            if passed.is_set():
                await e9Question(message, state)
        case EnglishTest.ninthQ:
            await answerHandler('english', randomQuestions[8],
                                randomOptions[2], 9, message, state)
            if passed.is_set():
                await e10Question(message, state)
        case EnglishTest.tenthQ:
            await answerHandler('english', randomQuestions[9],
                                randomOptions[2], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case HistoryTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                if passed.is_set():
                    await h2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[2], 1, message, state)
                await TestEnd(message, state)
        case HistoryTest.secondQ:
            await answerHandler('history', randomQuestions[1],
                                randomOptions[2], 2, message, state)
            if passed.is_set():
                await h3Question(message, state)
        case HistoryTest.thirdQ:
            await answerHandler('history', randomQuestions[2],
                                randomOptions[2], 3, message, state)
            if passed.is_set():
                await h4Question(message, state)
        case HistoryTest.fourthQ:
            await answerHandler('history', randomQuestions[3],
                                randomOptions[2], 4, message, state)
            if passed.is_set():
                await h5Question(message, state)
        case HistoryTest.fifthQ:
            await answerHandler('history', randomQuestions[4],
                                randomOptions[2], 5, message, state)
            if passed.is_set():
                await h6Question(message, state)
        case HistoryTest.sixthQ:
            await answerHandler('history', randomQuestions[5],
                                randomOptions[2], 6, message, state)
            if passed.is_set():
                await h7Question(message, state)
        case HistoryTest.seventhQ:
            await answerHandler('history', randomQuestions[6],
                                randomOptions[2], 7, message, state)
            if passed.is_set():
                await h8Question(message, state)
        case HistoryTest.eighthQ:
            await answerHandler('history', randomQuestions[7],
                                randomOptions[2], 8, message, state)
            if passed.is_set():
                await h9Question(message, state)
        case HistoryTest.ninthQ:
            await answerHandler('history', randomQuestions[8],
                                randomOptions[2], 9, message, state)
            if passed.is_set():
                await h10Question(message, state)
        case HistoryTest.tenthQ:
            await answerHandler('history', randomQuestions[9],
                                randomOptions[2], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)


@router.callback_query(F.data == 'd')
async def answerD(message: Message, state: FSMContext):
    global selectedAnswer
    selectedAnswer = 'd'
    current_state = await state.get_state()
    match current_state:
        case MathTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                if passed.is_set():
                    await m2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('math', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                await TestEnd(message, state)
        case MathTest.secondQ:
            await answerHandler('math', randomQuestions[1], randomOptions[3],
                                2, message, state)
            if passed.is_set():
                await m3Question(message, state)
        case MathTest.thirdQ:
            await answerHandler('math', randomQuestions[2], randomOptions[3],
                                3, message, state)
            if passed.is_set():
                await m4Question(message, state)
        case MathTest.fourthQ:
            await answerHandler('math', randomQuestions[3], randomOptions[3],
                                4, message, state)
            if passed.is_set():
                await m5Question(message, state)
        case MathTest.fifthQ:
            await answerHandler('math', randomQuestions[4], randomOptions[3],
                                5, message, state)
            if passed.is_set():
                await m6Question(message, state)
        case MathTest.sixthQ:
            await answerHandler('math', randomQuestions[5], randomOptions[3],
                                6, message, state)
            if passed.is_set():
                await m7Question(message, state)
        case MathTest.seventhQ:
            await answerHandler('math', randomQuestions[6], randomOptions[3],
                                7, message, state)
            if passed.is_set():
                await m8Question(message, state)
        case MathTest.eighthQ:
            await answerHandler('math', randomQuestions[7], randomOptions[3],
                                8, message, state)
            if passed.is_set():
                await m9Question(message, state)
        case MathTest.ninthQ:
            await answerHandler('math', randomQuestions[8], randomOptions[3],
                                9, message, state)
            if passed.is_set():
                await m10Question(message, state)
        case MathTest.tenthQ:
            await answerHandler('math', randomQuestions[9], randomOptions[3],
                                10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case PhysicsTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                if passed.is_set():
                    await p2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('physics', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                await TestEnd(message, state)
        case PhysicsTest.secondQ:
            await answerHandler('physics', randomQuestions[1],
                                randomOptions[3], 2, message, state)
            if passed.is_set():
                await p3Question(message, state)
        case PhysicsTest.thirdQ:
            await answerHandler('physics', randomQuestions[2],
                                randomOptions[3], 3, message, state)
            if passed.is_set():
                await p4Question(message, state)
        case PhysicsTest.fourthQ:
            await answerHandler('physics', randomQuestions[3],
                                randomOptions[3], 4, message, state)
            if passed.is_set():
                await p5Question(message, state)
        case PhysicsTest.fifthQ:
            await answerHandler('physics', randomQuestions[4],
                                randomOptions[3], 5, message, state)
            if passed.is_set():
                await p6Question(message, state)
        case PhysicsTest.sixthQ:
            await answerHandler('physics', randomQuestions[5],
                                randomOptions[3], 6, message, state)
            if passed.is_set():
                await p7Question(message, state)
        case PhysicsTest.seventhQ:
            await answerHandler('physics', randomQuestions[6],
                                randomOptions[3], 7, message, state)
            if passed.is_set():
                await p8Question(message, state)
        case PhysicsTest.eighthQ:
            await answerHandler('physics', randomQuestions[7],
                                randomOptions[3], 8, message, state)
            if passed.is_set():
                await p9Question(message, state)
        case PhysicsTest.ninthQ:
            await answerHandler('physics', randomQuestions[8],
                                randomOptions[3], 9, message, state)
            if passed.is_set():
                await p10Question(message, state)
        case PhysicsTest.tenthQ:
            await answerHandler('physics', randomQuestions[9],
                                randomOptions[3], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case EnglishTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                if passed.is_set():
                    await e2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('english', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                await TestEnd(message, state)
        case EnglishTest.secondQ:
            await answerHandler('english', randomQuestions[1],
                                randomOptions[3], 2, message, state)
            if passed.is_set():
                await e3Question(message, state)
        case EnglishTest.thirdQ:
            await answerHandler('english', randomQuestions[2],
                                randomOptions[3], 3, message, state)
            if passed.is_set():
                await e4Question(message, state)
        case EnglishTest.fourthQ:
            await answerHandler('english', randomQuestions[3],
                                randomOptions[3], 4, message, state)
            if passed.is_set():
                await e5Question(message, state)
        case EnglishTest.fifthQ:
            await answerHandler('english', randomQuestions[4],
                                randomOptions[3], 5, message, state)
            if passed.is_set():
                await e6Question(message, state)
        case EnglishTest.sixthQ:
            await answerHandler('english', randomQuestions[5],
                                randomOptions[3], 6, message, state)
            if passed.is_set():
                await e7Question(message, state)
        case EnglishTest.seventhQ:
            await answerHandler('english', randomQuestions[6],
                                randomOptions[3], 7, message, state)
            if passed.is_set():
                await e8Question(message, state)
        case EnglishTest.eighthQ:
            await answerHandler('english', randomQuestions[7],
                                randomOptions[3], 8, message, state)
            if passed.is_set():
                await e9Question(message, state)
        case EnglishTest.ninthQ:
            await answerHandler('english', randomQuestions[8],
                                randomOptions[3], 9, message, state)
            if passed.is_set():
                await e10Question(message, state)
        case EnglishTest.tenthQ:
            await answerHandler('english', randomQuestions[9],
                                randomOptions[3], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)

        case HistoryTest.firstQ:
            if testType == 'firstTest' or testType == 'thirdTest':
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                if passed.is_set():
                    await h2Question(message, state)
            elif testType == 'secondTest' or dailyTaskActive:
                await answerHandler('history', randomQuestions[0],
                                    randomOptions[3], 1, message, state)
                await TestEnd(message, state)
        case HistoryTest.secondQ:
            await answerHandler('history', randomQuestions[1],
                                randomOptions[3], 2, message, state)
            if passed.is_set():
                await h3Question(message, state)
        case HistoryTest.thirdQ:
            await answerHandler('history', randomQuestions[2],
                                randomOptions[3], 3, message, state)
            if passed.is_set():
                await h4Question(message, state)
        case HistoryTest.fourthQ:
            await answerHandler('history', randomQuestions[3],
                                randomOptions[3], 4, message, state)
            if passed.is_set():
                await h5Question(message, state)
        case HistoryTest.fifthQ:
            await answerHandler('history', randomQuestions[4],
                                randomOptions[3], 5, message, state)
            if passed.is_set():
                await h6Question(message, state)
        case HistoryTest.sixthQ:
            await answerHandler('history', randomQuestions[5],
                                randomOptions[3], 6, message, state)
            if passed.is_set():
                await h7Question(message, state)
        case HistoryTest.seventhQ:
            await answerHandler('history', randomQuestions[6],
                                randomOptions[3], 7, message, state)
            if passed.is_set():
                await h8Question(message, state)
        case HistoryTest.eighthQ:
            await answerHandler('history', randomQuestions[7],
                                randomOptions[3], 8, message, state)
            if passed.is_set():
                await h9Question(message, state)
        case HistoryTest.ninthQ:
            await answerHandler('history', randomQuestions[8],
                                randomOptions[3], 9, message, state)
            if passed.is_set():
                await h10Question(message, state)
        case HistoryTest.tenthQ:
            await answerHandler('history', randomQuestions[9],
                                randomOptions[3], 10, message, state)
            if passed.is_set():
                await TestEnd(message, state)


async def answerHandler(subject, questionKey, answer, questionNumber, message,
                        state):
    global correctAnswersInTest
    global wrongAnswersInTest
    global question
    global answerList
    global randomOptions
    global lives
    global passed
    global correct_option_key
    question = dict
    match subject:
        case 'math':
            match difficulty:
                case 'easy':
                    question = next(q for q in mathEasyQuestions
                                    if q['id'] == questionKey)
                case 'normal':
                    question = next(q for q in mathMediumQuestions
                                    if q['id'] == questionKey)
                case 'hard':
                    question = next(q for q in mathHardQuestions
                                    if q['id'] == questionKey)
            correct_option_key = question['correct_option_key']
        case 'physics':
            match difficulty:
                case 'easy':
                    question = next(q for q in physicsEasyQuestions
                                    if q['id'] == questionKey)
                case 'normal':
                    question = next(q for q in physicsMediumQuestions
                                    if q['id'] == questionKey)
                case 'hard':
                    question = next(q for q in physicsHardQuestions
                                    if q['id'] == questionKey)
            correct_option_key = question['correct_option_key']
        case 'english':
            match difficulty:
                case 'easy':
                    question = next(q for q in englishEasyQuestions
                                    if q['id'] == questionKey)
                case 'normal':
                    question = next(q for q in englishMediumQuestions
                                    if q['id'] == questionKey)
                case 'hard':
                    question = next(q for q in englishHardQuestions
                                    if q['id'] == questionKey)
            correct_option_key = question['correct_option_key']
        case 'history':
            match difficulty:
                case 'easy':
                    question = next(q for q in historyEasyQuestions
                                    if q['id'] == questionKey)
                case 'normal':
                    question = next(q for q in historyMediumQuestions
                                    if q['id'] == questionKey)
                case 'hard':
                    question = next(q for q in historyHardQuestions
                                    if q['id'] == questionKey)
            correct_option_key = question['correct_option_key']
    if answer == correct_option_key:
        setattr(CorrectlyAnsweredTenQuestions,
                f"is{str(questionNumber)}QuestionAnsweredCorrectly", True)
        getattr(CorrectlyAnsweredTenQuestions,
                f"is{str(questionNumber)}QuestionAnsweredCorrectly")
        correctAnswersInTest += 1
        passed.set()
    else:
        setattr(CorrectlyAnsweredTenQuestions,
                f"is{str(questionNumber)}QuestionAnsweredCorrectly", False)
        getattr(CorrectlyAnsweredTenQuestions,
                f"is{str(questionNumber)}QuestionAnsweredCorrectly")
        wrongAnswersInTest += 1
        if testType == 'thirdTest':
            lives -= 1
            passed.set()
        if lives <= 0:
            passed.clear()
            await TestEnd(message, state)
            return
        passed.set()
    answerList.append(question['options'][answer])
