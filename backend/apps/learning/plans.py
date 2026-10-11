from .models import Arrangement, PracticePlan, PracticeTask
from .curriculum import ensure_curriculum


def create_draft_plan(composition, profile, source_url="", arrangement_title=""):
    """Fixed onboarding scaffold; this is not score analysis or AI instruction."""
    arrangement = Arrangement.objects.create(
        composition=composition, source_url=source_url,
        title=arrangement_title or "Aniq variant hali tanlanmagan",
        source_kind="link" if source_url else "pending",
        rights_note="Manba va foydalanish huquqi tekshirilishi kerak; havola huquqni tasdiqlamaydi.",
    )
    plan = PracticePlan.objects.create(
        arrangement=arrangement, profile=profile,
        title=f"{composition.title}: boshlang'ich reja",
        summary="Bu namuna reja. Aniq aranjirovka tanlanib, qiyin joylar baholangach individual dars tuziladi.",
    )
    tasks = [
        ("listen", "Avval aynan variantni belgilang", "Tanlagan ijro yoki nota manbasini saqlang. Qaysi joyda to'xtashingizni yozib oling; takt raqamini faqat nota tasdiqlangach belgilang.", 4, "Forma va eshitish", "Bitta aniq manba va bitta qiyin fragment belgilandi."),
        ("theory", "Ritmni tushunib oling", "Tanlangan fragmentning urishlarini sanang va ritmini qarsak bilan ayting. Hali tekshirilmagan o'lchov yoki tonallikni taxmin sifatida yozing.", 6, "Puls, ritm va fraza", "Fragmentni sanab va qarsak bilan mustaqil takrorlay oldim."),
        ("technique", "Harakatni kichik bo'lakda tekshiring", "O'zingiz biladigan 1–2 soniyalik qiyin harakatni sekin, qulay tezlikda takrorlang. Barmoqlashni barqaror tuting, zo'riqish sezilganda tanaffus qiling.", 7, "Koordinatsiya va barmoqlash", "Qulay tezlikda uch marta ravon takrorladim."),
        ("piece", "Musiqaga qayting", "O'sha harakatni oldi va keyingi kichik fragment bilan ulang. Sekin tempdan boshlang; sifat saqlansagina tezlikni oshiring.", 10, "Fragmentlarni ulash", "Ulangan bo'lakni to'xtamasdan ijro qildim; holatimni o'zim baholadim."),
        ("reflect", "Keyingi dars uchun kuzatuv", "Bugungi qulay BPM, ishlagan daqiqa va eng qiyin joyni kundalikka kiriting. Natija avtomatik nota aniqligi emas, sizning kuzatuvingiz bo'ladi.", 3, "Refleksiya", "Sessiya yozuvi va keyingi aniq maqsad saqlandi."),
    ]
    PracticeTask.objects.bulk_create([
        PracticeTask(plan=plan, order=index, kind=kind, title=title, instructions=instructions,
                     minutes=minutes, concept=concept, success_criterion=criterion)
        for index, (kind, title, instructions, minutes, concept, criterion) in enumerate(tasks, 1)
    ])
    ensure_curriculum(arrangement)
    return plan
