import json
from django.core.management.base import BaseCommand, CommandError
from apps.studio.midi_quality import audit_catalog


class Command(BaseCommand):
    help = "Audit every bundled performance without editing MIDI files."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="Print the complete machine-readable report.")

    def handle(self, *args, **options):
        rows = audit_catalog()
        if options["json"]:
            self.stdout.write(json.dumps(rows, ensure_ascii=False, indent=2))
        issues = [(row, issue) for row in rows for issue in row["issues"]]
        for row, issue in issues:
            self.stderr.write(f"{row['code']} / {row['variant']}: {issue}")
        if issues:
            raise CommandError(f"MIDI audit needs attention: {len(issues)} issue(s). No source files were changed.")
        if not options["json"]:
            self.stdout.write(self.style.SUCCESS(
                f"MIDI audit passed: {len(rows)} performances, {sum(row['notes'] for row in rows)} attacks. "
                "Source overlaps/duplicates are pinned and reviewed; long holds are retained. "
                "This checks technical integrity, not equivalence to an unavailable score."))
