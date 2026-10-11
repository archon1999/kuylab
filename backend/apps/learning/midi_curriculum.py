"""Composition lessons use literal events from the learner's exact MIDI file."""
from collections import defaultdict
import hashlib
import json
from urllib.parse import urlencode
from .curriculum import question
from apps.scores.midi import quarters_at_seconds


def note_name(midi):
    names = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
    return names[midi % 12] + str(midi // 12 - 1)


def fragments(score):
    parsed = score.parsed
    events = [event for event in parsed["events"] if not event.get("percussion") and event.get("pitch")]
    duration = parsed["metadata"]["duration_seconds"]
    if not events:
        return {"events": [], "duration": duration}
    sections = score.sections or []
    opening = sections[0] if sections else None
    windows = parsed["measures"]
    first_start = windows[opening["start_index"]]["start_seconds"] if opening else events[0]["onset_seconds"]
    first_end = windows[opening["end_index"]]["end_seconds"] if opening else min(duration, first_start + 4)
    opening_events = [event for event in events if first_start - 1e-9 <= event["onset_seconds"] < first_end - 1e-9]
    by_time = defaultdict(list)
    for event in events:
        by_time[(event["part_id"], event.get("port", 0), event["channel"], event["start_ticks"])].append(event)
    triad = None
    for group in by_time.values():
        pitches = sorted({event["pitch"]["midi"] % 12 for event in group})
        if len(pitches) != 3:
            continue
        for root in pitches:
            structure = {(pitch - root) % 12 for pitch in pitches}
            if structure in [{0, 3, 7}, {0, 4, 7}]:
                triad = {"events": group, "root": root, "mode": "minor" if structure == {0, 3, 7} else "major"}
                break
        if triad:
            break
    hand = lambda event: score.hand_overrides.get(event["id"], event.get("hand", "unknown"))
    left = next((event for event in events if hand(event) == "left"), None)
    left_groups = [[event for event in group if hand(event) == "left"] for group in by_time.values()]
    paired = next((group for group in left_groups if len(group) >= 2), None)
    simultaneous = next((group for group in by_time.values() if len(group) >= 2), None)
    right = [event for event in events if hand(event) == "right" and not event.get("chord")]
    melodic = next(((a, b) for a, b in zip(right, right[1:]) if a["pitch"]["midi"] != b["pitch"]["midi"]), None)
    if melodic is None:
        melodic = next(((a, b) for a, b in zip(events, events[1:]) if a["onset_seconds"] != b["onset_seconds"]), None)
    return {"events": events, "duration": duration, "opening": (first_start, first_end), "left": left,
            "paired": paired, "melodic": melodic, "triad": triad, "hand": hand,
            "opening_events": opening_events, "simultaneous": simultaneous}


def midi_definitions(arrangement, score):
    facts = fragments(score)
    events, duration = facts["events"], facts["duration"]
    if not events:
        return []
    group = facts["paired"] or ([facts["left"]] if facts["left"] else events[:1])
    register_start = group[0]["onset_seconds"]
    left_start = facts["left"]["onset_seconds"] if facts["left"] else events[0]["onset_seconds"]
    melodic_start = facts["melodic"][0]["onset_seconds"] if facts["melodic"] else events[0]["onset_seconds"]
    chord_group = facts["triad"]["events"] if facts["triad"] else facts["simultaneous"]
    triad_start = chord_group[0]["onset_seconds"] if chord_group else melodic_start
    span = max(event["pitch"]["midi"] for event in group) - min(event["pitch"]["midi"] for event in group)
    a, b = facts["melodic"] if facts["melodic"] else (events[0], events[0])
    interval = abs(b["pitch"]["midi"] - a["pitch"]["midi"])
    names = "–".join(note_name(event["pitch"]["midi"]) for event in chord_group or [])
    mode = facts["triad"]["mode"] if facts["triad"] else "interval"
    first_event = facts["opening_events"][0] if facts["opening_events"] else events[0]
    first_note = note_name(first_event["pitch"]["midi"])
    meter = score.parsed["measures"][first_event["measure_index"]].get("time")
    meter_label = f"{meter['beats']}/{meter['beat_type']}" if meter else "kiritilmagan"
    first_part = first_event["part_id"]
    opening_attacks = sorted({event["onset_quarters"] for event in facts["opening_events"] if event["part_id"] == first_part})[:5]
    opening_gaps = [round(b - a, 9) for a, b in zip(opening_attacks, opening_attacks[1:])]
    compound_long_short = bool(meter and meter["beats"] == "6" and meter["beat_type"] == 8
                               and len(opening_attacks) == 5 and abs(opening_attacks[0]) < 1e-9
                               and opening_gaps == [1, 0.5, 1, 0.5] and facts["opening"][0] == 0)
    first_key_duration = round(first_event["duration_quarters"], 6)
    completeness_verified = bool(getattr(score, "completeness_verified_at", None))
    last_release = max(event["onset_seconds"] + event["duration_seconds"] for event in events)
    ending_start = min(max(0, last_release - 4.5), events[-1]["onset_seconds"])
    template = [
        ("midi-pulse", "Boshlanish: haqiqiy ritm", "rhythm", facts["opening"],
         "Tanlangan MIDI boshlanishidagi nota hujumlari orasidagi vaqtni tinglang va sanang.",
         [{"title": "Nota va vaqt", "text": f"Birinchi tovush {first_note}. Faylning yozilgan time-signature metama'lumoti {meter_label}; tempo chorak birligida berilgan. Nota bosib turish davomiyligi keyingi nota boshlanish oralig'idan farq qilishi mumkin."},
          {"title": "Kichik guruh", "text": "Playerdagi aynan shu manba bo'lagini sekin tinglang. Avval bir xil tovushlarning hujumini qarsak bilan takrorlang, keyin pianinoda chalib ko'ring. Yangi ritm to'qilmaydi."}],
         [question("midi-first-note", "Shu parchaning birinchi tovushi qaysi?", [first_note, note_name((first_event["pitch"]["midi"] + 2) % 128), note_name((first_event["pitch"]["midi"] + 5) % 128)], 0, "Javob tanlangan parchadagi birinchi note_on hodisasidan olingan.")]),
        ("midi-register", "Chap qo'l kirishi: klavish masofasi" if facts["left"] else "Klavish masofasi: qo'lni belgilang", "reading", (register_start, min(duration, register_start + 3.6)),
         "Chap qo'lning aynan manbadagi birga boshlanadigan tovushlarini toping." if facts["left"] else "Bu faylda chap qo'l ko'rsatkichi yo'q. Haqiqiy klavishlarni toping va playerda qo'lni belgilang.",
         [{"title": "Manbadagi masofa", "text": f"Tanlangan chap qo'l guruhining pastki va yuqori tovushi orasida {span} yarim ton. " + ("12 yarim ton — oktava: nota nomi bir xil, registr boshqa." if span == 12 else "Masofa shu manba hodisalaridan hisoblandi; oktava deb taxmin qilinmaydi.")},
          {"title": "Qulay harakat", "text": "Guruh tovushlarini avval alohida toping, keyin manbadagi vaqtda birga chaling. Qo'lni majburan cho'zmang; qulayroq ko'chirishni sinang."}],
         [question("midi-span", "Tanlangan chap qo'l guruhining masofasi nechta yarim ton?", [str(span + 1), str(span), str(span + 2)], 1, f"Manbadagi MIDI raqamlari farqi {span}; registr klavish balandligini bildiradi.")]),
        ("midi-interval", "Ohang: ikki tovush orasidagi yo'l", "intervals", (melodic_start, min(duration, max(melodic_start + 3, b["onset_seconds"] + b["duration_seconds"]))),
         "Tanish ohangdagi haqiqiy o'zgarishni interval sifatida tushuning.",
         [{"title": "Aynan juftlik", "text": f"{note_name(a['pitch']['midi'])} → {note_name(b['pitch']['midi'])}: {interval} yarim ton. Harakat yo'nalishi va masofani oldindan ayting. MIDI harf yozuvini saqlamaydi; ko'rsatilgan nomlar klavish uchun standart displey nomlari."},
          {"title": "Asarga qaytish", "text": "Ikki tovushni manbadagi hujum vaqtida takrorlang, keyin oldi va keyingi tovushga ulang. Alohida yodlangan shakldan aynan kompozitsiya o'tishiga qayting."}],
         [question("midi-interval", "Ko'rsatilgan manba juftligi orasida nechta yarim ton?", [str(interval), str(interval + 1), str(interval + 2)], 0, f"Ikki MIDI klavish raqami orasidagi mutlaq farq {interval}.")]),
        ("midi-chord", "Kompozitsiyadagi akkord shakli", "harmony", (triad_start, min(duration, triad_start + 3.6)),
         "Birga boshlanadigan haqiqiy tovushlarni nomlang va eshiting.",
         [{"title": "Aynan tovushlar", "text": f"Tanlangan manba guruhida {names}. " + (f"Pitch-class tuzilishi {mode} uch tovushli akkordiga mos. Kichik tersiya 3, katta tersiya 4 yarim ton; sof kvinta 7." if facts["triad"] else "Bu juftlik interval; uch tovushli akkord deb belgilanmaydi.")},
          {"title": "Harmoniya va metadata", "text": "Bitta akkord shakli butun asarning tonalligini isbotlamaydi. MIDI key metadata qiymati o'zgartirilmaydi; nazariy savol shu haqiqiy tovush guruhiga tegishli."}],
         [question("midi-chord", "Tanlangan haqiqiy tovush guruhi qaysi tuzilishga mos?", [mode, "minor" if mode != "minor" else "major", "faqat bitta tovush"], 0, "Tuzilish tanlangan birga boshlanuvchi MIDI tovushlari orasidagi masofadan tekshirildi.")]),
        ("midi-coordination", "Ikki qo'lni aynan bo'lakda ulang" if facts["left"] else "Qo'l xaritasini tekshiring", "coordination", (left_start, min(duration, left_start + 7.2)),
         "Qo'llar kirishi va birga boshlanishini haqiqiy vaqt xaritasida ko'ring.",
         [{"title": "Qo'l dalili", "text": "Right Hand / Left Hand nomlari manba treklaridan yoki siz belgilagan qo'l xaritasidan olinadi. Barmoqlash MIDI orqali aniqlanmaydi."},
          {"title": "Uchrashuv", "text": "Avval shu fragmentning bir qo'lini tinglab/chaling, keyin ikkinchisini qo'shing. Bir vaqtda boshlanadigan manba tovushlariga qarang; har ikkala qo'lni butun asar bo'ylab alohida yodlash shart emas."}],
         [question("midi-fingering", "MIDI trek nomi nimani beradi?", ["Har bir barmoq raqamini", "Qo'l partiyasi uchun manba ko'rsatkichi, keyin tekshirish mumkin", "Ijro mukammalligi bahosini"], 1, "Trek nomi qo'lga oid manba ko'rsatkichi; barmoqlash va ijro sifati alohida.")]),
        ("midi-recall", "Yakun va keyingi kundagi sinov", "practice", (ending_start, duration),
         "MIDI fayli yakunidan qayta boshlash va saqlanishni tekshiring.",
         [{"title": "Haqiqiy yakun", "text": f"Bu faylning to'liq vaqt chegarasi {duration:.3f} soniya. Tanlangan fragment oxirgi manba nota qo'yib yuborilishigacha boradi; pedal cho'zilishi alohida yuritiladi."},
          {"title": "Qayta chaqirish", "text": "Yakuniy bo'lakni qulay tempda uch marta chaling. Keyingi kuni avval yordamni o'chirib birinchi urinishni sinang. Sessiyadagi qulay ijro bilan keyingi saqlanish alohida dalil."}],
         [question("midi-recall", "Keyingi kuni saqlanishni qanday tekshirasiz?", ["Darhol eng tez tempga o'taman", "Avval shu bo'lakni yordam kamaytirilgan holda bir marta sinayman", "Faqat qancha daqiqa ishlaganimni ko'raman"], 1, "Birinchi mustaqil urinish aynan shu bo'lakning qayta chaqirilishini tekshiradi.")]),
    ]
    definitions = []
    for code, title, skill, (start, end), summary, explanation, quizzes in template:
        unavailable = {"midi-pulse": not facts["opening_events"], "midi-interval": not facts["melodic"], "midi-chord": not chord_group}
        if unavailable.get(code, False):
            continue
        if not facts["left"] and code == "midi-register":
            quizzes = [{**item, "prompt": "Tanlangan manba guruhining masofasi nechta yarim ton?"} for item in quizzes]
            explanation[0] = {**explanation[0], "text": explanation[0]["text"].replace("chap qo'l guruhining", "manba guruhining")}
        if not facts["left"] and code == "midi-coordination":
            explanation = [{"title": "Qo'l dalili", "text": "Manbada chap qo'lni ko'rsatadigan trek nomi topilmadi. Balandlikdan qo'l taxmin qilinmaydi; playerda tovushlarga qo'lni o'zingiz belgilang, keyin shu bo'lakni mashq qiling."}, explanation[1]]
        if code == "midi-pulse":
            if compound_long_short:
                explanation.append({"title": "Manbadagi 3 + 3", "text": f"Birinchi trek hujumlari chorak birliklarida 0, 1, 1.5, 2.5, 3 da boshlanadi. Oraliqlar 1, 0.5, 1, 0.5 chorak: sakkizlikda (2 + 1) / (2 + 1). Olti bo'linmada hujumlar 1, 3, 4, 6 ga tushadi; katta pulslar 1 va 4. BIR—uch / IKKI—uch deb sanang. Birinchi klavish {first_key_duration:g} chorak bosib turiladi, keyingi hujum esa 1 chorakdan so'ng: ushlash va ritmik oraliq boshqa qiymatlar."})
                quizzes = [*quizzes, question("midi-pulse-group", "Aynan boshlanishdagi hujum oraliqlari sakkizliklarda qanday guruhlanadi?", ["(2 + 1) / (2 + 1)", "(1 + 1 + 1) / (1 + 1 + 1)", "2 + 2 + 2"], 0, "Manbadagi 1, 0.5, 1, 0.5 chorak oraliqlari 2, 1, 2, 1 sakkizlikka teng. Ikki katta pulsning har biri 3 sakkizlik.")]
            else:
                explanation.append({"title": "Haqiqiy hujum oraliqlari", "text": f"Birinchi trekning dastlabki hujumlari chorak birliklarida: {', '.join(f'{value:g}' for value in opening_attacks)}. Ketma-ket oraliqlar: {', '.join(f'{value:g}' for value in opening_gaps) or 'juftlik yo‘q'}. 3 + 3 guruhi bu faylga taxmin bilan biriktirilmaydi."})
        selected = [event for event in events if start - 1e-9 <= event["onset_seconds"] < end - 1e-9]
        if not selected:
            continue
        start_index, end_index = selected[0]["measure_index"], selected[-1]["measure_index"]
        start_q = quarters_at_seconds(score.parsed, start)
        end_q = quarters_at_seconds(score.parsed, end)
        binding = {"score_id": score.id, "version": score.version, "title": score.title, "source_format": "midi", "sha256": score.content_sha256,
                   "start_seconds": start, "end_seconds": end, "event_ids": [event["id"] for event in selected], "start_index": start_index, "end_index": end_index}
        if code == "midi-pulse" and compound_long_short:
            binding["source_rhythm_pattern"] = "6/8:(2+1)/(2+1)"
        if code == "midi-pulse" and first_event["id"] != events[0]["id"]:
            binding["opening_first_event_id"] = first_event["id"]
        if score.hand_overrides:
            binding["hand_assignment"] = {event["id"]: facts["hand"](event) for event in selected}
            binding["quiz_facts"] = [{"id": item["id"], "choices": item["choices"], "correct_choice": item["correct_choice"]} for item in quizzes]
        fingerprint = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()[:8]
        link = "/?" + urlencode({"page": "practice", "composition": arrangement.composition_id, "score": score.id,
                                  "start_index": start_index, "end_index": end_index, "start_seconds": start, "end_seconds": end, "bpm": 100, "beat_unit": "quarter"})
        definitions.append({"code": f"midi-{score.id}-{fingerprint}-{code}", "title": title, "skill": skill, "minutes": 7, "summary": summary,
                            "context": f"{score.title} · aynan {start:.3f}–{end:.3f} s. " + ("Tekshirilgan to'liq manba" if completeness_verified else "Yuklangan fayl") + f" {duration:.3f} s; dars bo'lagi shu fayldan ajratilgan.",
                            "kind": "source_excerpt", "score_version_id": score.id, "success_criterion": "Aynan shu manba bo'lagini qulay tempda uch marta ravon chaldim; keyingi tekshiruv maqsadini yozdim.",
                            "content": {"midi_topic": code, "explanation": explanation, "steps": [{"title": "Aynan bo'lakni tinglang", "instruction": f"{start:.3f}–{end:.3f} s manba fragmentini sekin tinglang; ko'rsatilgan haqiqiy tovushlarni toping."},
                                                              {"title": "Ajrating va ulang", "instruction": "Darsdagi bitta fikrni shu bo'lakda tekshiring; zarur bo'lsa bir qo'lni tanlang, keyin ikkala qo'lni birlashtiring."},
                                                              {"title": "Mustaqil sinov", "instruction": "Yordamni kamaytirib uchta qulay urinishni tekshiring; puls, tovushlar va qulaylik haqida aniq qayd yozing."}],
                                        "exercise": {"type": "midi_source_fragment", "original": False, "label": "Aynan kompozitsiya MIDI bo'lagi", "score_id": score.id,
                                                     "score_url": f"/api/scores/{score.id}/", "fragment_url": "", "start_seconds": start, "end_seconds": end,
                                                     "start_quarters": start_q, "end_quarters": end_q, "event_ids": binding["event_ids"], "bpm": 100, "beat_unit": "quarter"},
                                        "score_binding": binding, "practice_link": link, "transfer": "Aynan shu kompozitsiya o'tishini oldi va keyini bilan ulang; to'liq player darsdan alohida ochiladi.",
                                        "midi_facts": {"first_note": first_note, "span_semitones": span, "interval_semitones": interval,
                                                       "interval_from": note_name(a["pitch"]["midi"]), "interval_to": note_name(b["pitch"]["midi"]),
                                                       "chord_notes": names, "chord_mode": mode, "duration_seconds": duration,
                                                       "opening_attacks_quarters": opening_attacks, "opening_gaps_quarters": opening_gaps,
                                                       "compound_long_short": compound_long_short, "first_key_duration_quarters": first_key_duration, "meter_label": meter_label,
                                                       "left_available": bool(facts["left"]), "source_completeness_verified": completeness_verified},
                                        "sources": [{"title": "MIDI manbasi", "url": score.source_url}] if score.source_url else []}, "quiz": {"questions": quizzes}})
    return definitions
