import io
from pathlib import Path
import tempfile
import warnings
from unittest.mock import patch
import zipfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from tests.support import LearnerTestCase as APITestCase
from apps.learning.models import Arrangement, Composition
from apps.scores.models import Score
from apps.scores.parser import ScoreImportError, extract_musicxml, parse_musicxml

DEMO = (Path(__file__).resolve().parents[2] / "apps/scores/demo.musicxml").read_bytes()


def xml(measures, attributes="<divisions>2</divisions><time><beats>4</beats><beat-type>4</beat-type></time>"):
    return (f'<score-partwise version="4.0"><part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list>'
            f'<part id="P1"><measure number="1"><attributes>{attributes}</attributes>{measures}</measure></part></score-partwise>').encode()


def note(step="C", octave=4, duration=2, extra=""):
    return f"<note>{extra}<pitch><step>{step}</step><octave>{octave}</octave></pitch><duration>{duration}</duration><type>quarter</type></note>"


def mxl(content, target="score.musicxml"):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("META-INF/container.xml", f'<container><rootfiles><rootfile full-path="{target}" media-type="application/vnd.recordare.musicxml+xml"/></rootfiles></container>')
        archive.writestr(target, content)
    return stream.getvalue()


class MusicXmlParserTests(SimpleTestCase):
    def test_standard_musicxml_doctype_accepted_without_network_or_entity_expansion(self):
        declaration = b'<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">'
        source = DEMO.replace(b"?>", b"?>\n" + declaration, 1)
        with patch("socket.create_connection", side_effect=AssertionError("Network must not be used")) as connection, patch(
                "urllib.request.urlopen", side_effect=AssertionError("DTD must not be fetched")) as urlopen:
            parsed = parse_musicxml(source)
        connection.assert_not_called()
        urlopen.assert_not_called()
        self.assertEqual(parsed["metadata"]["event_count"], 16)
        self.assertEqual(parsed["playback_order"], [0, 1, 0, 1])
        # Standard DOCTYPE is harmless in UTF-16 as well; internal subsets aren't.
        utf16 = source.decode("utf-8").replace('encoding="UTF-8"', 'encoding="UTF-16"').encode("utf-16")
        self.assertEqual(parse_musicxml(utf16)["metadata"]["event_count"], 16)
        for altered in [source.replace(declaration, declaration[:-1] + b" []>"),
                        source.replace(b"http://www.musicxml.org/dtds/partwise.dtd", b"http://localhost/internal-secret"),
                        source.replace(b"KuyLab</creator>", b"&undefined;</creator>")]:
            with self.subTest(altered=altered[:100]), self.assertRaises(ScoreImportError):
                parse_musicxml(altered)

    def test_two_staff_demo_preserves_source_rhythm_chords_ties_meter_and_repeat(self):
        parsed = parse_musicxml(DEMO)
        self.assertEqual(parsed["metadata"]["time"]["beats"], "6")
        self.assertEqual(parsed["metadata"]["time"]["beat_type"], 8)
        self.assertEqual(parsed["metadata"]["tempo"]["quarter_bpm"], 90)
        self.assertEqual(parsed["metadata"]["tempo"]["beat_unit_dots"], 1)
        self.assertEqual(parsed["metadata"]["tempo"]["bpm"], 60)
        self.assertEqual(parsed["playback_order"], [0, 1, 0, 1])
        self.assertEqual(parsed["measures"][1]["start_quarters"], 3)
        left = [e for e in parsed["events"] if e["measure_index"] == 0 and e["staff"] == 2]
        self.assertEqual([e["offset_quarters"] for e in left], [0, 0, 1.5, 1.5])
        self.assertEqual([e["pitch"]["midi"] for e in left], [50, 57, 45, 52])
        self.assertTrue(all(e["hand"] == "left" for e in left))
        self.assertEqual(parsed["events"][10]["ties"], ["start"])
        self.assertEqual(parsed["events"][11]["ties"], ["stop"])
        self.assertFalse(parsed["capabilities"]["automatic_fingering"])

    def test_rests_forward_and_fractional_duration_do_not_shift_chords(self):
        source = xml(note(duration=1) + note("E", duration=1, extra="<chord/>")
                     + '<forward><duration>1</duration></forward><note><rest/><duration>2</duration><type>quarter</type></note>'
                     + note("G", duration=2), "<divisions>3</divisions><time><beats>2</beats><beat-type>4</beat-type></time>")
        events = parse_musicxml(source)["events"]
        self.assertEqual(events[0]["duration_fraction"], "1/3")
        self.assertEqual(events[1]["offset_quarters"], 0)
        self.assertAlmostEqual(events[2]["offset_quarters"], 2 / 3)
        self.assertTrue(events[2]["rest"])
        self.assertIsNone(events[2]["pitch"])
        self.assertAlmostEqual(events[3]["offset_quarters"], 4 / 3)
        self.assertTrue(all(e["hand"] == "unknown" for e in events))

    def test_mxl_rootfile_container_and_xml_namespace(self):
        namespaced = DEMO.replace(b'<score-partwise version="4.0">', b'<score-partwise xmlns="http://www.musicxml.org/ns/musicxml" version="4.0">')
        extracted = extract_musicxml(mxl(namespaced, "notation/main.musicxml"), "my.mxl")
        self.assertEqual(extracted, namespaced)
        self.assertEqual(parse_musicxml(extracted)["metadata"]["event_count"], 16)

    def test_first_second_endings_follow_repeat_pass(self):
        source = ('<score-partwise><part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list><part id="P1">'
                  '<measure number="1"><attributes><divisions>1</divisions></attributes><barline location="left"><repeat direction="forward"/></barline>' + note(duration=1) + '</measure>'
                  '<measure number="2"><barline location="left"><ending number="1" type="start"/></barline>' + note("D", duration=1) + '<barline location="right"><ending number="1" type="stop"/><repeat direction="backward"/></barline></measure>'
                  '<measure number="3"><barline location="left"><ending number="2" type="start"/></barline>' + note("E", duration=1) + '<barline location="right"><ending number="2" type="stop"/></barline></measure></part></score-partwise>').encode()
        self.assertEqual(parse_musicxml(source)["playback_order"], [0, 1, 0, 2])

    def test_pickup_meter_change_and_tempo_preserved(self):
        source = DEMO.replace(b'<measure number="1">', b'<measure number="0" implicit="yes">').replace(
            b'<measure number="2">', b'<measure number="2"><attributes><time><beats>3</beats><beat-type>4</beat-type></time><key><fifths>0</fifths><mode>major</mode></key></attributes><sound tempo="120"/>')
        parsed = parse_musicxml(source)
        self.assertEqual(parsed["measures"][0]["number"], "0")
        self.assertEqual(parsed["measures"][1]["time"]["beats"], "3")
        self.assertEqual(parsed["measures"][1]["key"], {"fifths": 0, "mode": "major"})
        self.assertEqual(parsed["measures"][1]["tempos"][0]["quarter_bpm"], 120)
        pickup = xml(note(duration=2)).replace(b'<measure number="1">', b'<measure number="0" implicit="yes">').replace(
            b"</measure>", ("</measure><measure number=\"1\">" + note(duration=8) + "</measure>").encode(), 1)
        pickup_parsed = parse_musicxml(pickup)
        self.assertEqual(pickup_parsed["measures"][0]["length_quarters"], 1)
        self.assertEqual(pickup_parsed["measures"][1]["start_quarters"], 1)

    def test_invalid_or_unsafe_xml_rejected_including_utf16_entities(self):
        entity = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE score-partwise [<!ENTITY secret SYSTEM "file:///secret">]><score-partwise>&secret;</score-partwise>'.encode("utf-16")
        examples = [DEMO[:-80], b"not xml", entity, b'<!DOCTYPE score-partwise SYSTEM "https://example.org/a.dtd">' + DEMO.split(b"?>", 1)[1],
                    b'<?xml-stylesheet type="text/xsl" href="https://example.org/x"?>' + DEMO,
                    xml(note()).replace(b"<part-list>", b'<credit><credit-image source="https://example.org/img"/></credit><part-list>'),
                    xml(note()).replace(b"<duration>2</duration>", b"<duration>1e999999999</duration>"),
                    xml(note(extra="<chord/>")), xml('<backup><duration>2</duration></backup>' + note()),
                    DEMO.replace(b"score-partwise", b"score-timewise")]
        for source in examples:
            with self.subTest(source=source[:80]), self.assertRaises(ScoreImportError):
                parse_musicxml(source)

    def test_zip_corruption_traversal_duplicate_members_and_oversize_rejected(self):
        for content in [b"PK invalid", mxl(DEMO, "../score.musicxml")]:
            with self.subTest(content=content[:30]), self.assertRaises(ScoreImportError):
                extract_musicxml(content, "bad.mxl")
        with patch("apps.scores.parser.MAX_XML_BYTES", 512), self.assertRaises(ScoreImportError):
            extract_musicxml(mxl(DEMO), "large.mxl")
        duplicate = io.BytesIO()
        with warnings.catch_warnings(), zipfile.ZipFile(duplicate, "w") as archive:
            warnings.simplefilter("ignore", UserWarning)
            archive.writestr("score.musicxml", DEMO)
            archive.writestr("score.musicxml", DEMO)
        with self.assertRaises(ScoreImportError):
            extract_musicxml(duplicate.getvalue(), "duplicate.mxl")
        with self.assertRaises(ScoreImportError):
            extract_musicxml(DEMO, "score.pdf")
        with patch("apps.scores.parser.MAX_NOTES", 4), self.assertRaises(ScoreImportError):
            parse_musicxml(DEMO)

    def test_complex_navigation_is_flagged_not_guessed(self):
        source = DEMO.replace(b'<sound tempo="90"/>', b'<sound tempo="90" dalsegno="segno1"/>')
        parsed = parse_musicxml(source)
        self.assertFalse(parsed["capabilities"]["timed_notes"])
        self.assertTrue(any("D.C./D.S." in warning for warning in parsed["warnings"]))


