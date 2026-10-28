"""Prepare checked-in assets from a reviewed local import plan."""
import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from apps.studio.ivory_import import build_catalog


class Command(BaseCommand):
    help = "Validate and bundle reviewed Ivory MIDI files without changing the database."

    def add_arguments(self,parser):
        parser.add_argument("--plan",required=True)
        parser.add_argument("--source-dir",required=True)
        parser.add_argument("--output-dir",default=str(Path(__file__).resolve().parents[2]/"assets"/"ivory"))

    def handle(self,*args,**options):
        try:
            plan = json.loads(Path(options["plan"]).read_text(encoding="utf-8"))
            groups = build_catalog(plan,options["source_dir"],options["output_dir"])
        except (OSError,ValueError,KeyError,TypeError) as error:
            raise CommandError(str(error)) from error
        performances = [v for group in groups for v in group["variants"]]
        self.stdout.write(self.style.SUCCESS(f"Prepared {len(groups)} compositions, {len(performances)} performances, {sum(v['trim_start_seconds']>0 for v in performances)} reviewed intro cuts; database unchanged."))