# Historical authoring API behavior; the live curated studio remains read-only.
@override_settings(CURATED_STUDIO_READ_ONLY=False)
class ScoreApiTests(APITestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="kuylab-score-tests-")
        self.addCleanup(temporary.cleanup)
        settings = override_settings(MEDIA_ROOT=temporary.name)
        settings.enable()
        self.addCleanup(settings.disable)
        composition = Composition.objects.create(title="My original piece")
        self.arrangement = Arrangement.objects.create(composition=composition, title="My version")

    def upload(self, data=DEMO, name="my.musicxml", **fields):
        return self.client.post("/api/scores/", {"file": SimpleUploadedFile(name, data), "arrangement_id": self.arrangement.pk,
            "rights_confirmed": "true", **fields}, format="multipart")

    def test_import_creates_immutable_versions_and_serves_exact_xml(self):
        first = self.upload(exact_version_confirmed="true", rights_note="My original exercise")
        self.assertEqual(first.status_code, 201, first.data)
        second = self.upload()
        self.assertEqual(second.status_code, 201, second.data)
        self.assertEqual([first.data["version"], second.data["version"]], [1, 2])
        self.assertTrue(first.data["exact_version_confirmed"])
        self.assertFalse(second.data["exact_version_confirmed"])
        self.assertEqual(first.data["rights_basis"], "user_confirmed_copy")
        source = self.client.get(first.data["musicxml_url"])
        self.assertEqual(source.status_code, 200)
        self.assertEqual(source.content, DEMO)
        self.assertEqual(source["X-Content-Type-Options"], "nosniff")
        listed = self.client.get(f"/api/scores/?arrangement_id={self.arrangement.pk}").data
        self.assertEqual(len(listed), 2)
        self.assertNotIn("parsed", listed[0])
        detail = self.client.get(f'/api/scores/{first.data["id"]}/').data
        self.assertEqual(detail["parsed"]["metadata"]["event_count"], 16)

    def test_hand_and_sections_edit_persist_without_mutating_score_content(self):
        score = self.upload().data
        event_id = score["parsed"]["events"][0]["id"]
        response = self.client.patch(f'/api/scores/{score["id"]}/', {"hand_overrides": {event_id: "left"}, "sections": [
            {"id": "intro", "title": "Difficult phrase", "start_index": 0, "end_index": 1, "notes": "Slowly"}], "exact_version_confirmed": True}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["hand_overrides"][event_id], "left")
        self.assertEqual(response.data["sections"][0]["end_index"], 1)
        self.assertEqual(response.data["content_sha256"], score["content_sha256"])
        self.assertEqual(response.data["parsed"]["events"][0]["hand"], "right")
        self.assertTrue(response.data["exact_version_confirmed"])

    def test_rejects_unconfirmed_rights_invalid_file_and_false_metadata(self):
        for fields in [{"rights_confirmed": "false"}, {"arrangement_id": 99999}, {"accuracy": "100"}]:
            with self.subTest(fields=fields):
                self.assertEqual(self.upload(**fields).status_code, 400)
        self.assertEqual(self.upload(data=b"<broken>").status_code, 400)
        self.assertEqual(self.upload(name="score.pdf").status_code, 400)
        self.assertEqual(Score.objects.count(), 0)

    def test_invalid_measure_range_and_event_hand_are_rejected(self):
        item = self.upload().data
        url = f'/api/scores/{item["id"]}/'
        for fields in [{"hand_overrides": {"missing": "left"}}, {"parsed": {}}, {"sections": [
            {"id": "wrong", "title": "Bad range", "start_index": 1, "end_index": 2}]}]:
            with self.subTest(fields=fields):
                self.assertEqual(self.client.patch(url, fields, format="json").status_code, 400)
        self.assertEqual(self.client.get("/api/scores/?arrangement_id=invalid").status_code, 400)

    def test_mxl_upload_and_original_demo_do_not_claim_song_score(self):
        response = self.upload(data=mxl(DEMO), name="my.mxl")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(self.client.get(response.data["musicxml_url"]).content, DEMO)
        demo = self.client.get("/api/scores/demo/")
        self.assertEqual(demo.status_code, 200)
        self.assertTrue(demo.data["is_demo"])
        self.assertEqual(demo.data["rights_basis"], "original_cc0")
        self.assertIsNone(demo.data["arrangement_id"])
        self.assertIn("ko'chirilmagan", demo.data["rights_note"])
        self.assertEqual(self.client.get(demo.data["musicxml_url"]).content, DEMO)
